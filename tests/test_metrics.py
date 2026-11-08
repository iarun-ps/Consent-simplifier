from src.checker import KEY_TERMS
from src.metrics import load_annotations, score_key_terms


def test_perfect_match_scores_one():
    rows = [
        {"checker_term": "hemorrhage", "status": "altered"},
        {"checker_term": "infection", "status": "kept"},
    ]
    result = score_key_terms(rows, ["hemorrhage"])
    assert result["precision"] == 1.0
    assert result["recall"] == 1.0
    assert result["f1"] == 1.0


def test_false_alarm_and_miss_are_counted():
    rows = [
        {"checker_term": "a", "status": "kept"},
        {"checker_term": "b", "status": "altered"},
        {"checker_term": "c", "status": "missing"},
    ]
    result = score_key_terms(rows, ["a", "c"])
    assert result["true_positives"] == 1
    assert result["false_positives"] == 1
    assert result["false_negatives"] == 1
    assert result["precision"] == 0.5
    assert result["recall"] == 0.5
    assert result["f1"] == 0.5


def test_rows_without_checker_term_are_skipped():
    rows = [{"checker_term": "", "status": "invented"}]
    result = score_key_terms(rows, [])
    assert result["true_positives"] == 0
    assert result["false_negatives"] == 0


def test_annotation_terms_exist_in_key_terms():
    names = {name for name, _category, _original, _simplified in KEY_TERMS}
    for row in load_annotations("data/annotations.csv"):
        if row["checker_term"]:
            assert row["checker_term"] in names
