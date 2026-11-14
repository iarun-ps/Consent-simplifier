# Reproducibility Information

## Project

Safe and Patient-Friendly Medical Consent Simplification Using Generative AI

## Development Environment

- Operating system: Windows
- Python version: 3.14.0
- Model runtime: Ollama
- Model: llama3.2:3b
- Ollama model ID: a80c4f17acd5
- Model size: approximately 2.0 GB
- Temperature: 0
- Random seed: 42

## Dependencies

The project provides two dependency files:

- requirements.txt: Minimum package version requirements.
- requirements-lock.txt: Exact installed Python package versions recorded during development.

For reproducing the recorded Python environment:

    python -m pip install -r requirements-lock.txt

The lock file is an environment snapshot and may contain packages not directly required by this project.

## Reproducing Evaluation Results

The repository includes the original medical consent forms, frozen simplified outputs, and manually prepared annotations.

Run automated tests:

    python -m pytest -q

Calculate preservation checker metrics:

    python -m src.metrics

Generate the final results and figures:

    python -m src.make_results

The reported evaluation results are:

- True positives: 7
- False positives: 0
- False negatives: 6
- Precision: 1.000
- Recall: 0.538
- F1-score: 0.700

The evaluation uses frozen simplified texts to maintain consistency with the manual annotations.

## Reproducing LLM Generation

Install Ollama and obtain the model:

    ollama pull llama3.2:3b

The recorded model ID is a80c4f17acd5.

Generation settings:

- Temperature: 0
- Seed: 42

Identical outputs across different machines are not guaranteed, even when the same model name and settings are used.

## Limitations

- Exact dependency versions may not install on every operating system or Python version.
- The dependency lock file does not include the Ollama model weights.
- The evaluation was performed on three consent forms.
- Reproducibility on an independent computer has not yet been verified.
