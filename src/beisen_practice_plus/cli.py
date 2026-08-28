from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from .importer import parse_questions_js, read_bank, write_bank
from .practice import run_practice
from .server import run_server
from .sync import sync_bank
from .text_matcher import TextMatcher
from .validator import validate_questions
from .vision import compare_files


def _load(path: str):
    p = Path(path)
    return parse_questions_js(p) if p.suffix == ".js" else read_bank(p)


def cmd_sync(args: argparse.Namespace) -> int:
    metadata = sync_bank(args.data_dir, images=not args.no_images)
    print(json.dumps(metadata, ensure_ascii=False, indent=2))
    return 0


def cmd_build(args: argparse.Namespace) -> int:
    questions = parse_questions_js(args.source)
    output = write_bank(questions, args.output)
    print(f"Built {len(questions)} questions -> {output}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    questions = _load(args.bank)
    issues = validate_questions(questions)
    counts = Counter(issue.severity for issue in issues)
    report = {
        "question_count": len(questions),
        "issue_count": len(issues),
        "severity": dict(counts),
        "issues": [issue.to_dict() for issue in issues],
    }
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
        print(f"Validation report -> {args.output}")
    else:
        print(text)
    return 2 if counts.get("error", 0) else 0


def cmd_search(args: argparse.Namespace) -> int:
    questions = _load(args.bank)
    matches = TextMatcher(questions).search(args.stem, limit=args.limit, category=args.category)
    for item in matches:
        print(f"{item.question_id}\t{item.score:.3f}\tstem={item.stem_score:.3f}\toptions={item.options_score:.3f}")
    return 0


def cmd_compare(args: argparse.Namespace) -> int:
    result = compare_files(args.image_a, args.image_b)
    print(json.dumps({
        "phash": round(result.phash, 4),
        "orb": round(result.orb, 4),
        "ssim": round(result.ssim, 4),
        "combined": round(result.combined, 4),
    }, indent=2))
    return 0


def cmd_practice(args: argparse.Namespace) -> int:
    return run_practice(_load(args.bank), category=args.category, count=args.count)


def cmd_serve(args: argparse.Namespace) -> int:
    run_server(args.bank, args.image_dir, host=args.host, port=args.port)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="beisen-practice")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("sync", help="Fetch the upstream question bank and referenced images")
    p.add_argument("--data-dir", default="data")
    p.add_argument("--no-images", action="store_true")
    p.set_defaults(func=cmd_sync)

    p = sub.add_parser("build-bank", help="Convert questions.js into normalized JSON")
    p.add_argument("source")
    p.add_argument("--output", default="data/question_bank.json")
    p.set_defaults(func=cmd_build)

    p = sub.add_parser("validate", help="Validate answer fields and structural problems")
    p.add_argument("bank")
    p.add_argument("--output", default="")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("search", help="Offline fuzzy search for bank QA/deduplication")
    p.add_argument("bank")
    p.add_argument("stem")
    p.add_argument("--category", choices=["verbal", "data", "graphic"])
    p.add_argument("--limit", type=int, default=5)
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("compare-images", help="Compare two local images perceptually")
    p.add_argument("image_a")
    p.add_argument("image_b")
    p.set_defaults(func=cmd_compare)

    p = sub.add_parser("practice", help="Run a local interactive practice session")
    p.add_argument("bank")
    p.add_argument("--category", choices=["verbal", "data", "graphic"])
    p.add_argument("--count", type=int, default=10)
    p.set_defaults(func=cmd_practice)

    p = sub.add_parser("serve", help="Run the local browser-extension matching service")
    p.add_argument("--bank", default="../beisen/src/data/questions.js")
    p.add_argument("--image-dir", default="../beisen/public/question-bank")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.set_defaults(func=cmd_serve)

    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
