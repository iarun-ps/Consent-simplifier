"""Medical terminology extraction: a glossary lookup plus spaCy tokenisation."""
import re

import spacy

GLOSSARY = {
    "laparoscopic": "done through small cuts using a thin camera",
    "cholecystectomy": "surgery to remove the gallbladder",
    "thromboembolism": "a blood clot that travels through the blood",
    "hemorrhage": "heavy bleeding",
    "coagulopathy": "a problem with blood clotting",
    "cardiopulmonary": "affecting the heart and lungs",
    "contraindicated": "not safe or not advised",
    "biliary colic": "pain caused by gallstones",
    "postoperative": "after surgery",
    "transfusion": "receiving donated blood",
    "anesthesia": "medicine that blocks pain or keeps you asleep",
    "myocardial infarction": "heart attack",
    "arthroscopy": "looking inside a joint with a thin camera",
    "analgesic": "pain-relief medicine",
    "anticoagulant": "medicine that thins the blood",
    "hypertension": "high blood pressure",
    "incision": "a cut made during surgery",
    "sutures": "stitches",
    "biopsy": "taking a small piece of tissue for testing",
    "pulmonary embolism": "a blood clot in the lungs",
}

# Longest terms first, so "myocardial infarction" matches before shorter words.
_TERMS_LONGEST_FIRST = sorted(GLOSSARY, key=len, reverse=True)
_NLP = spacy.blank("en")  # tokenizer only, no model download needed


def extract_terms(text: str) -> list[dict]:
    """Return glossary terms found in the text, with plain-language meanings."""
    found = []
    seen = set()
    lowered = text.lower()
    for term in _TERMS_LONGEST_FIRST:
        if re.search(rf"\b{re.escape(term)}\b", lowered) and term not in seen:
            seen.add(term)
            found.append({"term": term, "meaning": GLOSSARY[term]})
    return found


def find_unknown_long_words(text: str, min_length: int = 12) -> list[str]:
    """Return long words not in the glossary, as candidates to add to it."""
    known = " ".join(GLOSSARY).lower()
    words = {
        tok.text.lower()
        for tok in _NLP(text)
        if tok.is_alpha and len(tok.text) >= min_length
    }
    return sorted(w for w in words if w not in known)


def build_glossary_hint(text: str) -> str:
    """Return a short glossary block to send to the model with the form."""
    terms = extract_terms(text)
    if not terms:
        return ""
    lines = [f"- {item['term']}: {item['meaning']}" for item in terms]
    return "Glossary (use these meanings in brackets; add no other facts):\n" + "\n".join(lines)


def annotate_terms(text: str) -> str:
    """Add the glossary meaning in brackets after the first use of each term."""
    for item in extract_terms(text):
        term, meaning = item["term"], item["meaning"]
        # Remove empty brackets the model may have put around the bare term.
        text = re.sub(rf"\[{re.escape(term)}\]", term, text, flags=re.IGNORECASE)
        pattern = re.compile(rf"\b{re.escape(term)}\b(?!\s*\()", re.IGNORECASE)
        match = pattern.search(text)
        if match:
            text = text[: match.end()] + f" ({meaning})" + text[match.end():]
    return text
