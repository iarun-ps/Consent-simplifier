"""Readability metrics for before/after comparison."""
import textstat


def readability(text: str) -> dict:
    """Return reading-ease and grade-level scores for a text."""
    return {
        "flesch_reading_ease": textstat.flesch_reading_ease(text),
        "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
    }
