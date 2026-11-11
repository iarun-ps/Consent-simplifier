from pathlib import Path

from src.checker import KEY_TERMS
from src.metrics import RUNS, load_annotations, report_flags, score_flags


def test_perfect_match_scores_one():
    rows = [
        {"checker_term": "hemorrhage", "status": "altered"},
        {"checker_term": "infection", "status": "kept"},
    ]
    result = score_flags(rows, {"hemorrhage"})
    assert result["precision"] == 1.0
    assert result["recall"] == 1.0
    assert result["f1"] == 1.0


def test_false_alarm_and_miss_are_counted():
    rows = [
        {"checker_term": "a", "status": "kept"},
        {"checker_term": "b", "status": "altered"},
        {"checker_term": "c", "status": "missing"},
    ]
    result = score_flags(rows, {"a", "c"})
    assert result["true_positives"] == 1
    assert result["false_positives"] == 1
    assert result["false_negatives"] == 1
    assert result["precision"] == 0.5
    assert result["recall"] == 0.5
    assert result["f1"] == 0.5


def test_problem_without_a_rule_counts_as_a_miss():
    rows = [{"checker_term": "", "status": "altered"}]
    result = score_flags(rows, set())
    assert result["false_negatives"] == 1
    assert result["recall"] == 0.0


def test_finding_without_any_annotated_problem_is_a_false_alarm():
    result = score_flags([], {"number:2.1"})
    assert result["false_positives"] == 1
    assert result["precision"] == 0.0


def test_kept_rows_without_checker_term_are_ignored():
    rows = [{"checker_term": "", "status": "kept"}]
    result = score_flags(rows, set())
    assert result["true_positives"] == 0
    assert result["false_positives"] == 0
    assert result["false_negatives"] == 0


def test_report_flags_names_every_finding():
    report = {
        "missing_numbers": ["95%"],
        "possible_fabricated_numbers": ["5%"],
        "number_risk_mismatches": [
            {"number": "2%", "expected": ["infection"], "found": "hemorrhage"}
        ],
        "missing_key_terms": ["hemorrhage"],
        "frequency_changes": [
            {
                "term": "conversion to open surgery",
                "kind": "dropped",
                "original": ["rare"],
                "simplified": [],
            }
        ],
    }
    assert report_flags(report) == {
        "number:95%",
        "fabricated:5%",
        "mismatch:2%",
        "hemorrhage",
        "frequency:conversion to open surgery",
    }


def test_annotation_terms_exist_in_key_terms():
    names = {name for name, _category, _original, _simplified in KEY_TERMS}
    for row in load_annotations("data/annotations.csv"):
        term = row["checker_term"]
        if term and ":" not in term:
            assert term in names


def test_every_annotated_run_is_registered_and_has_files():
    for row in load_annotations("data/annotations.csv"):
        assert (row["form"], row["model_run"]) in RUNS
    for original_path, simplified_path in RUNS.values():
        assert Path(original_path).exists()
        assert Path(simplified_path).exists()