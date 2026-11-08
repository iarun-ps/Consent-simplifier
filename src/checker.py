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


def extract_numbers(text: str) -> list[str]:
    """Return numbers, ranges and percentages in a normal form.

    "2-5%", "2 to 5 percent" and "2–5%" all become "2-5%".
    """
    found = []
    for match in NUMBER_PATTERN.finditer(text):
        value = _clean(match.group("first"))
        if match.group("second"):
            value += "-" + _clean(match.group("second"))
        if match.group("pct"):
            value += "%"
        found.append(value)
    return found


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


def check_preservation(original: str, simplified: str) -> dict:
    """Compare original and simplified text; return a report dictionary."""
    original_numbers = Counter(extract_numbers(original))
    simplified_numbers = Counter(extract_numbers(simplified))

    missing_numbers = sorted((original_numbers - simplified_numbers).elements())
    fabricated_numbers = sorted((simplified_numbers - original_numbers).elements())
    missing_key_terms = find_missing_key_terms(original, simplified)
    return {
        "missing_numbers": missing_numbers,
        "possible_fabricated_numbers": fabricated_numbers,
        "missing_key_terms": missing_key_terms,
        "passed": not (missing_numbers or fabricated_numbers or missing_key_terms),
    }
