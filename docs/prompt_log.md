
## v3 (strict prompt plus: copy frequency words, name alternatives in full, no intro)
- All numbers correct and attached to the right risk.
- "Cardiopulmonary" now kept as "heart and lungs"; "may" kept.
- Still added an intro line, despite rule 8.
- Added "in the lungs" to thromboembolism (hallucination).
- Dropped "rare" for conversion to open surgery and changed its meaning (omission, alteration).
- "Uncorrected coagulopathy" still "a blood problem"; "contraindicated" softened.
- Benefit generalised; biliary colic and gallstone complications lost.
- Medical terms not explained in brackets.
- Conclusion: prompt tuning has limited effect on a 3B model; a checker is needed.

## v5.1 (v5 with a non-medical example in the prompt)
- Invented antibiotics line gone; all numbers, "rare" and the benefit correct.
- Glossary meanings added once each by terms.py, including in the heading.
- Remaining errors: "cardiopulmonary" narrowed to "heart"; open surgery conversion worded as "the old way";
  "uncorrected coagulopathy" softened to "uncorrected bleeding problems" (no explanation added);
  "hemorrhage" dropped; dietary changes listed as a separate option; nested brackets after thromboembolism.
- Conclusion: prompt tuning has reached its limit for llama3.2:3b. Remaining errors are test cases for the checker.
- v5.1 readability on sample_form.txt: Flesch reading ease 0.9 -> 36.9, Flesch-Kincaid grade 16.1 -> 13.9.
  (The earlier 62.4 / 7.6 scores belong to v5, not v5.1.)
- Same form, temperature 0, seed 42 gave identical text on a second run (reproducible).
- Likely reason for the lower score than v5: bracket explanations lengthen words and sentences,
  and bullet lines without full stops are counted as one long sentence by the readability tool.
- Pipeline now runs the preservation checker; it reports missing "hemorrhage",
  "cardiopulmonary events" and "conversion to open surgery", with no number problems.
