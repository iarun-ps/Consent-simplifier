from src.matching import (
    check_with_sentence_matching,
    find_unmatched,
    split_fragments,
)


def word_overlap(first, second):
    """Tiny stand-in for the embedding model: share of words in common."""

    def score(a, b):
        words_a, words_b = set(a.lower().split()), set(b.lower().split())
        return len(words_a & words_b) / len(words_a | words_b)

    return [[score(a, b) for b in second] for a in first]


def test_split_fragments_splits_and_drops_short_pieces():
    text = "Risks include infection (2%), hemorrhage (5%). Rare cases need surgery."
    assert split_fragments(text) == [
        "Risks include infection (2%)",
        "Rare cases need surgery.",
    ]


def test_original_fragment_without_match_is_a_possible_omission():
    original = "Infection occurs in some patients. Bleeding may need a transfusion."
    simplified = "Infection occurs in some patients."
    omissions, hallucinations = find_unmatched(
        split_fragments(original),
        split_fragments(simplified),
        threshold=0.5,
        similarity=word_overlap,
    )
    assert [o["text"] for o in omissions] == ["Bleeding may need a transfusion."]
    assert hallucinations == []


def test_simplified_fragment_without_match_is_a_possible_hallucination():
    original = "Infection occurs in some patients."
    simplified = (
        "Infection occurs in some patients. Infection also affects the lungs badly."
    )
    omissions, hallucinations = find_unmatched(
        split_fragments(original),
        split_fragments(simplified),
        threshold=0.5,
        similarity=word_overlap,
    )
    assert omissions == []
    assert [h["text"] for h in hallucinations] == [
        "Infection also affects the lungs badly."
    ]


def test_empty_simplified_text_flags_every_original_fragment():
    omissions, hallucinations = find_unmatched(
        ["Infection occurs often here"], [], similarity=word_overlap
    )
    assert len(omissions) == 1
    assert hallucinations == []


def test_report_includes_sentence_matching_results():
    original = "Infection occurs in some patients."
    simplified = (
        "Infection occurs in some patients. Infection also affects the lungs badly."
    )
    report = check_with_sentence_matching(
        original, simplified, threshold=0.5, similarity=word_overlap
    )
    assert report["possible_omissions"] == []
    assert len(report["possible_hallucinations"]) == 1
    assert report["passed"] is False
