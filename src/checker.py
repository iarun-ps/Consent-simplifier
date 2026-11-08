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


def check_preservation(original: str, simplified: str) -> dict:
    """Compare original and simplified text; return a report dictionary."""
    original_numbers = Counter(extract_numbers(original))
    simplified_numbers = Counter(extract_numbers(simplified))

    missing_numbers = sorted((original_numbers - simplified_numbers).elements())
    fabricated_numbers = sorted((simplified_numbers - original_numbers).elements())
    missing_key_terms: list[str] = []  # added in the next step

    return {
        "missing_numbers": missing_numbers,
        "possible_fabricated_numbers": fabricated_numbers,
        "missing_key_terms": missing_key_terms,
        "passed": not (missing_numbers or fabricated_numbers or missing_key_terms),
    }
