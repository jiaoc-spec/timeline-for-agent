#!/usr/bin/env python3
"""Append Markdown to an Obsidian daily note."""

from __future__ import annotations

import argparse
import os
import re
import shutil
import sys
from datetime import date
from pathlib import Path


DEFAULT_VAULT = "/Users/jiaocheng/Library/Mobile Documents/iCloud~md~obsidian/Documents/Jiao's Obsidian"
DEFAULT_DAILY_FOLDER = "03. 🔵 Tagebuch/01. 日记"
DEFAULT_SECTION = "## 今日记录"
DEFAULT_ATTACHMENT_FOLDER = "资料库/附件"
DEFAULT_IMAGE_SECTION = "## 时间轴报表"
DEFAULT_DATA_SECTION = "## 时间轴数据"


def main() -> int:
    args = parse_args()
    target_date = resolve_date(args.date)
    vault = Path(args.vault or os.environ.get("OBSIDIAN_VAULT_DIR") or DEFAULT_VAULT).expanduser()
    daily_folder = args.daily_folder or os.environ.get("OBSIDIAN_DAILY_FOLDER") or DEFAULT_DAILY_FOLDER
    section = args.section or os.environ.get("OBSIDIAN_DAILY_SECTION") or DEFAULT_SECTION
    attachment_folder = (
        args.attachment_folder
        or os.environ.get("OBSIDIAN_ATTACHMENT_FOLDER")
        or DEFAULT_ATTACHMENT_FOLDER
    )
    note_path = vault / daily_folder / f"{target_date}.md"
    entry = read_entry(args)
    image_embeds = copy_images(vault, attachment_folder, target_date, args.images, args.dry_run)
    data_block = read_data_block(args)

    if not entry.strip() and not image_embeds and not data_block.strip():
        raise SystemExit("No content provided. Use --text, --stdin, --image, --data-file, or --data-json.")

    updated = update_note(
        read_existing(note_path),
        target_date,
        section,
        entry,
        args.image_section,
        image_embeds,
        args.data_section,
        data_block,
    )

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
    parser.add_argument("--image-section", default=DEFAULT_IMAGE_SECTION, help="Markdown heading for image embeds.")
    parser.add_argument("--data-section", default=DEFAULT_DATA_SECTION, help="Markdown heading for data blocks.")
    parser.add_argument("--attachment-folder", help="Folder inside the vault for copied images.")
    parser.add_argument("--text", help="Markdown text to append.")
    parser.add_argument("--image", dest="images", action="append", default=[], help="Report image to copy and embed.")
    parser.add_argument("--data-file", help="File whose contents should be appended as a fenced data block.")
    parser.add_argument("--data-json", help="JSON/text to append as a fenced data block.")
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


def update_note(
    existing: str,
    target_date: str,
    entry_section: str,
    entry: str,
    image_section: str,
    image_embeds: list[str],
    data_section: str,
    data_block: str,
) -> str:
    text = existing.rstrip()
    if not text:
        text = f"# {target_date}"

    if entry.strip():
        text = append_to_section(text, entry_section, entry)
    if image_embeds:
        text = append_to_section(text, image_section, "\n".join(image_embeds))
    if data_block.strip():
        text = append_to_section(text, data_section, data_block)

    return f"{text.rstrip()}\n"


def append_to_section(markdown: str, section: str, content: str) -> str:
    text = markdown.rstrip()
    section = section.strip()
    content = content.strip()
    if not has_heading(text, section):
        text = f"{text}\n\n{section}"
    return f"{text}\n\n{content}"


def copy_images(
    vault: Path,
    attachment_folder: str,
    target_date: str,
    images: list[str],
    dry_run: bool,
) -> list[str]:
    embeds = []
    attachment_dir = vault / attachment_folder
    for index, image in enumerate(images, start=1):
        source = Path(image).expanduser()
        if not source.exists():
            raise SystemExit(f"Image not found: {source}")
        if not source.is_file():
            raise SystemExit(f"Image path is not a file: {source}")
        suffix = source.suffix.lower() or ".png"
        stem = safe_stem(source.stem) or f"report-{index}"
        target = unique_path(attachment_dir / f"timeline-{target_date}-{stem}{suffix}")
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        embeds.append(f"![[{to_vault_relative(target, vault)}]]")
    return embeds


def read_data_block(args: argparse.Namespace) -> str:
    data = ""
    if args.data_file:
        data = Path(args.data_file).expanduser().read_text(encoding="utf-8")
    if args.data_json:
        data = f"{data.rstrip()}\n\n{args.data_json}".strip() if data else args.data_json
    data = data.strip()
    if not data:
        return ""
    fence = "json" if looks_like_json(data) else ""
    return f"```{fence}\n{data}\n```"


def safe_stem(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", value).strip("-._")


def unique_path(path: Path) -> Path:
    if not path.exists():
        return path
    for index in range(2, 1000):
        candidate = path.with_name(f"{path.stem}-{index}{path.suffix}")
        if not candidate.exists():
            return candidate
    raise SystemExit(f"Could not find a free filename near: {path}")


def to_vault_relative(path: Path, vault: Path) -> str:
    try:
        return path.resolve().relative_to(vault.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def looks_like_json(data: str) -> bool:
    stripped = data.lstrip()
    return stripped.startswith("{") or stripped.startswith("[")


def has_heading(markdown: str, heading: str) -> bool:
    escaped = re.escape(heading.strip())
    return re.search(rf"(?m)^{escaped}\s*$", markdown) is not None


if __name__ == "__main__":
    raise SystemExit(main())
