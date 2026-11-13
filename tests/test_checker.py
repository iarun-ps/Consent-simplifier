from pathlib import Path

from src.checker import (
    check_preservation,
    extract_numbers,
    find_frequency_changes,
    find_missing_key_terms,
    find_missing_qualifiers,
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

def test_list_markers_are_not_numbers():
    text = (
        "1. Introduction\n"
        "2.1 Risks of surgery\n"
        "2.2. Bleeding may occur in 3% of patients\n"
        "(3) Infection\n"
        "4) Pain"
    )
    assert extract_numbers(text) == ["3%"]


def test_decimal_at_line_start_is_still_a_number():
    assert extract_numbers("2.5 mg is given\n0.5% of patients") == ["2.5", "0.5%"]


def test_renumbered_list_does_not_cause_missing_numbers():
    original = "2.1 Infection may occur.\n2.2 Bleeding may occur."
    simplified = "- Infection may occur.\n- Bleeding may occur."
    assert check_preservation(original, simplified)["missing_numbers"] == []


def test_real_number_is_still_found_next_to_list_markers():
    original = "5.1 Success rate is more than 95%.\n5.2 Conversion occurs in 3% of cases."
    simplified = "- Success is high.\n- Conversion occurs in 3% of cases."
    result = check_preservation(original, simplified)
    assert result["missing_numbers"] == ["95%"]

def test_dropped_solely_is_flagged():
    original = "Additional treatment will be given solely to save my life."
    simplified = "Additional treatment will be given to save my life."
    assert find_missing_qualifiers(original, simplified) == [
        {"qualifier": "only/solely", "original": 1, "simplified": 0}
    ]


def test_synonym_counts_as_kept():
    original = "Additional treatment will be given solely to save my life."
    simplified = "Additional treatment will be given only to save my life."
    assert find_missing_qualifiers(original, simplified) == []


def test_dropped_acute_or_chronic_is_flagged():
    result = find_missing_qualifiers("Acute or chronic pain may occur.", "Pain may occur.")
    assert result == [{"qualifier": "acute/chronic", "original": 2, "simplified": 0}]


def test_dropped_condition_on_a_number_is_flagged():
    original = "Depending on the stage of the disease, conversion occurs in 3% of cases."
    simplified = "Conversion occurs in 3% of cases."
    assert find_missing_qualifiers(original, simplified) == [
        {"qualifier": "depends on", "original": 1, "simplified": 0}
    ]


def test_unchanged_text_has_no_missing_qualifiers():
    text = "Massive bleeding may occur, but only rarely."
    assert find_missing_qualifiers(text, text) == []


def test_report_includes_missing_qualifiers():
    result = check_preservation("Pain may occur solely at night.", "Pain may occur at night.")
    assert result["missing_qualifiers"] == [
        {"qualifier": "only/solely", "original": 1, "simplified": 0}
    ]
    assert result["passed"] is False

def test_frequency_heading_applies_to_bulleted_risk():
    original = (
        "Very rare - Extremely unlikely to happen (less than 1 in 1000)\n"
        "Infection (endophthalmitis) or bleeding inside the eye."
    )
    simplified = (
        "Very rare - Extremely unlikely to happen (less than 1 in 1000)\n"
        "• Infection (endophthalmitis) or bleeding inside the eye."
    )

    assert find_frequency_changes(original, simplified) == []
