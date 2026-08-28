from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np
from rapidfuzz.fuzz import WRatio

from .models import Question
from .text_matcher import TextMatch, TextMatcher
from .vision import compare_arrays, load_gray, phash_bits


@dataclass(slots=True)
class ImageMatch:
    question_ids: tuple[str, ...]
    filename: str
    score: float


class ImageMatcher:
    """Two-stage local image search: pHash recall, then ORB/SSIM reranking."""

    def __init__(self, questions: list[Question], image_dir: str | Path):
        self.image_dir = Path(image_dir)
        self._questions_by_file: dict[str, list[str]] = {}
        self._hashes: dict[str, np.ndarray] = {}

        for question in questions:
            for filename in question.images:
                path = self.image_dir / filename
                if not path.is_file():
                    continue
                self._questions_by_file.setdefault(filename, []).append(question.id)
                if filename in self._hashes:
                    continue
                data = np.fromfile(str(path), dtype=np.uint8)
                gray = cv2.imdecode(data, cv2.IMREAD_REDUCED_GRAYSCALE_4)
                if gray is None:
                    continue
                self._hashes[filename] = phash_bits(gray)

    @property
    def image_count(self) -> int:
        return len(self._hashes)

    def search(self, images: Iterable[bytes], *, shortlist: int = 8) -> ImageMatch | None:
        best: ImageMatch | None = None
        for payload in images:
            array = np.frombuffer(payload, dtype=np.uint8)
            query = cv2.imdecode(array, cv2.IMREAD_GRAYSCALE)
            if query is None:
                continue
            query_hash = phash_bits(query)
            candidates = sorted(
                self._hashes,
                key=lambda name: int(np.count_nonzero(query_hash != self._hashes[name])),
            )[:shortlist]
            for filename in candidates:
                score = compare_arrays(query, load_gray(self.image_dir / filename)).combined
                candidate = ImageMatch(tuple(self._questions_by_file[filename]), filename, score)
                if best is None or candidate.score > best.score:
                    best = candidate
        return best


class QuestionMatcher:
    def __init__(self, questions: list[Question], image_dir: str | Path):
        self.questions = questions
        self.by_id = {question.id: question for question in questions}
        self.text = TextMatcher(questions)
        self.images = ImageMatcher(questions, image_dir)

    def match(
        self,
        stem: str,
        options: list[str],
        image_payloads: Iterable[bytes] = (),
    ) -> dict[str, object] | None:
        option_map = {chr(65 + index): value for index, value in enumerate(options)}
        text_matches = self.text.search(stem, option_map, limit=8)
        image_match = self.images.search(image_payloads)
        selected, method, confidence = self._select(text_matches, image_match)
        if selected is None:
            return None

        question = self.by_id[selected]
        answer_key = question.answer or ""
        answer_text = question.options.get(answer_key, "")
        page_index, page_text, option_score = self._map_option(answer_key, answer_text, options)
        return {
            "question_id": question.id,
            "category": question.category,
            "method": method,
            "confidence": round(confidence, 4),
            "stem": question.stem,
            "answer_key": answer_key,
            "answer_text": answer_text,
            "page_option_index": page_index,
            "page_option_text": page_text,
            "option_confidence": round(option_score, 4),
            "image": image_match.filename if image_match and question.id in image_match.question_ids else "",
        }

    @staticmethod
    def _select(
        text_matches: list[TextMatch], image_match: ImageMatch | None
    ) -> tuple[str | None, str, float]:
        text_top = text_matches[0] if text_matches else None
        text_margin = text_top.score - text_matches[1].score if len(text_matches) > 1 else 1.0
        image_text = next(
            (match for match in text_matches if image_match and match.question_id in image_match.question_ids),
            None,
        )

        if image_match and image_text and image_text.score >= 0.20:
            return image_text.question_id, "text+image", max(image_text.score, image_match.score)
        if text_top and text_top.score >= 0.78 and text_margin >= 0.04:
            return text_top.question_id, "text", text_top.score
        if image_match and image_match.score >= 0.72 and len(image_match.question_ids) == 1:
            return image_match.question_ids[0], "image", image_match.score
        if text_top and text_top.score >= 0.55:
            return text_top.question_id, "text-low-confidence", text_top.score
        return None, "none", 0.0

    @staticmethod
    def _map_option(answer_key: str, answer_text: str, options: list[str]) -> tuple[int | None, str, float]:
        if not options:
            return None, "", 0.0
        scores = [WRatio(answer_text, option) / 100.0 if answer_text else 0.0 for option in options]
        best_index = max(range(len(scores)), key=scores.__getitem__)
        if scores[best_index] >= 0.55:
            return best_index, options[best_index], scores[best_index]
        fallback = ord(answer_key) - ord("A") if answer_key else -1
        if 0 <= fallback < len(options):
            return fallback, options[fallback], scores[fallback]
        return None, "", 0.0
