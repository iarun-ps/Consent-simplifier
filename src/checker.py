"""Medical Information Preservation Checker.

check_preservation(original, simplified) compares a consent form with its
simplified version and reports information that was lost or invented.
"""

import re
from collections import Counter

_NUM = r"\d+(?:\.\d+)?"
_RANGE_SEP = r"\s*(?:-|–|—|to)\s*"
_PERCENT = r"\s*(?:%|percent\b|per cent\b)"

NUMBER_PATTERN = re.compile(
    rf"(?P<first>{_NUM})(?:{_RANGE_SEP}(?P<second>{_NUM}))?(?P<pct>{_PERCENT})?",
    re.IGNORECASE,
)


def _clean(number: str) -> str:
    """Write 0.50 and 0.5 the same way."""
    return f"{float(number):g}"


def _numbers_with_positions(text: str) -> list[tuple[str, int]]:
    """Return (number in normal form, position in the text) for each number."""
    found = []
    for match in NUMBER_PATTERN.finditer(text):
        value = _clean(match.group("first"))
        if match.group("second"):
            value += "-" + _clean(match.group("second"))
        if match.group("pct"):
            value += "%"
        found.append((value, match.start()))
    return found


def extract_numbers(text: str) -> list[str]:
    """Return numbers, ranges and percentages in a normal form.

    "2-5%", "2 to 5 percent" and "2–5%" all become "2-5%".
    """
    return [value for value, _position in _numbers_with_positions(text)]


# Each entry: (name, category, words that mark it in the original,
#              wording accepted as "kept" in the simplified text).
# Matching ignores case and matches from the start of a word, so "lung"
# also matches "lungs". The category will be used in the report later.
KEY_TERMS = [
    ("infection", "risk", ["infection"], ["infection"]),
    (
        "hemorrhage",
        "risk",
        ["hemorrhage", "haemorrhage"],
        [
            "hemorrhage",
            "haemorrhage",
            "heavy bleeding",
            "severe bleeding",
            "major bleeding",
        ],
    ),
    ("bile duct injury", "risk", ["bile duct"], ["bile duct"]),
    (
        "thromboembolism",
        "risk",
        ["thromboembolism"],
        ["thromboembolism", "blood clot"],
    ),
    (
        "cardiopulmonary events",
        "risk",
        ["cardiopulmonary"],
        ["cardiopulmonary", "heart and lung", "heart or lung", "lung and heart"],
    ),
    (
        "conversion to open surgery",
        "risk",
        ["conversion to open", "converted to open"],
        [
            "conversion",
            "convert",
            "switch to open",
            "switched to open",
            "change to open",
            "changed to open",
        ],
    ),
    (
        "non-surgical management",
        "alternative",
        ["non-surgical", "nonsurgical"],
        ["non-surgical", "nonsurgical", "without surgery", "not doing surgery"],
    ),
    ("dietary modification", "alternative", ["dietary"], ["diet"]),
    (
        "observation",
        "alternative",
        ["observation"],
        ["observation", "watching", "monitor"],
    ),
    (
        "open cholecystectomy",
        "alternative",
        ["open cholecystectomy"],
        ["open cholecystectomy", "open surgery", "open operation"],
    ),
    (
        "contraindication",
        "contraindication",
        ["contraindicated", "contraindication"],
        [
            "contraindicated",
            "not safe",
            "not advised",
            "not recommended",
            "should not",
            "must not",
        ],
    ),
    (
        "coagulopathy",
        "contraindication",
        ["coagulopathy"],
        ["coagulopathy", "clotting", "bleeding problem", "bleeding disorder"],
    ),
    ("biliary colic", "benefit", ["biliary colic"], ["biliary colic"]),
    (
        "gallstone complications",
        "benefit",
        ["gallstone complications"],
        ["gallstone"],
    ),
]


def _mentions(text: str, phrases: list[str]) -> bool:
    """True if any phrase appears in the text (ignores case)."""
    return any(re.search(rf"\b{re.escape(p)}", text, re.IGNORECASE) for p in phrases)


def find_missing_key_terms(original: str, simplified: str) -> list[str]:
    """Return key terms that are in the original but not kept in the simplified text."""
    missing = []
    for name, _category, in_original, in_simplified in KEY_TERMS:
        if _mentions(original, in_original) and not _mentions(
            simplified, in_simplified
        ):
            missing.append(name)
    return missing


# A new sentence starts after . ! ? and a space, at a bullet point, or after
# a blank line.
_UNIT_SPLIT = re.compile(r"(?<=[.!?])\s+|\n\s*[•\-*]\s*|\n\s*\n")


def _split_units(text: str) -> list[str]:
    """Split text into sentences and bullet points."""
    units = _UNIT_SPLIT.split(text)
    return [" ".join(unit.split()) for unit in units if unit.strip()]


def _term_positions(unit: str, use_original_wording: bool) -> list[tuple[int, str]]:
    """Return (position, term name) for every key term found in the unit."""
    found = []
    for name, _category, in_original, in_simplified in KEY_TERMS:
        phrases = in_original if use_original_wording else in_simplified
        for phrase in phrases:
            for match in re.finditer(rf"\b{re.escape(phrase)}", unit, re.IGNORECASE):
                found.append((match.start(), name))
    return found


