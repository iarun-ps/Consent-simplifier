"""Simplify a medical consent form into patient-friendly language (local LLM)."""
import ollama

from src.config import MODEL_NAME, RANDOM_SEED

SYSTEM_PROMPT = """You rewrite medical consent forms in plain language for patients.

Rules:
1. Copy every number, percentage and range exactly. Keep each number with the
   SAME risk it belongs to.
2. Copy frequency words exactly (rare, common, may). Do not change them
   and do not add new ones. If a risk has no number, give it no number.
3. Keep every risk, benefit, alternative and contraindication. Name each
   alternative and each condition in full. Never replace a specific
   term with a vague phrase like "a blood problem" or "a different kind of surgery".
4. Do not add any fact, cause, symptom or advice that is not in the original.
5. Keep each medical term, then explain it in brackets in simple words.
6. Use short sentences, at about a 6th-8th grade reading level.
7. List the risks as bullet points, in the same order as the original.
8. Start directly with the rewritten text. No introduction and no closing remarks.
Return only the rewritten text."""


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
