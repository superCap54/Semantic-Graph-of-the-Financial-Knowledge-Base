from __future__ import annotations

import argparse
import re
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path.cwd()
RAW = ROOT / "raw"
INDEX = ROOT / "索引"

KIND_DIRS = {
    "company": "公司",
    "industry": "行业",
    "event": "事件",
    "policy": "政策",
    "product": "产品",
}

KIND_TAGS = {
    "company": "finance/company",
    "industry": "finance/industry",
    "event": "finance/event",
    "policy": "finance/policy",
    "product": "finance/product",
}


def now_slug() -> str:
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def today() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def safe_filename(value: str) -> str:
    value = re.sub(r'[<>:"/\\|?*]+', "-", value).strip()
    return re.sub(r"\s+", " ", value)[:140] or "untitled"


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    parts = text.split("---\n", 2)
    if len(parts) == 3:
        return parts[2]
    return text


def extract_frontmatter_value(text: str, key: str) -> str:
    if not text.startswith("---\n"):
        return ""
    header = text.split("---\n", 2)[1]
    for line in header.splitlines():
        if line.startswith(f"{key}:"):
            return line.split(":", 1)[1].strip()
    return ""


def parse_horizon_items(text: str) -> list[dict[str, str]]:
    body = strip_frontmatter(text)
    pattern = re.compile(
        r'<a id="(?P<id>item-\d+)"></a>\s*\n'
        r'## \[(?P<title>[^\]]+)\]\((?P<url>[^)]+)\)\s*⭐️\s*(?P<score>[\d.]+)/10\s*\n\n'
        r'(?P<body>.*?)(?=\n---\n\n<a id="item-\d+"></a>|\n---\s*$|\Z)',
        re.DOTALL,
    )
    items = []
    for match in pattern.finditer(body):
        item_body = match.group("body").strip()
        source_line = ""
        summary_lines = []
        for line in item_body.splitlines():
            if re.match(r"^[\w\\_]+ · .+ · .+", line):
                source_line = line.replace("\\_", "_")
                break
            summary_lines.append(line)
        summary = "\n".join(summary_lines).strip()
        background = ""
        background_match = re.search(r"\*\*背景\*\*:\s*(.*?)(?=\n\n<details>|\n\n\*\*标签\*\*:|\Z)", item_body, re.DOTALL)
        if background_match:
            background = background_match.group(1).strip()
        tags = ""
        tags_match = re.search(r"\*\*标签\*\*:\s*(.*)", item_body)
        if tags_match:
            tags = tags_match.group(1).strip()
        items.append(
            {
                "id": match.group("id"),
                "title": match.group("title").strip(),
                "url": match.group("url").strip(),
                "horizon_score": match.group("score").strip(),
                "summary": summary,
                "source_line": source_line,
                "background": background,
                "tags": tags,
                "raw_body": item_body,
            }
        )
    return items


def source_name_from_item(item: dict[str, str]) -> str:
    parts = [p.strip() for p in item.get("source_line", "").split("·")]
    if len(parts) >= 2 and parts[1]:
        return parts[1]
    host = urlparse(item["url"]).hostname or ""
    return host.removeprefix("www.") or "unknown"


def ensure_dirs() -> None:
    for path in [
        RAW / "horizon-reports",
        RAW / "news",
        RAW / "announcements",
        RAW / "policies",
        RAW / "reports",
        ROOT / "日报",
        ROOT / "周报",
        INDEX,
        *(ROOT / folder for folder in KIND_DIRS.values()),
    ]:
        path.mkdir(parents=True, exist_ok=True)


def wiki_name(kind: str, name: str, ticker: str = "") -> str:
    if kind == "company" and ticker:
        return f"{name}（{ticker}）"
    return name


def cmd_init(_args: argparse.Namespace) -> None:
    ensure_dirs()
    for name in ["公司索引", "行业索引", "事件索引", "政策索引", "产品索引", "健康检查"]:
        path = INDEX / f"{name}.md"
        if not path.exists():
            path.write_text(f"# {name}\n\n", encoding="utf-8")
    print(f"Initialized vault at {ROOT}")


