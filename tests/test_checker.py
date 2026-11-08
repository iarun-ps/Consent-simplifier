from pathlib import Path

from src.checker import check_preservation, extract_numbers


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
