"""Simplify a medical consent form into patient-friendly language (local LLM)."""
import ollama

from src.config import MODEL_NAME, RANDOM_SEED
from src.terms import annotate_terms

SYSTEM_PROMPT = """You rewrite medical consent forms in plain language for patients.

Rules:
1. Rewrite every sentence in shorter, simpler words. Do not copy the original wording
   when a simpler word exists. Use short sentences, at about a 6th-8th grade level.
2. Copy every number, percentage and range exactly. Keep each number with the
   SAME risk it belongs to.
3. Keep frequency words as written (rare, common, may). Do not add new ones.
   If a risk has no number, give it no number.
4. Keep every risk, benefit, alternative and contraindication, and name each in full.
   Never replace a specific term with a vague phrase like "a blood problem".
5. Do not add any fact, cause, symptom or advice that is not in the original.
6. Keep the medical terms exactly as written. Do NOT put explanations in
   brackets; they are added automatically afterwards.
7. List the risks as bullet points, in the same order as the original.
8. Start directly with the rewritten text. No introduction and no closing remarks.

Example:
Original: "Participants must abstain from driving for 24 hours."
Rewritten: "- Do not drive for 24 hours."

Return only the rewritten text."""


def simplify_text(original_text: str) -> str:
    """Send the form to the local LLM, then add glossary meanings in brackets."""
    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": original_text},
        ],
        options={"temperature": 0, "seed": RANDOM_SEED},
    )
    return annotate_terms(response["message"]["content"])
