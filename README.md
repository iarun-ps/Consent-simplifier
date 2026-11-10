# Consent-simplifier

## Preservation checker

`src/checker.py` compares an original consent form with its simplified version and reports information that was lost, changed or invented. It needs no model and no internet.

Run it on two text files:

```bash
python -m src.checker --original data/original/sample_form.txt --simplified tests/fixtures/v5_1_simplified.txt
```

From Python:

```python
from src.checker import check_preservation
report = check_preservation(original_text, simplified_text)
```

The report is a dictionary:

| Key | Meaning |
|---|---|
| `missing_numbers` | numbers, ranges or percentages in the original that are gone |
| `possible_fabricated_numbers` | numbers in the simplified text that are not in the original |
| `number_risk_mismatches` | a number that now sits next to a different risk |
| `missing_key_terms` | risks, alternatives, contraindications or benefits that were lost |
| `frequency_changes` | frequency words (for example "rare") that were dropped or changed |
| `passed` | `True` only when all lists above are empty |

Run the tests with `python -m pytest -q`.

Score the checker against the hand-made annotation (`data/annotations.csv`) with `python -m src.metrics`.

Known limits: the key term list in `KEY_TERMS` is written by hand and must grow with new forms; the checks compare the whole text word by word, so a changed list structure is not detected; results so far come from one form.