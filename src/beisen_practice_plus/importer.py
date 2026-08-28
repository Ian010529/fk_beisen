from __future__ import annotations

import json
from pathlib import Path

from .models import Question


def parse_questions_js(path: str | Path) -> list[Question]:
    """Parse BeiSen_Practice/src/data/questions.js.

    The upstream file stores each question object on a single line as valid JSON,
    inside a JavaScript array. This parser deliberately ignores the surrounding
    JS metadata and only consumes question-object lines.
    """
    path = Path(path)
    questions: list[Question] = []
    errors: list[str] = []

    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        text = line.strip().rstrip(",")
        if not text.startswith('{"id":'):
            continue
        try:
            raw = json.loads(text)
        except json.JSONDecodeError as exc:
            errors.append(f"line {line_no}: {exc}")
            continue
        questions.append(Question.from_dict(raw))

    if errors:
        preview = "\n".join(errors[:8])
        raise ValueError(f"Failed to parse {len(errors)} question lines:\n{preview}")
    if not questions:
        raise ValueError(f"No question objects found in {path}")
    return questions


def write_bank(questions: list[Question], output: str | Path) -> Path:
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema_version": 1,
        "count": len(questions),
        "questions": [q.to_dict() for q in questions],
    }
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def read_bank(path: str | Path) -> list[Question]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    raw_questions = payload.get("questions", payload if isinstance(payload, list) else [])
    return [Question.from_dict(item) for item in raw_questions]
