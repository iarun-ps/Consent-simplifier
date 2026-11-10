"""Run the full pipeline on one consent form: simplify, check, score readability.

Usage: python -m src.pipeline --input data/original/sample_form.txt
"""
import argparse
import json
from pathlib import Path

from src.checker import check_preservation
from src.evaluate import readability
from src.simplify import simplify_text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to a .txt consent form")
    args = parser.parse_args()

    original = Path(args.input).read_text(encoding="utf-8")
    simplified = simplify_text(original)

    name = Path(args.input).stem
    Path("data/simplified").mkdir(parents=True, exist_ok=True)
    Path(f"data/simplified/{name}_simplified.txt").write_text(
        simplified, encoding="utf-8"
    )

    result = {
        "readability_before": readability(original),
        "readability_after": readability(simplified),
        "preservation_report": check_preservation(original, simplified),
    }
    Path("results").mkdir(exist_ok=True)
    Path(f"results/{name}_report.json").write_text(
        json.dumps(result, indent=2, default=str), encoding="utf-8"
    )
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
