# Session 4: Data Cleaning and Deduplication

This assignment adds a standalone, reproducible Session 4 cleaning run without changing the existing Session 5 training pipeline.

## Dataset

The selected source is [HuggingFaceH4/ultrachat_200k](https://huggingface.co/datasets/HuggingFaceH4/ultrachat_200k), an MIT-licensed English conversation dataset. Its `train_sft` split contains 207,865 conversations. The default run cleans the first 12,000 records in source order. At roughly 900 whitespace-delimited words per record, that slice is in the requested 10–100M token-size range, but the report labels the count as a word-based proxy rather than a tokenizer measurement.

Related sources raised by the course include [Dolma](https://huggingface.co/datasets/allenai/dolma), which is a useful pretraining-text candidate but not a direct SFT conversation source, and the Indic web crawl discussed in the lesson. The latter needs a language-aware filter and Indic-specific quality validation; this English-only run does not claim to solve that problem.

## Strategies

The session's eight named cleaning commitments are applied or explicitly audited:

1. Canonicalize structured conversation roles without introducing fake text markers.
2. Normalize Unicode, HTML entities, invisible noise, and whitespace while preserving ZWJ/ZWNJ.
3. Detect language and retain English records above a confidence threshold.
4. Filter records that are too short or dominated by repeated lines.
5. Remove exact duplicates and near-duplicates using 5-word MinHash shingles and LSH.
6. Mask emails, phone numbers, and IPv4 addresses with regular expressions.
7. Scan for synthetic evaluation canaries and report the limitation that full benchmark fingerprints were not scanned.
8. Record deterministic content hashes and source/cleaner provenance.

## Run

Install the repository requirements, then run:

```bash
python S4-data-cleaning-deduplication/clean_dataset.py
```

The script fetches records from the Hugging Face Datasets Server and writes the machine-readable report under `S4-data-cleaning-deduplication/artifacts/`. Add `--write-cleaned` to also emit the cleaned JSONL; this is opt-in because conversations can still contain names that regex-only PII masking does not recognize. For a quick smoke run, pass `--rows 100 --output /tmp/assignment4-smoke`.

Serve the widget locally from the repository root:

```bash
python -m http.server 8000
```

Open `http://localhost:8000/S4-data-cleaning-deduplication/`.

## Deploy to Netlify

The repository-root `netlify.toml` configures Netlify to publish this directory as a static site. Commit and push the project to GitHub, then in Netlify choose **Add new site → Import an existing project**, connect the repository, and deploy using the detected configuration. The published dashboard URL will be shown in Netlify when the deploy completes. No build command is needed; keep `artifacts/stats.json` in the published directory.

Alternatively, deploy this directory with Netlify Drop at <https://app.netlify.com/drop>. The static dashboard works with the included report; the Python cleaning script itself is not run by the static site.

## Verification and limits

Run `pytest -q tests/test_assignment4_cleaning.py` for the focused cleaning tests. Counts are measured against the downloaded sample; they are not projected to the entire source split. PII coverage is regex-only, the contamination scan uses two synthetic canaries, and language quality is not validated for Indic scripts. Do not treat this sample run as a production-ready multilingual corpus.