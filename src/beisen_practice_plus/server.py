from __future__ import annotations

import base64
import binascii
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .codex_answerer import CodexAnswerer
from .importer import parse_questions_js, read_bank
from .question_matcher import QuestionMatcher


def load_questions(path: str | Path):
    path = Path(path)
    return parse_questions_js(path) if path.suffix == ".js" else read_bank(path)


def decode_images(raw_images: list[Any]) -> list[bytes]:
    decoded: list[bytes] = []
    for item in raw_images[:6]:
        value = item.get("data", "") if isinstance(item, dict) else str(item)
        if not value:
            continue
        encoded = value.split(",", 1)[1] if value.startswith("data:") and "," in value else value
        try:
            payload = base64.b64decode(encoded, validate=True)
        except (ValueError, binascii.Error):
            continue
        if 0 < len(payload) <= 8 * 1024 * 1024:
            decoded.append(payload)
    return decoded


def make_handler(matcher: QuestionMatcher, codex: CodexAnswerer | None = None):
    class Handler(BaseHTTPRequestHandler):
        def do_OPTIONS(self):
            self.send_response(204)
            self._cors_headers()
            self.end_headers()

        def do_GET(self):
            if self.path != "/health":
                self._json(404, {"error": "not found"})
                return
            self._json(200, {
                "status": "ok",
                "questions": len(matcher.questions),
                "images": matcher.images.image_count,
                "codex": bool(codex and codex.available),
            })

        def do_POST(self):
            if self.path != "/match":
                self._json(404, {"error": "not found"})
                return
            try:
                length = int(self.headers.get("Content-Length", "0"))
                if length <= 0 or length > 50 * 1024 * 1024:
                    raise ValueError("invalid request size")
                body = json.loads(self.rfile.read(length))
                stem = str(body.get("stem", ""))
                options = [str(value) for value in body.get("options", [])][:8]
                images = decode_images(body.get("images", []))
                if body.get("use_codex"):
                    if not codex:
                        raise RuntimeError("Codex 回答器未配置")
                    result = codex.answer(stem, options, images)
                else:
                    result = matcher.match(stem, options, images)
                self._json(200, {"match": result})
            except (ValueError, TypeError, json.JSONDecodeError) as exc:
                self._json(400, {"error": str(exc)})
            except RuntimeError as exc:
                self._json(502, {"error": str(exc)})

        def log_message(self, format, *args):
            print(f"[matcher] {self.address_string()} {format % args}")

        def _cors_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")

        def _json(self, status: int, payload: dict[str, Any]):
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self._cors_headers()
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    return Handler


def run_server(bank: str | Path, image_dir: str | Path, host: str = "127.0.0.1", port: int = 8765):
    questions = load_questions(bank)
    matcher = QuestionMatcher(questions, image_dir)
    codex = CodexAnswerer()
    server = ThreadingHTTPServer((host, port), make_handler(matcher, codex))
    print(f"Loaded {len(questions)} questions and {matcher.images.image_count} referenced images")
    print(f"Codex CLI: {'available' if codex.available else 'unavailable'}")
    print(f"Matcher service: http://{host}:{port}")
    server.serve_forever()
