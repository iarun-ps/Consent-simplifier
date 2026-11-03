"""Simplify a medical consent form into patient-friendly language (local LLM)."""
import ollama

from src.config import MODEL_NAME, RANDOM_SEED

SYSTEM_PROMPT = """You rewrite medical consent forms in plain language for patients.

Rules:
1. Keep every risk, number, percentage and range exactly as written.
   Keep each number attached to the SAME risk it belongs to. Never move a
   number to a different risk.
2. If the original gives no number or frequency for a risk, do not add one
   and do not add words like "rare" or "common".
3. Keep every risk, benefit, alternative and contraindication. Drop none.
4. Do not add any facts, causes, symptoms or advice that are not in the original.
5. Keep important medical terms. After each one, add a short plain-word
   explanation in brackets, without adding new medical claims.
6. Use short sentences, at about a 6th-8th grade reading level.
7. Keep the same order as the original and list the risks as bullet points.
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
