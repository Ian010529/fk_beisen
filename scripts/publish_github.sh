#!/usr/bin/env bash
set -euo pipefail

REPO_NAME="${1:-beisen-practice-plus}"
VISIBILITY="${2:-private}"

if ! command -v gh >/dev/null 2>&1; then
  echo "GitHub CLI (gh) is required: https://cli.github.com/" >&2
  exit 1
fi

gh auth status >/dev/null

if [ ! -d .git ]; then
  git init
  git add .
  git commit -m "Initial integration: local practice bank sync, validation and perceptual image matching"
fi

gh repo create "$REPO_NAME" "--$VISIBILITY" --source=. --remote=origin --push
