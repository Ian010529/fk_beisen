from __future__ import annotations

from dataclasses import dataclass

from rapidfuzz.fuzz import ratio

from .models import Question
from .normalize import normalize_options, normalize_text


@dataclass(slots=True)
class TextMatch:
    question_id: str
    score: float
    stem_score: float
    options_score: float


class TextMatcher:
    """Offline similarity matcher for bank QA and duplicate detection.

    It returns question IDs and similarity scores only. Local practice code may
    subsequently look up the question by ID; this module intentionally does not
    implement any browser/page automation or answer submission.
    """

    def __init__(self, questions: list[Question]):
        self.questions = questions
        self._stem = {q.id: normalize_text(q.stem) for q in questions}
        self._options = {q.id: normalize_options(q.options) for q in questions}

    def search(
        self,
        stem: str,
        options: dict[str, str] | None = None,
        *,
        limit: int = 5,
        category: str | None = None,
    ) -> list[TextMatch]:
        needle_stem = normalize_text(stem)
        needle_options = normalize_options(options)
        results: list[TextMatch] = []

        for q in self.questions:
            if category and q.category != category:
                continue
            stem_score = ratio(needle_stem, self._stem[q.id]) / 100.0 if needle_stem else 0.0
            options_score = (
                ratio(needle_options, self._options[q.id]) / 100.0
                if needle_options and self._options[q.id]
                else 0.0
            )
            if needle_options:
                score = 0.72 * stem_score + 0.28 * options_score
            else:
                score = stem_score
            results.append(TextMatch(q.id, score, stem_score, options_score))

        return sorted(results, key=lambda x: x.score, reverse=True)[: max(1, limit)]
