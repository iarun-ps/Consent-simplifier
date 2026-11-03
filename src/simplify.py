"""Simplify a medical consent form into patient-friendly language (local LLM)."""
import ollama

from src.config import MODEL_NAME, RANDOM_SEED

SYSTEM_PROMPT = """You simplify medical consent forms for patients.
Rules:
- Write at about a 6th-8th grade reading level.
- Keep EVERY risk, probability, number, benefit, alternative, and
  contraindication. Never round, soften, or drop figures.
- Do not add any information that is not in the original.
- Explain medical terms in brackets the first time they appear.
Return only the simplified text."""


def simplify_text(original_text: str) -> str:
    """Send the original consent text to the local LLM and return simplified text."""
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": original_text},
        ],
        options={"temperature": 0, "seed": RANDOM_SEED},
    )
    return response["message"]["content"]
