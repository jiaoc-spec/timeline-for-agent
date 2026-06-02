---
name: obsidian-daily-timeline
description: Record conversational daily-life updates into an Obsidian daily note and optionally mirror structured time-block events into timeline-for-agent. Use when the user says what they did today/yesterday/on a date, asks Codex to remember or log a day, wants notes sent to Obsidian, or wants daily diary content plus timeline data.
---

# Obsidian Daily Timeline

Use this skill to turn the user's conversational day report into a durable Obsidian daily-note entry. Obsidian is the primary destination; `timeline-for-agent` is optional and should be used only when the user asks for timeline/dashboard data or gives enough event timing to structure it safely.

## Default Targets

- Vault: `/Users/jiaocheng/Library/Mobile Documents/iCloud~md~obsidian/Documents/Jiao's Obsidian`
- Daily folder: `03. 🔵 Tagebuch/01. 日记`
- Daily filename: `YYYY-MM-DD.md`
- Default section: `## 今日记录`

These can be overridden with script flags or environment variables.

## Workflow

1. Resolve the date from the user's wording and the current conversation date. Use exact dates in commands.
2. Convert the user's report into concise Markdown. Preserve concrete details, names, links, decisions, and emotional/physical state. Do not invent times, durations, categories, or outcomes.
3. Append the Markdown to the Obsidian daily note with `scripts/append_daily_note.py`.
4. If the user also wants timeline data, or the update contains clear start/end times, use the project CLI after the Obsidian write:
   - Run `timeline-for-agent categories` when category or eventNode choice is unclear.
   - Run `timeline-for-agent read --date YYYY-MM-DD` before modifying existing events.
   - Run `timeline-for-agent write --date YYYY-MM-DD --stdin` with valid event JSON.
5. Report the note path and whether timeline data was also written.

## Obsidian Write

Prefer the bundled script instead of manually editing the note:

```bash
python3 .codex/skills/obsidian-daily-timeline/scripts/append_daily_note.py \
  --date 2026-06-02 \
  --stdin <<'EOF'
- Worked on the timeline-for-agent Obsidian logging skill.
- Decided Obsidian daily notes are the primary memory surface; timeline data is optional.
EOF
```

Useful flags:

- `--date YYYY-MM-DD`: target daily note.
- `--section "## 今日记录"`: heading to append under.
- `--vault PATH`: Obsidian vault root.
- `--daily-folder PATH`: folder inside the vault.
- `--dry-run`: print the target path and resulting note without writing.

Environment overrides:

- `OBSIDIAN_VAULT_DIR`
- `OBSIDIAN_DAILY_FOLDER`
- `OBSIDIAN_DAILY_SECTION`

When the vault is outside the writable sandbox, request filesystem approval rather than trying to work around permissions.

## Timeline Mirroring

Mirror to `timeline-for-agent` only when it adds value. The daily note can accept fuzzy natural language, but timeline events need precise, valid data.

Do not create timeline events when:

- The user only gives a broad summary with no time range.
- The classification is unclear and categories have not been checked.
- An event crosses midnight and has not been split.

When mirroring, follow the existing project instructions in `docs/agent-instructions.md`: use CLI commands first, do not edit raw JSON directly, and keep events inside the target date.