def _link_numbers(
    text: str, use_original_wording: bool
) -> list[tuple[str, str | None]]:
    """Pair each number with the key term it belongs to.

    Rule: the nearest key term before the number in the same sentence or
    bullet point; if there is none, the first key term after it.
    None means no key term was found.
    """
    pairs = []
    for unit in _split_units(text):
        terms = sorted(_term_positions(unit, use_original_wording))
        for value, position in _numbers_with_positions(unit):
            before = [name for start, name in terms if start < position]
            after = [name for start, name in terms if start > position]
            if before:
                term = before[-1]
            elif after:
                term = after[0]
            else:
                term = None
            pairs.append((value, term))
    return pairs


def find_number_risk_mismatches(original: str, simplified: str) -> list[dict]:
    """Find numbers that moved next to a different risk than in the original."""
    expected: dict[str, set[str]] = {}
    for value, term in _link_numbers(original, use_original_wording=True):
        if term:
            expected.setdefault(value, set()).add(term)

    mismatches = []
    for value, term in _link_numbers(simplified, use_original_wording=False):
        if term and value in expected and term not in expected[value]:
            mismatches.append(
                {"number": value, "expected": sorted(expected[value]), "found": term}
            )
    return mismatches


# Frequency words and how often they mean. A higher level means more often.
FREQUENCY_WORDS = {
    "extremely rare": 1,
    "very rare": 1,
    "very rarely": 1,
    "rare": 2,
    "rarely": 2,
    "uncommon": 3,
    "infrequent": 3,
    "occasionally": 3,
    "sometimes": 3,
    "common": 4,
    "commonly": 4,
    "frequent": 4,
    "frequently": 4,
    "often": 4,
    "very common": 5,
    "very often": 5,
}

# For each key term: the wording that counts as "kept" in the simplified text.
_SIMPLIFIED_WORDING = {name: wording for name, _cat, _orig, wording in KEY_TERMS}


def _frequency_words(unit: str) -> list[tuple[int, str]]:
    """Return (position, frequency word) for each frequency word in the unit.

    Longer phrases are matched first, so "very rare" is not also counted as "rare".
    """
    found = []
    used = []  # (start, end) of text already matched by a longer phrase
    for word in sorted(FREQUENCY_WORDS, key=len, reverse=True):
        for match in re.finditer(rf"\b{re.escape(word)}\b", unit, re.IGNORECASE):
            overlaps = any(
                match.start() < end and start < match.end() for start, end in used
            )
            if not overlaps:
                used.append((match.start(), match.end()))
                found.append((match.start(), word))
    return found


def _nearest_term(terms: list[tuple[int, str]], position: int) -> str | None:
    """The nearest key term before the position, otherwise the first one after it."""
    before = [name for start, name in terms if start < position]
    after = [name for start, name in terms if start > position]
    if before:
        return before[-1]
    if after:
        return after[0]
    return None


def _frequency_by_term(text: str, use_original_wording: bool) -> dict[str, list[str]]:
    """Map each key term to the frequency words that belong to it."""
    linked: dict[str, list[str]] = {}
    for unit in _split_units(text):
        terms = sorted(_term_positions(unit, use_original_wording))
        for position, word in _frequency_words(unit):
            term = _nearest_term(terms, position)
            if term:
                linked.setdefault(term, []).append(word)
    return linked


def find_frequency_changes(original: str, simplified: str) -> list[dict]:
    """Find frequency words that were dropped or changed for the same risk."""
    expected = _frequency_by_term(original, use_original_wording=True)
    found = _frequency_by_term(simplified, use_original_wording=False)

    changes = []
    for term, original_words in expected.items():
        if not _mentions(simplified, _SIMPLIFIED_WORDING[term]):
            continue  # the term itself is missing; find_missing_key_terms reports it
        simplified_words = found.get(term, [])
        original_levels = {FREQUENCY_WORDS[w] for w in original_words}
        simplified_levels = {FREQUENCY_WORDS[w] for w in simplified_words}
        if original_levels != simplified_levels:
            changes.append(
                {
                    "term": term,
                    "kind": "changed" if simplified_words else "dropped",
                    "original": original_words,
                    "simplified": simplified_words,
                }
            )
    return changes


def check_preservation(original: str, simplified: str) -> dict:
    """Compare original and simplified text; return a report dictionary."""
    original_numbers = Counter(extract_numbers(original))
    simplified_numbers = Counter(extract_numbers(simplified))

    missing_numbers = sorted((original_numbers - simplified_numbers).elements())
    fabricated_numbers = sorted((simplified_numbers - original_numbers).elements())
    number_risk_mismatches = find_number_risk_mismatches(original, simplified)
    missing_key_terms = find_missing_key_terms(original, simplified)
    frequency_changes = find_frequency_changes(original, simplified)

    return {
        "missing_numbers": missing_numbers,
        "possible_fabricated_numbers": fabricated_numbers,
        "number_risk_mismatches": number_risk_mismatches,
        "missing_key_terms": missing_key_terms,
        "frequency_changes": frequency_changes,
        "passed": not (
            missing_numbers
            or fabricated_numbers
            or number_risk_mismatches
            or missing_key_terms
            or frequency_changes
        ),
    }
