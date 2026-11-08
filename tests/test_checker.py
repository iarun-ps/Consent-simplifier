from pathlib import Path

from src.checker import (
    check_preservation,
    extract_numbers,
    find_frequency_changes,
    find_missing_key_terms,
    find_number_risk_mismatches,
)


def test_extracts_percentages_and_ranges():
    text = "infection (2-5%), hemorrhage (less than 1%), bile duct injury (0.3-0.5%)"
    assert extract_numbers(text) == ["2-5%", "1%", "0.3-0.5%"]


def test_range_written_with_words_matches_symbols():
    assert extract_numbers("between 2 to 5 percent") == ["2-5%"]
    assert extract_numbers("about 2–5%") == ["2-5%"]


def test_trailing_zero_is_ignored():
    assert extract_numbers("0.50%") == ["0.5%"]


def test_real_sample_form_numbers():
    text = Path("data/original/sample_form.txt").read_text(encoding="utf-8")
    assert extract_numbers(text) == ["2-5%", "1%", "0.3-0.5%", "2%"]


def test_identical_numbers_pass():
    result = check_preservation(
        "infection (2-5%)", "Infection happens in 2 to 5 percent."
    )
    assert result["missing_numbers"] == []
    assert result["possible_fabricated_numbers"] == []
    assert result["passed"] is True


def test_missing_number_is_flagged():
    result = check_preservation("infection (2-5%), bleeding (1%)", "infection (2-5%)")
    assert result["missing_numbers"] == ["1%"]
    assert result["passed"] is False


def test_invented_number_is_flagged():
    result = check_preservation("infection (2%)", "infection (2%), bleeding (5%)")
    assert result["possible_fabricated_numbers"] == ["5%"]
    assert result["passed"] is False


def test_missing_key_term_is_flagged():
    result = find_missing_key_terms("risk of hemorrhage", "risk of infection")
    assert result == ["hemorrhage"]


def test_plain_wording_counts_as_kept():
    assert find_missing_key_terms("risk of hemorrhage", "risk of heavy bleeding") == []


def test_term_not_in_original_is_ignored():
    assert find_missing_key_terms("risk of infection", "risk of infection") == []


def test_narrowed_term_is_flagged():
    # v5.1: "cardiopulmonary" became "heart" and the lungs were lost
    original = "Adverse cardiopulmonary events may occur."
    assert find_missing_key_terms(original, "Heart problems may happen.") == [
        "cardiopulmonary events"
    ]
    assert find_missing_key_terms(original, "Heart and lung problems may happen.") == []


def test_v5_1_real_errors():
    original = Path("data/original/sample_form.txt").read_text(encoding="utf-8")
    simplified = Path("tests/fixtures/v5_1_simplified.txt").read_text(encoding="utf-8")
    result = check_preservation(original, simplified)
    assert result["missing_numbers"] == []
    assert result["number_risk_mismatches"] == []
    assert result["possible_fabricated_numbers"] == []
    assert sorted(result["missing_key_terms"]) == [
        "cardiopulmonary events",
        "conversion to open surgery",
        "hemorrhage",
    ]
    assert result["passed"] is False


def test_swapped_numbers_are_flagged():
    original = "Risks include infection (2%) and hemorrhage (5%)."
    simplified = "Risks include infection (5%) and heavy bleeding (2%)."
    result = find_number_risk_mismatches(original, simplified)
    assert [(m["number"], m["found"]) for m in result] == [
        ("5%", "infection"),
        ("2%", "hemorrhage"),
    ]


def test_number_written_before_its_risk_is_linked_to_it():
    original = (
        "Risks: infection (3%). "
        "In rare cases (about 2%), conversion to open surgery may be required."
    )
    simplified = (
        "Risks: infection (2%). "
        "In rare cases (about 3%), conversion to open surgery may be required."
    )
    result = find_number_risk_mismatches(original, simplified)
    assert [(m["number"], m["found"]) for m in result] == [
        ("2%", "infection"),
        ("3%", "conversion to open surgery"),
    ]


def test_numbers_next_to_same_risks_pass():
    original = "Risks include infection (2%) and hemorrhage (5%)."
    simplified = (
        "Infection happens in 2% of cases. Heavy bleeding happens in 5% of cases."
    )
    assert find_number_risk_mismatches(original, simplified) == []


def test_bullet_without_known_risk_is_not_blamed_on_previous_bullet():
    original = "Risks include infection (2%) and hemorrhage (5%)."
    simplified = "Risks:\n- Infection (2%)\n- Bleeding (5%)"
    assert find_number_risk_mismatches(original, simplified) == []


def test_rare_changed_to_very_rare_is_flagged():
    original = (
        "Infection is common. "
        "In rare cases, conversion to open surgery may be required."
    )
    simplified = (
        "Infection is common. "
        "In very rare cases, conversion to open surgery may be required."
    )
    assert find_frequency_changes(original, simplified) == [
        {
            "term": "conversion to open surgery",
            "kind": "changed",
            "original": ["rare"],
            "simplified": ["very rare"],
        }
    ]


def test_dropped_frequency_word_is_flagged():
    original = "In rare cases, conversion to open surgery may be required."
    simplified = "Conversion to open surgery may be required."
    result = find_frequency_changes(original, simplified)
    assert [(c["term"], c["kind"]) for c in result] == [
        ("conversion to open surgery", "dropped")
    ]


def test_same_frequency_level_passes():
    original = "In rare cases, conversion to open surgery may be required."
    simplified = "Rarely, conversion to open surgery may be needed."
    assert find_frequency_changes(original, simplified) == []


def test_missing_term_is_not_reported_as_frequency_change():
    original = "In rare cases, conversion to open surgery may be required."
    simplified = "The surgery might need to be done the old way."
    assert find_frequency_changes(original, simplified) == []
