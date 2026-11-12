
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
- Same form, temperature 0, seed 42: two consecutive runs gave identical text, but a later batch run differed (see below).
- Likely reason for the lower score than v5: bracket explanations lengthen words and sentences,
  and bullet lines without full stops are counted as one long sentence by the readability tool.
- Pipeline now runs the preservation checker; it reports missing "hemorrhage",
  "cardiopulmonary events" and "conversion to open surgery", with no number problems.

## Second form: laparoscopic_cholecystectomy_ankara.txt (prompt v5.1, llama3.2:3b)
- Readability: Flesch reading ease 43.0 -> 49.5, Flesch-Kincaid grade 10.5 -> 9.8 (small change; most list items were copied).
- Checker output: 24 false "missing numbers" (list markers 2.1 to 5.5) plus one real miss, "95%".
- Errors found by hand that the checker missed: lost conditions on the 3% conversion rate; "acute or chronic"
  and "inflammation" dropped; "required anesthetic procedure" dropped; "solely" lost in 5.2; "that can replace
  this form of treatment" dropped in 5.4.
- Model introduced the misspelling "Laporoscopic", so the glossary could not annotate it; the original typo
  "post-cholecystecomy" was also not annotated.
- Sections 2 to 4 were copied almost word for word; many terms (cystic duct, abscess, trocar, perforated,
  lacerated, postprandial) are not in the glossary.
- Takeaways: checker key terms and number rules need to generalise beyond the first form; glossary needs
  more terms; the 3B model copies list items instead of simplifying them.

## Run-to-run variation (sample_form.txt, same prompt v5.1, model, temperature 0, seed 42)
- A later batch run changed the text in four places (dietary option reworded, contraindication reworded,
  "expected benefit" became "the good things", "patients" became "people"). Grade after: 13.9 -> 13.1.
- Key terms flagged rose from 3 to 5: the checker now also flags "dietary modification" and "contraindication".
- Takeaway: temperature 0 and a fixed seed reduce variation but do not remove it. Report results as single runs
  or repeat each form several times. The checker matches phrases, not meaning ("not recommended" passed,
  "not good for" did not).

## Checker scores against hand annotations (saved v5_1 outputs, python -m src.metrics)
- sample_form: TP 3, FP 0, FN 2; precision 1.0, recall 0.60, F1 0.75.
- Ankara form: TP 4, FP 0, FN 4; precision 1.0, recall 0.50, F1 0.667 (was 0.222 before the list-marker fix).
- Overall: TP 7, FP 0, FN 6; precision 1.0, recall 0.538, F1 0.70.
- The checker raised no false alarms but found only about half of the annotated problems.
- Limits: two forms, 13 annotated problems, one annotator, saved outputs from one run each.
- Saved in results/metrics_v5_1.json.

## Third form: cataract_surgery_nhs.txt (prompt v5.1, llama3.2:3b)
- Readability: Flesch reading ease 41.0 -> 44.6, Flesch-Kincaid grade 13.5 -> 12.3 (small change; the model mostly copied the text).
- Checker output: no missing or invented numbers; one frequency flag ("very rare" dropped for infection).
- Manual check: the flag looks like a false positive. "Very rare - Extremely unlikely to happen (less than 1 in 1000)"
  is still directly above the infection item. Likely cause: the simplified text uses bullets, the original does not.
- All four frequency groups and the figures "1 in 20", "1 in 100" and "1 in 1000" were kept.
- Real differences found by hand: "Cataract surgery involves replacing..." became "We will replace..."; the heading
  "Discomfort" was dropped; "The risks quoted in this consent form" was shortened.
- Hard terms (endophthalmitis, suprachoroidal haemorrhage, sympathetic ophthalmia, cystoid macular oedema) were not explained
  because they are not in the glossary.
- Takeaway: on a form that is already written for patients the model copies instead of simplifying, so checker results
  depend on how much the model changes the text.
