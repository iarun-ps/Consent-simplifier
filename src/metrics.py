"""Score the preservation checker against the hand-made annotation file."""

import csv
import json
from pathlib import Path

from src.checker import check_preservation

# Statuses in the annotation that count as a real problem.
PROBLEM_STATUSES = {"missing", "altered", "invented"}


def load_annotations(path: str) -> list[dict]:
    """Read the annotation CSV into a list of rows."""
    with open(path, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def score_key_terms(rows: list[dict], flagged_terms: list[str]) -> dict:
    """Compare the checker's flagged key terms with the hand-made labels.

    Only rows that have a checker_term are scored. A row is a real problem
    when its status is missing, altered or invented.
    """
    tp = fp = fn = 0
    for row in rows:
        term = row.get("checker_term")
        if not term:
            continue
        is_problem = row["status"] in PROBLEM_STATUSES
        flagged = term in flagged_terms
        if flagged and is_problem:
            tp += 1
        elif flagged:
            fp += 1
        elif is_problem:
            fn += 1

    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
    }


def evaluate_run(
    annotations_path: str,
    form: str,
    model_run: str,
    original_path: str,
    simplified_path: str,
) -> dict:
    """Run the checker on one simplified form and score it against the annotation."""
    rows = [
        row
        for row in load_annotations(annotations_path)
        if row["form"] == form and row["model_run"] == model_run
    ]
    original = Path(original_path).read_text(encoding="utf-8")
    simplified = Path(simplified_path).read_text(encoding="utf-8")
    report = check_preservation(original, simplified)
    return score_key_terms(rows, report["missing_key_terms"])


if __name__ == "__main__":
    result = evaluate_run(
        "data/annotations.csv",
        "sample_form",
        "v5_1",
        "data/original/sample_form.txt",
        "tests/fixtures/v5_1_simplified.txt",
    )
    print(json.dumps(result, indent=2))
