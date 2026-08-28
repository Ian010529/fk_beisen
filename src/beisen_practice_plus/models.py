from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class Question:
    id: str
    stem: str
    options: dict[str, str]
    answer: str | None = None
    analysis: str = ""
    tag: str = ""
    images: list[str] = field(default_factory=list)
    category: str = "unknown"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "Question":
        qid = str(raw.get("id", ""))
        return cls(
            id=qid,
            stem=str(raw.get("stem", "")),
            options={str(k): str(v) for k, v in (raw.get("options") or {}).items()},
            answer=(str(raw["answer"]).upper() if raw.get("answer") is not None else None),
            analysis=str(raw.get("analysis", "")),
            tag=str(raw.get("tag", "")),
            images=[str(x) for x in (raw.get("images") or [])],
            category=category_from_id(qid),
        )


def category_from_id(qid: str) -> str:
    if qid.startswith("v-"):
        return "verbal"
    if qid.startswith("d-"):
        return "data"
    if qid.startswith("g-"):
        return "graphic"
    return "unknown"
