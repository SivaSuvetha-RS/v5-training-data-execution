# Conversational Dataset Cleaning Dashboard

This project demonstrates a reproducible workflow for cleaning and auditing a
sample of conversational training data. It includes a Python data-cleaning
script, a browser-based dashboard for exploring the results, and a machine-
readable report.

## Dataset

The workflow uses the English `train_sft` split of
[HuggingFaceH4/ultrachat_200k](https://huggingface.co/datasets/HuggingFaceH4/ultrachat_200k),
an MIT-licensed conversational dataset. It fetches a fixed source revision and
processes the first 12,000 rows by default, so runs use a consistent sample.

## What the cleaner does

- Normalizes structured conversation messages, Unicode, HTML entities, and
  whitespace.
- Checks language and filters short or repetitive conversations.
- Finds exact and near-duplicate content.
- Masks email addresses, phone numbers, and IPv4 addresses using regular
  expressions.
- Checks for synthetic contamination canaries and records content hashes and
  processing details.

The cleaning report describes the operations and their results. PII detection
is regex-based and does not reliably detect names. The canary check is limited
to synthetic examples; neither should be treated as comprehensive protection.
Word counts in the report are whitespace-delimited estimates, not model
tokenizer counts.

## Project contents

- `S4-data-cleaning-deduplication/clean_dataset.py` fetches and cleans the
  dataset.
- `S4-data-cleaning-deduplication/index.html` is the interactive results
  dashboard.
- `S4-data-cleaning-deduplication/artifacts/stats.json` contains the report
  displayed by the dashboard.
- `tests/test_assignment4_cleaning.py` contains focused tests for the cleaning
  workflow.

The included report reflects a sample run with 12,000 source rows and 11,800
accepted rows. Results are sample-specific and are not projections of the full
dataset.

## Run the cleaner

Install the project requirements and run the script from the repository root:

```bash
pip install -r requirements.txt
python S4-data-cleaning-deduplication/clean_dataset.py
```

The report is written to `S4-data-cleaning-deduplication/artifacts/stats.json`.
To also save the cleaned conversations as JSONL, opt in with:

```bash
python S4-data-cleaning-deduplication/clean_dataset.py --write-cleaned
```

For a smaller run, use `--rows`, for example:

```bash
python S4-data-cleaning-deduplication/clean_dataset.py --rows 100
```

## View the dashboard locally

From the repository root, start a local web server:

```bash
python -m http.server 8000
```

Then open <http://localhost:8000/S4-data-cleaning-deduplication/>. The dashboard
loads `artifacts/stats.json` from the same directory.

## Deploy

The root `netlify.toml` is configured to publish the dashboard directory as a
static site. Connect this repository to Netlify and deploy using the detected
configuration; no build command is required. Keep
`S4-data-cleaning-deduplication/artifacts/stats.json` in the published
directory so the dashboard can display the report. Netlify hosts the static
dashboard; it does not run the Python cleaning script.

## Tests

Run the focused cleaning tests with:

```bash
pytest -q tests/test_assignment4_cleaning.py
```
