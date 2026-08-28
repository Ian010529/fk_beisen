# BeiSen Practice Plus

A clean integration layer around the public `BeiSen_Practice` question bank for **local practice, validation, and image-similarity testing**.

It is designed around two observations from the upstream projects:

- `BeiSen_Practice` contains 445 questions (40 verbal, 253 data-analysis, 152 graphic-reasoning) plus referenced question images.
- The older automation project uses Selenium and text matching for personality/single-choice flows; A/B/C/D aptitude questions need a separate data model and matcher.

This repository does **not** include code that connects to or automatically submits answers on a live recruitment/assessment website.

## Features

- Sync all 445 upstream question records into a normalized JSON bank.
- Download every image referenced by the bank.
- Validate malformed records before using them in practice.
- Detect missing answers, invalid answer keys, and answer/analysis conflicts.
- Fuzzy text search for local bank QA and deduplication.
- Perceptual image comparison that tolerates resize/re-encoding:
  - DCT pHash
  - ORB local features
  - SSIM
- Local interactive practice CLI.
- Tests for importer, validator, text normalization, and image robustness.

## Install

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e .
```

## 1. Sync the upstream bank

```bash
beisen-practice sync --data-dir data
```

This creates locally:

```text
data/
├── questions.js
├── question_bank.json
├── sync_metadata.json
└── question-bank/
    ├── data-image*.jpg
    └── graphic-image*.jpg
```

The large upstream data/assets are `.gitignore`d so this repo does not republish another project's content. The source is:

- https://github.com/Liqing-Lin/BeiSen_Practice

## 2. Validate before practice

```bash
beisen-practice validate data/question_bank.json --output data/validation_report.json
```

The validator flags records such as:

- answer missing
- answer outside A-D / not present in options
- explicit `正确答案：X` text conflicting with the `answer` field
- malformed option shape
- duplicate IDs
- graphic questions without image references

## 3. Local practice

```bash
beisen-practice practice data/question_bank.json --category verbal --count 10
beisen-practice practice data/question_bank.json --category data --count 10
beisen-practice practice data/question_bank.json --category graphic --count 10
```

## 4. Text-bank QA

```bash
beisen-practice search data/question_bank.json "输入一段题干" --limit 5
```

This prints candidate question IDs and similarity scores. It is useful for finding duplicates or checking OCR/transcription changes in a local dataset.

## 5. Compare two images

Do not use SHA/MD5 for visual identity. Re-encoding or resizing changes file hashes even if the image is visually the same.

```bash
beisen-practice compare-images ./a.jpg ./b.jpg
```

Example output:

```json
{
  "phash": 0.957,
  "orb": 0.812,
  "ssim": 0.934,
  "combined": 0.884
}
```

See `docs/ARCHITECTURE.md` for the image pipeline.

## Tests

```bash
pytest -q
```

## Upstream references

- `Blunnny/FUCK_BEISEN` — MIT-licensed Selenium automation architecture used as a reference for the older single-choice flow.
- `Liqing-Lin/BeiSen_Practice` — question-bank source and local-practice application.

No upstream question text or images are vendored in this repository; `sync` fetches them into ignored local data files.

## Publish as a new GitHub repository

If GitHub CLI is already authenticated on your machine:

```bash
./scripts/publish_github.sh beisen-practice-plus private
# or public:
./scripts/publish_github.sh beisen-practice-plus public
```
