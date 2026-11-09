"""Sentence matching: find original text that has no match in the simplified
text (possible omissions) and simplified text that has no match in the
original (possible hallucinations)."""

import re
from collections.abc import Callable
from pathlib import Path

from src.checker import check_preservation

# A function that takes two lists of texts and returns a table of scores:
# table[i][j] is how similar first[i] is to second[j] (1.0 = same meaning).
Similarity = Callable[[list[str], list[str]], list[list[float]]]

_MODEL = None


def embedding_similarity(first: list[str], second: list[str]) -> list[list[float]]:
    """Cosine similarity of sentence embeddings (loads the model on first use)."""
    global _MODEL
    if _MODEL is None:
        from sentence_transformers import SentenceTransformer

        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    a = _MODEL.encode(first, normalize_embeddings=True)
    b = _MODEL.encode(second, normalize_embeddings=True)
    return (a @ b.T).tolist()


# A fragment ends after . ! ? and a space, at a bullet point, after a blank
# line, or after a comma, semicolon or colon followed by a space.
_FRAGMENT_SPLIT = re.compile(r"(?<=[.!?])\s+|\n\s*[•\-*]\s*|\n\s*\n|[,;:]\s+")


def split_fragments(text: str, min_words: int = 3) -> list[str]:
    """Split text into short fragments; very short ones are dropped."""
    parts = _FRAGMENT_SPLIT.split(text)
    fragments = [" ".join(part.split()) for part in parts]
    return [f for f in fragments if len(f.split()) >= min_words]


def best_matches(
    texts: list[str],
    others: list[str],
    similarity: Similarity = embedding_similarity,
) -> list[tuple[float, str]]:
    """For each text, return (best score, best matching text from others)."""
    if not texts:
        return []
    if not others:
        return [(0.0, "")] * len(texts)
    results = []
    for row in similarity(texts, others):
        best = max(range(len(row)), key=row.__getitem__)
        results.append((row[best], others[best]))
    return results


def _flag_unmatched(
    texts: list[str], others: list[str], threshold: float, similarity: Similarity
) -> list[dict]:
    flagged = []
    for text, (score, closest) in zip(texts, best_matches(texts, others, similarity)):
        if score < threshold:
            flagged.append({"text": text, "score": round(score, 2), "closest": closest})
    return flagged


def find_unmatched(
    original_units: list[str],
    simplified_units: list[str],
    threshold: float = 0.45,
    similarity: Similarity = embedding_similarity,
) -> tuple[list[dict], list[dict]]:
    """Return (possible omissions, possible hallucinations)."""
    omissions = _flag_unmatched(original_units, simplified_units, threshold, similarity)
    hallucinations = _flag_unmatched(
        simplified_units, original_units, threshold, similarity
    )
    return omissions, hallucinations


def check_with_sentence_matching(
    original: str,
    simplified: str,
    threshold: float = 0.45,
    similarity: Similarity = embedding_similarity,
) -> dict:
    """Run check_preservation and add the sentence matching results."""
    report = check_preservation(original, simplified)
    omissions, hallucinations = find_unmatched(
        split_fragments(original), split_fragments(simplified), threshold, similarity
    )
    report["possible_omissions"] = omissions
    report["possible_hallucinations"] = hallucinations
    report["passed"] = report["passed"] and not (omissions or hallucinations)
    return report


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Sentence matching report.")
    parser.add_argument("--original", required=True, help="Original form (.txt)")
    parser.add_argument("--simplified", required=True, help="Simplified form (.txt)")
    parser.add_argument("--threshold", type=float, default=0.45)
    args = parser.parse_args()

    original = Path(args.original).read_text(encoding="utf-8")
    simplified = Path(args.simplified).read_text(encoding="utf-8")
    original_units = split_fragments(original)
    simplified_units = split_fragments(simplified)

    print("ORIGINAL fragments and their best match in the simplified text")
    for text, (score, closest) in zip(
        original_units, best_matches(original_units, simplified_units)
    ):
        print(f"{score:.2f}  {text}\n        -> {closest}")

    print("\nSIMPLIFIED fragments and their best match in the original")
    for text, (score, closest) in zip(
        simplified_units, best_matches(simplified_units, original_units)
    ):
        print(f"{score:.2f}  {text}\n        -> {closest}")

    print("\nFULL REPORT")
    report = check_with_sentence_matching(original, simplified, args.threshold)
    print(json.dumps(report, indent=2))
