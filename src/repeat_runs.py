"""Repeat the simplification of each form several times to measure variability.

For every form in data/original the form is simplified N times. Each run is
checked for preservation and scored for readability. The runs are then
compared: how much the reading grade moves, and how much the checker's
findings change from run to run.

Outputs (data/simplified is never touched):
  results/repeat/<form>/run_<k>.txt   every simplified text
  results/repeat_runs.csv             one row per run
  results/repeat_summary.json         one summary per form

Usage:
  python -m src.repeat_runs --runs 5
  python -m src.repeat_runs --runs 3 --forms cataract_surgery_nhs
"""
import argparse
import csv
import json
import statistics
import time
from itertools import combinations
from pathlib import Path

from src.checker import check_preservation
from src.config import MODEL_NAME
from src.evaluate import readability
from src.metrics import report_flags
from src.simplify import simplify_text

INPUT_DIR = Path("data/original")
OUT_DIR = Path("results/repeat")
CSV_PATH = Path("results/repeat_runs.csv")
SUMMARY_PATH = Path("results/repeat_summary.json")


def jaccard(a: set, b: set) -> float:
    """Overlap between two sets: 1.0 means identical, 0.0 means nothing shared."""
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def mean_pairwise_jaccard(flag_sets: list[set]) -> float:
    """Average overlap of the checker's findings over every pair of runs."""
    pairs = list(combinations(flag_sets, 2))
    if not pairs:
        return 1.0
    return sum(jaccard(a, b) for a, b in pairs) / len(pairs)


def _sd(values: list[float]) -> float:
    return statistics.stdev(values) if len(values) > 1 else 0.0


def summarise_form(runs: list[dict]) -> dict:
    """Reduce the runs of one form to the numbers used in the report."""
    grades = [r["grade_after"] for r in runs]
    counts = [r["n_flags"] for r in runs]
    sets = [r["flags"] for r in runs]
    in_every_run = set.intersection(*sets)
    in_any_run = set.union(*sets)
    return {
        "runs": len(runs),
        "distinct_texts": len({r["text"] for r in runs}),
        "grade_after_mean": round(statistics.mean(grades), 2),
        "grade_after_sd": round(_sd(grades), 2),
        "flags_mean": round(statistics.mean(counts), 2),
        "flags_sd": round(_sd(counts), 2),
        "flags_min": min(counts),
        "flags_max": max(counts),
        "flags_in_every_run": len(in_every_run),
        "flags_in_some_runs_only": len(in_any_run - in_every_run),
        "flag_agreement_jaccard": round(mean_pairwise_jaccard(sets), 3),
    }


def run_form(path: Path, n_runs: int) -> list[dict]:
    """Simplify one form n_runs times and collect the scores of each run."""
    original = path.read_text(encoding="utf-8")
    form_dir = OUT_DIR / path.stem
    form_dir.mkdir(parents=True, exist_ok=True)
    runs = []
    for k in range(1, n_runs + 1):
        start = time.time()
        text = simplify_text(original)
        (form_dir / f"run_{k}.txt").write_text(text, encoding="utf-8")
        report = check_preservation(original, text)
        flags = report_flags(report)
        after = readability(text)
        runs.append(
            {
                "form": path.stem,
                "run": k,
                "model": MODEL_NAME,
                "grade_after": after["flesch_kincaid_grade"],
                "ease_after": after["flesch_reading_ease"],
                "n_flags": len(flags),
                "n_fabricated_numbers": len(report["possible_fabricated_numbers"]),
                "flags": flags,
                "text": text,
            }
        )
        print(f"  run {k}/{n_runs}: {len(flags)} findings, {time.time() - start:.0f}s")
    return runs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs", type=int, default=5, help="runs per form")
    parser.add_argument("--forms", nargs="*", help="form names without .txt")
    args = parser.parse_args()

    paths = sorted(INPUT_DIR.glob("*.txt"))
    if args.forms:
        paths = [p for p in paths if p.stem in args.forms]

    Path("results").mkdir(exist_ok=True)
    summary, rows = {}, []
    for path in paths:
        print(f"{path.name} ({args.runs} runs, model {MODEL_NAME})")
        runs = run_form(path, args.runs)
        summary[path.stem] = summarise_form(runs)
        if summary[path.stem]["distinct_texts"] == 1 and len(runs) > 1:
            print("  WARNING: all runs gave identical text. The model settings "
                  "probably fix the seed or use temperature 0.")
        rows += runs

    with open(CSV_PATH, "w", newline="", encoding="utf-8") as file:
        fields = ["form", "run", "model", "grade_after", "ease_after",
                  "n_flags", "n_fabricated_numbers", "flags"]
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        for r in rows:
            writer.writerow({**{k: r[k] for k in fields if k != "flags"},
                             "flags": ";".join(sorted(r["flags"]))})
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"\nSaved {CSV_PATH} and {SUMMARY_PATH}")
    for form, row in summary.items():
        print(form, row)


if __name__ == "__main__":
    main()
