from __future__ import annotations

import re
from collections import Counter
from dataclasses import asdict, dataclass

from .models import Question

_ANSWER_IN_ANALYSIS = re.compile(r"正确答案\s*[:：]\s*([A-E])", re.I)


@dataclass(slots=True)
class ValidationIssue:
    question_id: str
    severity: str
    code: str
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def validate_questions(questions: list[Question]) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    seen: Counter[str] = Counter(q.id for q in questions)

    for qid, count in seen.items():
        if count > 1:
            issues.append(ValidationIssue(qid, "error", "duplicate_id", f"ID appears {count} times"))

    for q in questions:
        if not q.stem.strip():
            issues.append(ValidationIssue(q.id, "error", "empty_stem", "Question stem is empty"))
        if set(q.options) != {"A", "B", "C", "D"}:
            issues.append(
                ValidationIssue(q.id, "warning", "option_shape", f"Expected A-D options, got {sorted(q.options)}")
            )
        if q.answer is None:
            issues.append(ValidationIssue(q.id, "error", "missing_answer", "Answer field is missing"))
        elif q.answer not in q.options:
            issues.append(
                ValidationIssue(q.id, "error", "invalid_answer", f"Answer {q.answer!r} is not present in options")
            )

        match = _ANSWER_IN_ANALYSIS.search(f"{q.stem}\n{q.analysis}")
        if match and q.answer and match.group(1).upper() != q.answer:
            issues.append(
                ValidationIssue(
                    q.id,
                    "warning",
                    "answer_analysis_conflict",
                    f"answer={q.answer}, analysis says {match.group(1).upper()}",
                )
            )

        if q.category == "graphic" and not q.images:
            issues.append(ValidationIssue(q.id, "warning", "graphic_without_image", "Graphic question has no image"))

    return issues
