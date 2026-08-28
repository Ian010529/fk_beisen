from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import quote

import requests

from .importer import parse_questions_js, write_bank

QUESTIONS_URL = "https://raw.githubusercontent.com/Liqing-Lin/BeiSen_Practice/refs/heads/main/src/data/questions.js"
IMAGE_BASE_URL = "https://raw.githubusercontent.com/Liqing-Lin/BeiSen_Practice/refs/heads/main/public/question-bank/"


def _download(url: str, path: Path, *, timeout: int = 45) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, timeout=timeout, stream=True) as response:
        response.raise_for_status()
        with path.open("wb") as f:
            for chunk in response.iter_content(chunk_size=1024 * 128):
                if chunk:
                    f.write(chunk)


def sync_bank(data_dir: str | Path, *, images: bool = True) -> dict[str, object]:
    data_dir = Path(data_dir)
    source_path = data_dir / "questions.js"
    bank_path = data_dir / "question_bank.json"
    image_dir = data_dir / "question-bank"

    _download(QUESTIONS_URL, source_path)
    questions = parse_questions_js(source_path)
    write_bank(questions, bank_path)

    image_names = sorted({name for q in questions for name in q.images})
    downloaded = 0
    if images:
        for name in image_names:
            target = image_dir / name
            if target.exists() and target.stat().st_size > 0:
                continue
            _download(IMAGE_BASE_URL + quote(name), target)
            downloaded += 1

    sha256 = hashlib.sha256(source_path.read_bytes()).hexdigest()
    metadata = {
        "source": QUESTIONS_URL,
        "question_count": len(questions),
        "image_reference_count": len(image_names),
        "images_downloaded": downloaded,
        "questions_js_sha256": sha256,
    }
    (data_dir / "sync_metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return metadata
