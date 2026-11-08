from src.terms import build_glossary_hint, extract_terms


def test_finds_known_terms():
    text = "Risks include thromboembolism and hemorrhage."
    found = {item["term"] for item in extract_terms(text)}
    assert {"thromboembolism", "hemorrhage"} <= found


def test_prefers_longest_term():
    text = "The patient had a myocardial infarction."
    found = {item["term"] for item in extract_terms(text)}
    assert "myocardial infarction" in found


def test_no_terms_gives_empty_hint():
    assert build_glossary_hint("The weather is nice today.") == ""


def test_annotate_adds_meaning_once():
    from src.terms import annotate_terms

    text = "Risk of hemorrhage. Hemorrhage is serious."
    result = annotate_terms(text)
    assert result.count("heavy bleeding") == 1


def test_annotate_replaces_empty_brackets():
    from src.terms import annotate_terms

    result = annotate_terms("This is [contraindicated] for you.")
    assert "[contraindicated]" not in result
    assert "not safe or not advised" in result
