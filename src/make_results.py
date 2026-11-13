"""Build the final results table and charts from the saved result files.

Reads:   results/summary.json          (from python -m src.run_all)
         results/metrics_v5_1.json     (from python -m src.metrics)
         results/repeat_summary.json   (from python -m src.repeat_runs, optional)
Writes:  results/final_table.csv
         results/fig_prf1.png, results/fig_readability.png, results/fig_repeat.png

Usage: python -m src.make_results
"""
import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

RESULTS = Path("results")


def load_json(name: str):
    path = RESULTS / name
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None


def build_rows(summary, metrics, repeat) -> list[dict]:
    """Merge the three result files into one row per form."""
    scores = {}
    for key, value in (metrics or {}).items():
        form = key.rsplit(" ", 1)[0] if key != "overall" else "overall"
        scores[form] = value
    rows = []
    for item in summary or []:
        stem = Path(item["form"]).stem
        row = {
            "form": stem,
            "grade_before": item["grade_before"],
            "grade_after": item["grade_after"],
            "fabricated_numbers": item["possible_fabricated_numbers"],
            "missing_numbers": item["missing_numbers"],
            "missing_key_terms": item["missing_key_terms"],
            "precision": scores.get(stem, {}).get("precision", ""),
            "recall": scores.get(stem, {}).get("recall", ""),
            "f1": scores.get(stem, {}).get("f1", ""),
        }
        if stem == "cataract_surgery_nhs":
            score = scores.get(stem, {})
            if (
                score.get("true_positives") == 0
                and score.get("false_positives") == 0
                and score.get("false_negatives") == 0
            ):
                row["precision"] = "N/A"
                row["recall"] = "N/A"
                row["f1"] = "N/A"

        rep = (repeat or {}).get(stem)
        row["repeat_runs"] = rep["runs"] if rep else ""
        row["repeat_grade_sd"] = rep["grade_after_sd"] if rep else ""
        row["repeat_flags_mean"] = rep["flags_mean"] if rep else ""
        row["repeat_flags_sd"] = rep["flags_sd"] if rep else ""
        row["repeat_agreement"] = rep["flag_agreement_jaccard"] if rep else ""
        rows.append(row)
    if "overall" in scores:
        rows.append({"form": "overall", **{k: scores["overall"][k]
                     for k in ("precision", "recall", "f1")}})
    return rows


def chart_prf1(rows) -> None:
    data = [
        r for r in rows
        if r.get("f1") not in ("", None, "N/A")
        and r["form"] != "cataract_surgery_nhs"
    ]
    if not data:
        return
    names = [r["form"].replace("_", "\n") for r in data]
    width, xs = 0.25, range(len(data))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for i, (key, label) in enumerate([("precision", "Precision"),
                                      ("recall", "Recall"), ("f1", "F1")]):
        ax.bar([x + (i - 1) * width for x in xs], [r[key] for r in data],
               width, label=label)
    ax.set_xticks(list(xs))
    ax.set_xticklabels(names, fontsize=8)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Score")
    ax.set_title("Checker scores against manual annotations")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "fig_prf1.png", dpi=200)
    plt.close(fig)


def chart_readability(rows) -> None:
    data = [r for r in rows if r.get("grade_before") not in (None, "")]
    if not data:
        return
    names = [r["form"].replace("_", "\n") for r in data]
    width, xs = 0.35, range(len(data))
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar([x - width / 2 for x in xs], [r["grade_before"] for r in data],
           width, label="Original")
    ax.bar([x + width / 2 for x in xs], [r["grade_after"] for r in data],
           width, label="Simplified")
    ax.set_xticks(list(xs))
    ax.set_xticklabels(names, fontsize=8)
    ax.set_ylabel("Flesch-Kincaid grade (lower is easier)")
    ax.set_title("Readability before and after simplification")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS / "fig_readability.png", dpi=200)
    plt.close(fig)


def chart_repeat(repeat) -> None:
    if not repeat:
        return
    names = list(repeat)
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar([n.replace("_", "\n") for n in names],
           [repeat[n]["flags_mean"] for n in names],
           yerr=[repeat[n]["flags_sd"] for n in names], capsize=5)
    ax.set_ylabel("Checker findings per run (mean ± SD)")
    ax.set_title("Variability across repeated runs")
    ax.tick_params(axis="x", labelsize=8)
    fig.tight_layout()
    fig.savefig(RESULTS / "fig_repeat.png", dpi=200)
    plt.close(fig)


def main() -> None:
    summary = load_json("summary.json")
    metrics = load_json("metrics_v5_1.json")
    repeat = load_json("repeat_summary.json")
    rows = build_rows(summary, metrics, repeat)
    if not rows:
        print("No results found. Run src.run_all and src.metrics first.")
        return
    fields = list(dict.fromkeys(k for r in rows for k in r))
    with open(RESULTS / "final_table.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    chart_prf1(rows)
    chart_readability(rows)
    chart_repeat(repeat)
    print("Saved results/final_table.csv and the charts (fig_*.png).")
    for r in rows:
        print(r)


if __name__ == "__main__":
    main()
