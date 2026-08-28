from __future__ import annotations

import re
import unicodedata

_PUNCT_RE = re.compile(r"[\s\u3000，。！？；：、,.!?;:'\"“”‘’（）()\[\]{}<>《》—–\-_]+")


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text or "").lower()
    return _PUNCT_RE.sub("", text)


def normalize_options(options: dict[str, str] | None) -> str:
    if not options:
        return ""
    return "|".join(f"{key.upper()}:{normalize_text(value)}" for key, value in sorted(options.items()))
