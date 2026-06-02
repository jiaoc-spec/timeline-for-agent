---
name: obsidian-daily-timeline
description: Record conversational daily-life updates into an Obsidian daily note and optionally mirror structured time-block events into timeline-for-agent. Use when the user says what they did today/yesterday/on a date, asks Codex to remember or log a day, wants notes sent to Obsidian, or wants daily diary content plus timeline data.
---

# Obsidian Daily Timeline

Use this skill to turn the user's conversational day report into a durable Obsidian daily-note entry with optional `timeline-for-agent` report screenshots and structured data. Obsidian is the primary destination; `timeline-for-agent` supplies the visual reports and optional time-block data.

## Default Targets

- Vault: `/Users/jiaocheng/Library/Mobile Documents/iCloud~md~obsidian/Documents/Jiao's Obsidian`
- Daily folder: `03. 🔵 Tagebuch/01. 日记`
- Daily filename: `YYYY-MM-DD.md`
- Default section: `## 今日记录`
- Attachment folder: `资料库/附件`
- Report section: `## 时间轴报表`
- Data section: `## 时间轴数据`

These can be overridden with script flags or environment variables.

## Workflow

1. Resolve the date from the user's wording and the current conversation date. Use exact dates in commands.
2. Convert the user's report into concise Markdown. Preserve concrete details, names, links, decisions, and emotional/physical state. Do not invent times, durations, categories, or outcomes.
3. If the user wants the designed report visuals, first generate one or more timeline screenshots with `timeline-for-agent screenshot`.
4. Append the Markdown, report image embeds, and optional data block to the Obsidian daily note with `scripts/append_daily_note.py`.
5. If the user also wants timeline data, or the update contains clear start/end times, use the project CLI before generating final screenshots:
   - Run `timeline-for-agent categories` when category or eventNode choice is unclear.
   - Run `timeline-for-agent read --date YYYY-MM-DD` before modifying existing events.
   - Run `timeline-for-agent write --date YYYY-MM-DD --stdin` with valid event JSON.
6. Report the note path, copied image path(s), and whether timeline data was also written.

## Obsidian Write

Prefer the bundled script instead of manually editing the note.

Text-only entry:

```bash
python3 .codex/skills/obsidian-daily-timeline/scripts/append_daily_note.py \
  --date 2026-06-02 \
  --stdin <<'EOF'
- Worked on the timeline-for-agent Obsidian logging skill.
- Decided Obsidian daily notes are the primary memory surface; timeline data is optional.
EOF
```

Entry with report images and a data file:

```bash
timeline-for-agent screenshot \
  --range day \
  --date 2026-06-02 \
  --selector main \
  --output /tmp/timeline-2026-06-02-main.png

python3 .codex/skills/obsidian-daily-timeline/scripts/append_daily_note.py \
  --date 2026-06-02 \
  --image /tmp/timeline-2026-06-02-main.png \
  --data-file /tmp/timeline-2026-06-02-events.json \
  --stdin <<'EOF'
- Today I worked on the Obsidian logging flow.
- The visual timeline report is embedded below for review.
EOF
```

Useful flags:

- `--date YYYY-MM-DD`: target daily note.
- `--section "## 今日记录"`: heading to append under.
- `--image PATH`: copy a PNG/JPEG/WebP report image into the Obsidian attachment folder and insert an embed. Can be passed multiple times.
- `--image-section "## 时间轴报表"`: heading for image embeds.
- `--data-file PATH`: append file contents as a fenced data block.
- `--data-json TEXT`: append JSON/text directly as a fenced data block.
- `--data-section "## 时间轴数据"`: heading for the data block.
- `--attachment-folder PATH`: folder inside the vault for copied report images.
- `--vault PATH`: Obsidian vault root.
- `--daily-folder PATH`: folder inside the vault.
- `--dry-run`: print the target path and resulting note without writing.

Environment overrides:

- `OBSIDIAN_VAULT_DIR`
- `OBSIDIAN_DAILY_FOLDER`
- `OBSIDIAN_DAILY_SECTION`
- `OBSIDIAN_ATTACHMENT_FOLDER`

When the vault is outside the writable sandbox, request filesystem approval rather than trying to work around permissions.

## Report Screenshot Guidance

Use the designed dashboard screenshots whenever the user wants a visual record in Obsidian.

Recommended captures:

- Whole day report: `timeline-for-agent screenshot --range day --date YYYY-MM-DD --selector main`
- Timeline only: `timeline-for-agent screenshot --range day --date YYYY-MM-DD --selector timeline`
- Analysis panels: `timeline-for-agent screenshot --range day --date YYYY-MM-DD --selector analytics`
- Event cards: `timeline-for-agent screenshot --range day --date YYYY-MM-DD --selector events`

For a daily Obsidian note, prefer one `main` screenshot unless the user asks for deeper analysis. If the user wants both tracking and human-readable review, include both:

- A concise diary summary under `## 今日记录`.
- One or more screenshot embeds under `## 时间轴报表`.
- The structured payload or important event table under `## 时间轴数据`.

## Timeline Mirroring

Mirror to `timeline-for-agent` only when it adds value. The daily note can accept fuzzy natural language, but timeline events need precise, valid data.

Do not create timeline events when:

- The user only gives a broad summary with no time range.
- The classification is unclear and categories have not been checked.
- An event crosses midnight and has not been split.

When mirroring, follow the existing project instructions in `docs/agent-instructions.md`: use CLI commands first, do not edit raw JSON directly, and keep events inside the target date.
