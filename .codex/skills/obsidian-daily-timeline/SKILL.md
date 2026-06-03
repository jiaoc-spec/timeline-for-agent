---
name: obsidian-daily-timeline
description: Collect conversational daily-life material into an Obsidian daily note and optionally mirror structured time-block events into timeline-for-agent. Use when the user reports what they did, narrates calendar items, mood, meaningful events, difficult moments, gratitude, relationships, body state, reflections, asks Codex to remember/log a day, wants notes sent to Obsidian, or wants daily diary content plus timeline report images/data.
---

# Obsidian Daily Timeline

Use this skill to turn the user's conversational day material into a durable Obsidian daily-note entry with optional `timeline-for-agent` report screenshots and structured data. Obsidian is the output archive for material collected through Telegram/CyberBoss/Codex conversation, not a manual input surface the user must fill every day. `timeline-for-agent` supplies visual reports and optional time-block data.

Keep two modes separate:

- Daily capture: sachlich, ohne Bewertung. Record what the user said in clear, factual language with minimal interpretation.
- Daily review after midnight: analytical and comprehensive, but still grounded in the day's notes and clearly separated from the raw log.

Core workflow principle:

```text
Human -> Telegram/CyberBoss conversation -> Codex/skill processing -> Obsidian output
```

Do not design daily notes around manual checkboxes, blank prompts, or fields that require the user to open Obsidian. If data is missing, leave it as "未记录" or write a short question under `## 待确认`, but do not block the note.

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
2. Convert the user's report into concise Markdown. Preserve concrete details, names, links, decisions, mood, emotional tone, physical state, difficult moments, gratitude, meaningful moments, and open loops. Do not invent times, durations, categories, causes, feelings, outcomes, or evaluations.
3. If the user wants the designed report visuals, first generate one or more timeline screenshots with `timeline-for-agent screenshot`.
4. Append the Markdown, report image embeds, and optional data block to the Obsidian daily note with `scripts/append_daily_note.py`.
5. If the user also wants timeline data, or the update contains clear start/end times, use the project CLI before generating final screenshots:
   - Run `timeline-for-agent categories` when category or eventNode choice is unclear.
   - Run `timeline-for-agent read --date YYYY-MM-DD` before modifying existing events.
   - Run `timeline-for-agent write --date YYYY-MM-DD --stdin` with valid event JSON.
6. Report the note path, copied image path(s), and whether timeline data was also written.

## Daily Capture Shape

When the user gives a broad spoken update, organize it under `## 今日记录` with only the sections that fit the material. Keep the user's language and emotional nuance, but keep the wording factual and non-judgmental. Do not over-clinicalize ordinary life. Daily capture should be append-only conversational intake, not a form.

Style requirements for daily capture:

- Write sachlich, ohne Bewertung.
- Prefer "用户说/提到/描述..." only when needed for uncertainty; otherwise record directly.
- Keep the user's stated feelings as facts, e.g. "心情：低落" or "感到感恩", not "反应过度" or "很积极".
- Do not add advice, diagnosis, motivational commentary, or hidden interpretation.
- Do not infer causes unless the user explicitly linked them.
- Preserve uncertainty with phrases like "未说明具体时间", "原因未明确", or "根据口述无法确认".

Recommended Markdown shape:

```markdown
### 事件流
- HH:MM（如已知）...
- 未记录具体时间：...

### 学习 / 工作 / 护理成长
- ...

### 运动 / 身体 / 能量
- ...

### 情绪和关系
- ...

### 有意义或值得保留
- ...

### 待确认
- ...
```

Use fewer headings for short updates. If the user speaks in a single flowing paragraph, preserve it as a short narrative plus bullets for important facts. If the user gives calendar-style items, keep them as an event list; if they give reflections, keep them as reflections. Do not add empty headings just because they exist in the template.

Convert short status messages into useful output:

- "下班了" -> an event under `### 事件流`.
- "到家了" -> an event and possible commute boundary, without inventing commute duration.
- "开始运动" / "运动结束" -> a workout event with duration only if both boundaries or a stated duration are available.
- "今天看了一篇 Trauma-informed Care 论文" -> learning/work growth entry; include paper details only if stated.
- "今天有点累" -> mood/body/energy entry; do not infer a cause unless stated.
- "Praxisanleitung 做了30分钟" -> learning/work statistic entry with duration.

Treat these as first-class diary content, not as secondary notes:

- Mood, anxiety, joy, disappointment, anger, calm, loneliness, motivation, or emotional shifts.
- Difficult, unfair, stressful, or unhappy events.
- Gratitude, tenderness, beauty, support received, and moments worth remembering.
- Meaningful or unusual events, even when they do not have a clear time range.
- Body state, sleep, energy, symptoms, appetite, medication, exercise, or sensory state.
- Relationship moments, conversations, conflicts, repair, affection, boundaries, and decisions.
- Open loops, questions, things to follow up, and patterns worth tracking.

If the update includes sensitive mental health material, write in grounded, non-diagnostic language. Preserve what the user said, and avoid adding interpretations that were not stated.

## Daily Review After Midnight

After 00:00, the task changes from raw capture to review of the previous day. Append the review to the previous day's daily note under `## 每日复盘`.

The review may analyze, but it must remain evidence-based and separated from the raw log. Use the previous day's Obsidian note, timeline data, and report images as inputs. Do not overwrite `## 今日记录`.

Recommended review shape:

```markdown
## 每日复盘

### 一天概览
- ...

### 时间线和活动分布
- ...

### 学习统计
- Deutsch / Fachsprache：...
- English：...
- Pflegewissenschaft / Paper：...
- Praxisanleitung：...
- Python / Projekte：...

### 运动和身体统计
- ...

### 情绪和能量线索
- ...

### 重要事件
- ...

### 感恩和有意义的部分
- ...

### 消耗和压力来源
- ...

### 自动评分 / 项目依据
- ...

### 模式和观察
- ...

### 明天可留意
- ...
```

Review rules:

- Base every analytical point on content from the daily note, timeline data, or report screenshot.
- Distinguish facts from hypotheses. Use "可能" or "值得观察" for hypotheses.
- Keep the tone calm, precise, and useful; avoid praise/blame language.
- If data is incomplete, say which parts are missing rather than filling gaps.
- Include report image embeds generated after the day's data is complete, usually one `main` screenshot and optionally `analytics`.
- Include a compact data block only when it helps future tracking.
- The review may infer mood and energy state, but label it as inferred when the user did not explicitly state it.
- Weekly and monthly summaries should aggregate generated daily outputs, not ask the user to fill separate weekly/monthly templates.

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
- The structured payload, reflection data, or important event table under `## 时间轴数据`.

## Timeline Mirroring

Mirror to `timeline-for-agent` only when it adds value. The daily note can accept fuzzy natural language, emotions, meaning, and reflection; timeline events need precise, valid data.

Do not create timeline events when:

- The user only gives a broad summary with no time range.
- The user gives mood, gratitude, conflict, reflection, or meaning without a concrete schedule.
- The classification is unclear and categories have not been checked.
- An event crosses midnight and has not been split.

When mirroring, follow the existing project instructions in `docs/agent-instructions.md`: use CLI commands first, do not edit raw JSON directly, and keep events inside the target date.
