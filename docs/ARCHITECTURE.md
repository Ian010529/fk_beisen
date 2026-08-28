# Architecture

## Data flow

1. `sync` downloads the upstream `questions.js`.
2. `importer.py` extracts one-line JSON question objects and normalizes them into `Question` dataclasses.
3. `validator.py` catches missing/invalid answers, A-D shape errors, duplicate IDs, and explicit analysis/answer conflicts.
4. `question_bank.json` is used by the local practice CLI.
5. `vision.py` compares local images using perceptual similarity rather than byte/file hashes.

## Image similarity

The image pipeline is designed for resize/re-encode differences:

- near-white border crop
- aspect-ratio-preserving letterbox
- DCT pHash for broad perceptual similarity
- ORB local feature matching for structural confirmation
- SSIM for normalized structural similarity

Combined score = `0.30*pHash + 0.40*ORB + 0.30*SSIM`.

This is intentionally a local image-comparison primitive. It is not wired to Selenium, browser scraping, or assessment submission.

## Future extension points

- Image index cache: precompute pHash + ORB descriptors for all bank images.
- Grouped data-analysis questions: cluster questions that share the same source chart.
- UI: reuse the upstream React practice app or expose the normalized JSON to a new frontend.
- Upstream pinning: change `sync.py` URLs from `main` to a commit SHA for reproducible builds.
