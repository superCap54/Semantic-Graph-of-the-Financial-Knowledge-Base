from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path


ROOT = Path.cwd()
KNOWLEDGE = ROOT / "knowledge"
RAW = KNOWLEDGE / "raw"
WIKI = KNOWLEDGE / "wiki"
INDEXES = KNOWLEDGE / "indexes"

KINDS = {
    "company": ("companies", "finance/company"),
    "industry": ("industries", "finance/industry"),
    "product": ("products", "finance/product"),
    "event": ("events", "finance/event"),
    "policy": ("policies", "finance/policy"),
}


def slug_date() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def safe_filename(value: str) -> str:
    value = re.sub(r'[<>:"/\\|?*]+', "-", value).strip()
    return re.sub(r"\s+", " ", value)[:120] or "untitled"


def ensure_dirs() -> None:
    for path in [
        RAW,
        INDEXES,
        KNOWLEDGE / "outputs",
        *(WIKI / folder for folder, _tag in KINDS.values()),
    ]:
        path.mkdir(parents=True, exist_ok=True)


def cmd_init(_args: argparse.Namespace) -> None:
    ensure_dirs()
    for name in ["companies", "industries", "products", "events", "policies", "open-questions", "health-check"]:
        path = INDEXES / f"{name}.md"
        if not path.exists():
            path.write_text(f"# {name}\n\n", encoding="utf-8")
    print(f"Initialized knowledge base at {KNOWLEDGE}")


def cmd_ingest(args: argparse.Namespace) -> None:
    ensure_dirs()
    title = args.title or f"raw-{slug_date()}"
    filename = f"{slug_date()} {safe_filename(title)}.md"
    path = RAW / filename
    captured_at = datetime.now().astimezone().isoformat(timespec="seconds")
    body = args.text
    if args.file:
        body = Path(args.file).read_text(encoding="utf-8")

    path.write_text(
        "\n".join(
            [
                "---",
                f"title: {title}",
                f"source: {args.source}",
                f"url: {args.url or ''}",
                f"captured_at: {captured_at}",
                f"query: {args.query or ''}",
                "status: raw",
                "---",
                "",
                f"# {title}",
                "",
                body or "",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(path)


def cmd_draft(args: argparse.Namespace) -> None:
    ensure_dirs()
    folder, tag = KINDS[args.kind]
    path = WIKI / folder / f"{safe_filename(args.name)}.md"
    if path.exists() and not args.force:
        print(f"Exists: {path}")
        return

    path.write_text(
        "\n".join(
            [
                "---",
                f"kind: {args.kind}",
                "aliases: []",
                "tags:",
                f"  - {tag}",
                "status: seed",
                f"updated_at: {today()}",
                "sources: []",
                "---",
                "",
                f"# {args.name}",
                "",
                "## 摘要",
                "",
                "## 关键事实",
                "",
                "## 相关公司",
                "",
                "## 相关行业",
                "",
                "## 相关产品",
                "",
                "## 相关事件",
                "",
                "## 相关政策",
                "",
                "## 来源",
                "",
                "## 待验证",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(path)


def cmd_search(args: argparse.Namespace) -> None:
    ensure_dirs()
    query = args.query.lower()
    roots = [RAW, WIKI, INDEXES]
    matches: list[tuple[Path, int, str]] = []
    for root in roots:
        for path in root.rglob("*.md"):
            try:
                lines = path.read_text(encoding="utf-8").splitlines()
            except UnicodeDecodeError:
                continue
            for idx, line in enumerate(lines, start=1):
                if query in line.lower():
                    matches.append((path, idx, line.strip()))
                    break

    for path, line_no, line in matches[: args.limit]:
        print(f"{path}:{line_no}: {line}")
    if len(matches) > args.limit:
        print(f"... {len(matches) - args.limit} more")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sgkb")
    sub = parser.add_subparsers(required=True)

    init = sub.add_parser("init", help="Create local knowledge base folders and indexes.")
    init.set_defaults(func=cmd_init)

    ingest = sub.add_parser("ingest", help="Save raw material as local markdown.")
    ingest.add_argument("--title", default="")
    ingest.add_argument("--source", default="manual")
    ingest.add_argument("--url", default="")
    ingest.add_argument("--query", default="")
    ingest.add_argument("--text", default="")
    ingest.add_argument("--file", default="")
    ingest.set_defaults(func=cmd_ingest)

    draft = sub.add_parser("draft", help="Create a wiki entry draft.")
    draft.add_argument("--kind", choices=sorted(KINDS), required=True)
    draft.add_argument("--name", required=True)
    draft.add_argument("--force", action="store_true")
    draft.set_defaults(func=cmd_draft)

    search = sub.add_parser("search", help="Search raw/wiki/index markdown files.")
    search.add_argument("query")
    search.add_argument("--limit", type=int, default=20)
    search.set_defaults(func=cmd_search)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()

