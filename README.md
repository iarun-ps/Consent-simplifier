# Safe and Patient-Friendly Medical Consent Simplification Using Generative AI

## Project Overview

This project uses Generative AI to simplify complex medical consent forms into patient-friendly language while checking whether important medical information is preserved.

The system uses Llama 3.2 (3B) through Ollama and a rule-based Medical Information Preservation Checker.

## Team Members

- Arun P S - MSc Data Science & BioAI
- Aparna V - MSc Computer Science with Data Analytics

## Technologies Used

- Python 3.14
- Ollama
- Llama 3.2 (3B)
- textstat
- Matplotlib
- pytest
- Git and GitHub

## Methodology

1. Collect medical consent forms.
2. Simplify the forms using a locally running LLM.
3. Compare original and simplified versions.
4. Detect missing or potentially fabricated information.
5. Evaluate readability using Flesch Reading Ease and Flesch-Kincaid Grade Level.
6. Evaluate preservation-checker performance using manual annotations.
7. Generate results, graphs and evaluation reports.

## Medical Information Preservation Checker

The checker identifies:

- Missing numbers and percentages
- Potentially fabricated numbers
- Number-risk mismatches
- Missing predefined medical terms
- Changes in risk-frequency descriptions
- Missing important qualifiers

Main implementation: `src/checker.py`

## Dataset

Three medical consent forms were evaluated:

1. Sample medical consent form
2. Ankara laparoscopic cholecystectomy consent form
3. NHS cataract surgery consent form

Original forms: `data/original/`

Simplified forms: `data/simplified/`

Frozen evaluation forms: `tests/fixtures/`

Manual annotations: `data/annotations.csv`

## Installation

Clone the repository:

    git clone https://github.com/iarun-ps/Consent-simplifier.git
    cd Consent-simplifier

Create and activate a virtual environment:

    python -m venv .venv
    source .venv/Scripts/activate

Install dependencies:

    pip install -r requirements.txt

Install Ollama separately and download the model:

    ollama pull llama3.2:3b

## Running the Project

Run the preservation checker:

    python -m src.checker --original data/original/sample_form.txt --simplified tests/fixtures/v5_1_simplified.txt

Run all automated tests:

    python -m pytest -q

Calculate evaluation metrics:

    python -m src.metrics

Generate results and graphs:

    python -m src.make_results

Generate simplified forms and reports:

    python -m src.run_all

WARNING: The last command overwrites existing generated simplified forms and reports.

## Experimental Results

### Readability Evaluation

| Consent Form | Original Grade | Simplified Grade |
|---|---:|---:|
| Sample form | 16.1 | 13.1 |
| Ankara surgery | 10.5 | 11.0 |
| NHS cataract surgery | 13.5 | 12.3 |

Readability improved for two of the three forms.

### Information Preservation Evaluation

| Metric | Result |
|---|---:|
| True Positives | 7 |
| False Positives | 0 |
| False Negatives | 6 |
| Precision | 100% |
| Recall | 53.8% |
| F1-score | 70% |

The cataract form had no annotated preservation errors or checker findings. Its individual precision, recall and F1-score are reported as N/A.

### Repeat-Run Evaluation

Three repeated simplifications were performed per form.

| Form | Runs | Mean Checker Findings |
|---|---:|---:|
| Sample form | 3 | 3 |
| Ankara surgery | 3 | 4 |
| Cataract surgery | 3 | 0 |

All repeated runs produced identical outputs under the configured deterministic model settings.

### Automated Testing

54 automated tests passed.

## Generated Results

- `results/final_table.csv` - Combined results
- `results/fig_prf1.png` - Precision, recall and F1-score
- `results/fig_readability.png` - Readability comparison
- `results/fig_repeat.png` - Repeat-run analysis
- `results/metrics_v5_1.json` - Evaluation metrics
- `results/repeat_summary.json` - Repeat-run statistics

## Limitations

- Rule-based medical terminology detection has limited coverage.
- Some medically important semantic changes may remain undetected.
- Detection of fabricated information is incomplete.
- Evaluation covers only three consent forms.
- Readability does not improve for every document.
- Repeatability under deterministic settings does not establish general reliability.
- Clinical validation has not been performed.

## Future Improvements

- Semantic consistency checking
- Expanded medical terminology coverage
- Evaluation using additional consent forms
- Expert clinical review
- Improved prompt engineering
- User-friendly interface

## Disclaimer

This is an academic research prototype. It does not replace original consent documents or professional medical judgment. Simplified medical information requires review by qualified healthcare professionals before clinical use.
