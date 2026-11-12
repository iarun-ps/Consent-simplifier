"""Run the full pipeline on every .txt form in data/original.

For each form: simplify, check preservation, score readability.
Saves each simplified text, one report per form, and results/summary.json.

Usage: python -m src.run_all
"""
import json
from pathlib import Path

from src.checker import check_preservation
from src.evaluate import readability
from src.simplify import simplify_text

INPUT_DIR = Path("data/original")
OUTPUT_DIR = Path("data/simplified")
RESULTS_DIR = Path("results")

PROBLEM_KEYS = [
    "missing_numbers",
    "possible_fabricated_numbers",
    "number_risk_mismatches",
    "missing_key_terms",
    "frequency_changes",
]


def process_form(path: Path) -> dict:
    """Simplify one form, check it, save its files, and return the full result."""
    original = path.read_text(encoding="utf-8")
    simplified = simplify_text(original)
    (OUTPUT_DIR / f"{path.stem}_simplified.txt").write_text(
        simplified, encoding="utf-8"
    )
    result = {
        "form": path.name,
        "readability_before": readability(original),
        "readability_after": readability(simplified),
        "preservation_report": check_preservation(original, simplified),
    }
    (RESULTS_DIR / f"{path.stem}_report.json").write_text(
        json.dumps(result, indent=2, default=str), encoding="utf-8"
    )
    return result


def summarise(result: dict) -> dict:
    """Reduce one result to a single row of numbers for the summary table."""
    report = result["preservation_report"]
    row = {
        "form": result["form"],
        "grade_before": round(result["readability_before"]["flesch_kincaid_grade"], 1),
        "grade_after": round(result["readability_after"]["flesch_kincaid_grade"], 1),
        "passed": report["passed"],
    }
    for key in PROBLEM_KEYS:
        row[key] = len(report[key])
    return row


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(exist_ok=True)

    rows = []
    for path in sorted(INPUT_DIR.glob("*.txt")):
        print(f"Processing {path.name} ...")
        rows.append(summarise(process_form(path)))

    (RESULTS_DIR / "summary.json").write_text(
        json.dumps(rows, indent=2), encoding="utf-8"
    )
    print(f"\nDone. {len(rows)} forms processed. Summary: results/summary.json\n")
    for row in rows:
        print(row)


if __name__ == "__main__":
    main()
