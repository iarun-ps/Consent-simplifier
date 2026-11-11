"""Score the preservation checker against the hand-made annotation file."""

import csv
import json
from pathlib import Path

from src.checker import check_preservation

# Statuses in the annotation that count as a real problem.
PROBLEM_STATUSES = {"missing", "altered", "invented"}

# Where the original and simplified text of each annotated run are stored.
RUNS = {
    ("sample_form", "v5_1"): (
        "data/original/sample_form.txt",
        "tests/fixtures/v5_1_simplified.txt",
    ),
    ("laparoscopic_cholecystectomy_ankara", "v5_1"): (
        "data/original/laparoscopic_cholecystectomy_ankara.txt",
        "data/simplified/laparoscopic_cholecystectomy_ankara_simplified.txt",
    ),
}


def load_annotations(path: str) -> list[dict]:
    """Read the annotation CSV into a list of rows."""
    with open(path, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def report_flags(report: dict) -> set[str]:
    """Name every finding in a checker report, so findings can be compared."""
    flags = set(report["missing_key_terms"])
    flags |= {f"number:{n}" for n in report["missing_numbers"]}
    flags |= {f"fabricated:{n}" for n in report["possible_fabricated_numbers"]}
    flags |= {f"mismatch:{m['number']}" for m in report["number_risk_mismatches"]}
    flags |= {f"frequency:{c['term']}" for c in report["frequency_changes"]}
    flags |= {f"qualifier:{q['qualifier']}" for q in report.get("missing_qualifiers", [])}
    return flags


def _scores(tp: int, fp: int, fn: int) -> dict:
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


def score_flags(rows: list[dict], flags: set[str]) -> dict:
    """Compare the checker's findings with the hand-made labels.

    A row is a real problem when its status is missing, altered or invented.
    It is found when the finding named in its checker_term column was raised.
    A real problem with no checker_term is a miss: the checker has no rule for it.
    A finding that no real problem claims is a false alarm.
    """
    problems = [row for row in rows if row["status"] in PROBLEM_STATUSES]
    found = [row for row in problems if row.get("checker_term") in flags]
    claimed = {row["checker_term"] for row in problems if row.get("checker_term")}
    tp = len(found)
    fn = len(problems) - tp
    fp = len(flags - claimed)
    return _scores(tp, fp, fn)


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
    return score_flags(rows, report_flags(report))


def evaluate_all(annotations_path: str = "data/annotations.csv") -> dict:
    """Score every annotated run, then add up the counts for an overall score."""
    results = {}
    tp = fp = fn = 0
    for (form, model_run), (original_path, simplified_path) in RUNS.items():
        result = evaluate_run(
            annotations_path, form, model_run, original_path, simplified_path
        )
        results[f"{form} {model_run}"] = result
        tp += result["true_positives"]
        fp += result["false_positives"]
        fn += result["false_negatives"]
    results["overall"] = _scores(tp, fp, fn)
    return results


if __name__ == "__main__":
    print(json.dumps(evaluate_all(), indent=2))