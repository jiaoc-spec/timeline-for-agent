#!/usr/bin/env python3
"""Append Markdown to an Obsidian daily note."""

from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import date
from pathlib import Path


DEFAULT_VAULT = "/Users/jiaocheng/Library/Mobile Documents/iCloud~md~obsidian/Documents/Jiao's Obsidian"
DEFAULT_DAILY_FOLDER = "03. 🔵 Tagebuch/01. 日记"
DEFAULT_SECTION = "## 今日记录"


def main() -> int:
    args = parse_args()
    target_date = resolve_date(args.date)
    vault = Path(args.vault or os.environ.get("OBSIDIAN_VAULT_DIR") or DEFAULT_VAULT).expanduser()
    daily_folder = args.daily_folder or os.environ.get("OBSIDIAN_DAILY_FOLDER") or DEFAULT_DAILY_FOLDER
    section = args.section or os.environ.get("OBSIDIAN_DAILY_SECTION") or DEFAULT_SECTION
    note_path = vault / daily_folder / f"{target_date}.md"
    entry = read_entry(args)

    if not entry.strip():
        raise SystemExit("No entry text provided. Use --text or --stdin.")

    updated = append_entry(read_existing(note_path), target_date, section, entry)

    if args.dry_run:
        print(f"target: {note_path}")
        print(updated, end="" if updated.endswith("\n") else "\n")
        return 0

    note_path.parent.mkdir(parents=True, exist_ok=True)
    note_path.write_text(updated, encoding="utf-8")
    print(f"updated: {note_path}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append Markdown to an Obsidian daily note.")
    parser.add_argument("--date", help="Daily note date in YYYY-MM-DD format. Defaults to today.")
    parser.add_argument("--vault", help="Obsidian vault root. Defaults to OBSIDIAN_VAULT_DIR or Jiao's vault.")
    parser.add_argument("--daily-folder", help="Folder inside the vault for daily notes.")
    parser.add_argument("--section", help="Markdown heading to append under.")
    parser.add_argument("--text", help="Markdown text to append.")
    parser.add_argument("--stdin", action="store_true", help="Read Markdown text from stdin.")
    parser.add_argument("--dry-run", action="store_true", help="Print the resulting note without writing.")
    return parser.parse_args()


def resolve_date(value: str | None) -> str:
    if not value:
        return date.today().isoformat()
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise SystemExit(f"Invalid --date {value!r}; expected YYYY-MM-DD.")
    return value


def read_entry(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    if args.stdin:
        return sys.stdin.read()
    if not sys.stdin.isatty():
        return sys.stdin.read()
    return ""


def read_existing(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def append_entry(existing: str, target_date: str, section: str, entry: str) -> str:
    text = existing.rstrip()
    if not text:
        text = f"# {target_date}"

    section = section.strip()
    entry = entry.strip()

    if not has_heading(text, section):
        text = f"{text}\n\n{section}"

    return f"{text}\n\n{entry}\n"


def has_heading(markdown: str, heading: str) -> bool:
    escaped = re.escape(heading.strip())
    return re.search(rf"(?m)^{escaped}\s*$", markdown) is not None


if __name__ == "__main__":
    raise SystemExit(main())
