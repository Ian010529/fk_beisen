# Architecture

```text
BeiSen page
  └─ content.js: extract visible stem, options and image URLs
       └─ background.js: fetch protected images and call localhost
            └─ Python service
                 ├─ TextMatcher: normalized stem + option fuzzy search
                 ├─ ImageMatcher: pHash shortlist → ORB/SSIM rerank
                 └─ QuestionMatcher: answer text → visible option index
                      └─ content.js: highlight suggestion
```

## Why a local service

The question bank and 655 source images already live in the sibling `beisen` directory. Keeping computer-vision code in Python avoids bundling those assets and OpenCV into a browser extension. The service binds to `127.0.0.1` only and does not upload page content.

## Matching policy

Text is preferred when the best candidate is strong and separated from the runner-up. Images are used to confirm text or identify image-heavy questions. A reused chart image is never treated as a unique question by itself; accompanying stem/options disambiguate it.

The bank's answer letter is converted to canonical answer text, then fuzzily matched against the visible page options. This handles reordered options.