def cmd_watchlist_template(_args: argparse.Namespace) -> None:
    path = ROOT / "config" / "watchlist.yaml"
    if path.exists():
        print(f"Exists: {path}")
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "targets:",
                "  - name: 华大基因",
                "    type: company",
                "    ticker: 300676.SZ",
                "    aliases:",
                "      - BGI Genomics",
                "      - 华大",
                "    tracking_scope:",
                "      breadth: broad",
                "      include:",
                "        - company_news",
                "        - announcements",
                "        - financial_reports",
                "        - industry_news",
                "        - policies",
                "        - products",
                "        - competitors",
                "        - upstream_downstream",
                "        - social_discussion",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(path)


def cmd_ingest(args: argparse.Namespace) -> None:
    ensure_dirs()
    title = args.title or f"raw-{now_slug()}"
    raw_type = args.raw_type
    folder = RAW / raw_type
    filename = f"{now_slug()} {safe_filename(title)}.md"
    path = folder / filename
    captured_at = datetime.now().astimezone().isoformat(timespec="seconds")
    body = args.text
    if args.file:
        body = Path(args.file).read_text(encoding="utf-8")

    path.write_text(
        "\n".join(
            [
                "---",
                f"source_adapter: {args.source_adapter}",
                f"query: {args.query}",
                f"title: {title}",
                f"url: {args.url}",
                f"captured_at: {captured_at}",
                f"source_tier: {args.source_tier}",
                f"evidence_type: {args.evidence_type}",
                "status: raw",
                "---",
                "",
                f"# {title}",
                "",
                "## 摘要",
                "",
                body or "",
                "",
                "## 关键摘录",
                "",
                "## 来源",
                "",
                f"- 原文链接：{args.url}",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(path)


def cmd_import_horizon(args: argparse.Namespace) -> None:
    ensure_dirs()
    source = Path(args.file)
    if not source.exists():
        raise FileNotFoundError(source)

    report_date = args.date or today()
    query = args.query or "未命名查询"
    filename = f"{report_date} {safe_filename(query)} Horizon报告.md"
    target = RAW / "horizon-reports" / filename
    body = source.read_text(encoding=args.encoding)
    captured_at = datetime.now().astimezone().isoformat(timespec="seconds")

    target.write_text(
        "\n".join(
            [
                "---",
                "source_adapter: horizon",
                f"query: {query}",
                f"source_file: {source}",
                f"captured_at: {captured_at}",
                "status: imported",
                "---",
                "",
                body,
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(target)


def cmd_split_horizon(args: argparse.Namespace) -> None:
    ensure_dirs()
    report = Path(args.report)
    if not report.exists():
        raise FileNotFoundError(report)

    text = report.read_text(encoding=args.encoding)
    query = args.query or extract_frontmatter_value(text, "query")
    report_name = report.stem
    report_date = args.date or (re.match(r"\d{4}-\d{2}-\d{2}", report.name).group(0) if re.match(r"\d{4}-\d{2}-\d{2}", report.name) else today())
    items = parse_horizon_items(text)
    output_paths = []

    for idx, item in enumerate(items, start=1):
        filename = f"{report_date} {safe_filename(item['title'])}.md"
        target = RAW / "news" / filename
        if target.exists() and not args.force:
            output_paths.append(target)
            continue
        source_name = source_name_from_item(item)
        captured_at = datetime.now().astimezone().isoformat(timespec="seconds")
        target.write_text(
            "\n".join(
                [
                    "---",
                    "source_adapter: horizon",
                    f"query: {query}",
                    f"title: {item['title']}",
                    f"url: {item['url']}",
                    f"source_name: {source_name}",
                    f"horizon_item_id: {item['id']}",
                    f"horizon_score: {item['horizon_score']}",
                    f"source_report: {report_name}",
                    f"captured_at: {captured_at}",
                    "source_tier: unknown",
                    "evidence_type: news",
                    "status: raw",
                    "---",
                    "",
                    f"# {item['title']}",
                    "",
                    "## 摘要",
                    "",
                    item["summary"],
                    "",
                    "## 背景",
                    "",
                    item["background"],
                    "",
                    "## Horizon 评分",
                    "",
                    f"- Horizon 评分：{item['horizon_score']}/10",
                    "",
                    "## 标签",
                    "",
                    item["tags"],
                    "",
                    "## 来源",
                    "",
                    f"- Horizon 报告：[[{report_name}]]",
                    f"- 原文链接：{item['url']}",
                    f"- 来源信息：{item['source_line']}",
                    "",
                ]
            ),
            encoding="utf-8",
        )
        output_paths.append(target)

    print(f"Split {len(items)} items from {report}")
    for path in output_paths:
        print(path)


def cmd_draft(args: argparse.Namespace) -> None:
    ensure_dirs()
    folder = ROOT / KIND_DIRS[args.kind]
    display_name = wiki_name(args.kind, args.name, args.ticker)
    path = folder / f"{safe_filename(display_name)}.md"
    if path.exists() and not args.force:
        print(f"Exists: {path}")
        return

    path.write_text(
        "\n".join(
            [
                "---",
                f"kind: {args.kind}",
                f"name: {args.name}",
                f"ticker: {args.ticker}",
                "aliases: []",
                "tags:",
                f"  - {KIND_TAGS[args.kind]}",
                "status: seed",
                f"updated_at: {today()}",
                "sources: []",
                "---",
                "",
                f"# {display_name}",
                "",
                "## 基础信息",
                "",
                "## 关键关系",
                "",
                "## 事件时间线",
                "",
                "## 分析日志",
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
    roots = [RAW, INDEX, *(ROOT / folder for folder in KIND_DIRS.values()), ROOT / "日报", ROOT / "周报"]
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

    init = sub.add_parser("init", help="Create vault folders and indexes.")
    init.set_defaults(func=cmd_init)

    watchlist = sub.add_parser("watchlist-template", help="Create config/watchlist.yaml from the sample target.")
    watchlist.set_defaults(func=cmd_watchlist_template)

    ingest = sub.add_parser("ingest", help="Save raw material as local markdown.")
    ingest.add_argument("--title", default="")
    ingest.add_argument("--raw-type", choices=["horizon-reports", "news", "announcements", "policies", "reports"], default="news")
    ingest.add_argument("--source-adapter", default="manual")
    ingest.add_argument("--source-tier", default="unknown")
    ingest.add_argument("--evidence-type", default="news")
    ingest.add_argument("--url", default="")
    ingest.add_argument("--query", default="")
    ingest.add_argument("--text", default="")
    ingest.add_argument("--file", default="")
    ingest.set_defaults(func=cmd_ingest)

    horizon = sub.add_parser("import-horizon", help="Import a Horizon markdown report into raw/horizon-reports.")
    horizon.add_argument("file")
    horizon.add_argument("--query", default="")
    horizon.add_argument("--date", default="")
    horizon.add_argument("--encoding", default="utf-8")
    horizon.set_defaults(func=cmd_import_horizon)

    split_horizon = sub.add_parser("split-horizon", help="Split an imported Horizon report into raw/news cards.")
    split_horizon.add_argument("report")
    split_horizon.add_argument("--query", default="")
    split_horizon.add_argument("--date", default="")
    split_horizon.add_argument("--encoding", default="utf-8")
    split_horizon.add_argument("--force", action="store_true")
    split_horizon.set_defaults(func=cmd_split_horizon)

    draft = sub.add_parser("draft", help="Create a wiki node draft.")
    draft.add_argument("--kind", choices=sorted(KIND_DIRS), required=True)
    draft.add_argument("--name", required=True)
    draft.add_argument("--ticker", default="")
    draft.add_argument("--force", action="store_true")
    draft.set_defaults(func=cmd_draft)

    search = sub.add_parser("search", help="Search markdown files in the vault.")
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
