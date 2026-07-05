# Workflow: Discover and Refresh Catalog

<required_reading>
Load these references before proceeding:
1. `references/category-keywords.md` — search terms per category
2. `references/repo-schema.md` — required fields per entry
3. `references/rate-limit-guide.md` — quota / pagination rules
</required_reading>

<process>
## Step 1: Confirm Scope and Auth

Check that one of these is available for authenticated GitHub calls (much higher rate limit):
- `gh auth status` returns logged in, OR
- `GITHUB_TOKEN` env var is set.

If neither, fall back to unauthenticated search (10 req/min, search limit 10/min) and warn the user. Recommend setting up `gh auth login`.

Ask the user (only if not obvious from context):
- Refresh all four categories, or just one?
- Any new keywords/topics to add this run? (optional)
- Max repos per category this run? (default 30)

## Step 2: Run the Discovery Script

Execute:

```bash
python scripts/discover_repos.py \
  --categories web-scraper dynamic-scraper api-collector agent-skill dataset \
  --max-per-category 30 \
  --catalog references/tool-catalog.json
```

The script (see `scripts/discover_repos.py`):
- Uses GitHub Search API (`/search/repositories`) with keywords from `category-keywords.md`.
- Filters: stars ≥ 50, pushed in last 2 years, not archived.
- Dedupes against existing catalog entries (by `repo_url`).
- Preserves user-added fields (`notes`, `verified`, `workflow_file`, `favorite`) on existing entries.
- Appends new entries with `verified: false` (auto-discovered, not yet validated).
- Writes updated JSON.

If `--categories` omitted, runs all five.

## Step 3: Regenerate the Markdown View

```bash
python scripts/build_catalog_md.py \
  --json references/tool-catalog.json \
  --out references/tool-catalog.md
```

This rebuilds the human-readable catalog from JSON. Never edit the markdown by hand.

## Step 4: Log the Run

Append to `references/discovery-log.md` using the template in `templates/discovery-log-entry.md`:

```
## YYYY-MM-DD HH:MM (TZ)
- Categories: …
- New entries: N
- Updated entries: M
- Skipped (dedupe / filtered): K
- Errors: …
- Runtime: ~Ns
- Triggered by: manual | scheduled
```

## Step 5: Report to User

Summarize:
- New repos added, broken down by category.
- Repos that crossed thresholds (e.g., newly >1k stars).
- Any categories that came back sparse (consider expanding keywords in `category-keywords.md`).
- Reminder of next scheduled run (if any) — see `workflows/schedule-refresh.md`.

Suggest next step: "要看新发现的工具，用 `/collection-skill browse`。要挑一个去抓数据，直接说要抓什么。"
</process>

<success_criteria>
- Discovery script ran without auth errors (or with documented fallback).
- Catalog JSON grew by N entries, each matching `repo-schema.md`.
- Markdown view regenerated and matches JSON.
- `discovery-log.md` has a new dated entry.
- Existing user-added fields (`notes`, `verified`, `favorite`) were preserved.
- No credentials written to disk.
</success_criteria>
