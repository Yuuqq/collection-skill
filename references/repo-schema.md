# Catalog Entry Schema

Every entry in `tool-catalog.json` MUST conform to this. `scripts/validate_catalog.py` enforces it: discovery repairs/drops non-conforming entries before writing, `add_repo.py` refuses to write a non-conforming entry, and CI runs the validator as a gate.

## Top-Level Shape

```json
{
  "schema_version": 1,
  "last_refreshed": "2026-07-05T18:30:00Z",
  "entries": [ { ...entry... }, ... ]
}
```

## Entry Fields

| Field | Type | Required | Set by | Notes |
|-------|------|----------|--------|-------|
| `repo_url` | string | ✅ | discovery | Canonical URL, primary dedup key |
| `full_name` | string | ✅ | discovery | `owner/name` |
| `name` | string | ✅ | discovery | Repo name only |
| `category` | enum | ✅ | discovery | One of: `web-scraper`, `dynamic-scraper`, `api-collector`, `agent-skill`, `dataset` |
| `one_line_description` | string | ✅ | discovery | ≤ 200 chars, English or Chinese |
| `stars` | integer | ✅ | discovery | From GitHub API |
| `language` | string \| null | ✅ | discovery | Primary language |
| `topics` | array[string] | ✅ | discovery | GitHub topics |
| `last_updated` | date (ISO) | ✅ | discovery | `pushed_at` from API |
| `discovered_at` | date (ISO) | ✅ | discovery | First time we saw it |
| `license` | string \| null | ✅ | discovery | SPDX id |
| `homepage` | string \| null | ✅ | discovery | Repo homepage URL if set |
| `verified` | boolean | ✅ | default `false` | True once a human/agent has confirmed it works |
| `use_cases` | array[string] | ✅ | discovery (heuristic) then refined | 1-3 short bullet phrases |
| `caveats` | array[string] | optional | manual | Warnings (rate limits, anti-bot, etc.) |
| `tags` | array[string] | optional | either | Free-form, for filtering |
| `favorite` | boolean | optional | manual | Default `false`; user-set |
| `notes` | string | optional | manual | User-added commentary |
| `workflow_file` | string \| null | optional | manual | Path to a per-tool workflow if we wrote one |
| `match_score` | integer | optional | discovery | 0-100, used for ranking |

## Validation Rules

1. `category` must be exactly one of the five enum values.
2. `repo_url` must start with `https://github.com/`.
3. `stars` must be ≥ 0.
4. `last_updated` must be within the last 5 years (else drop — abandoned).
5. `use_cases` has 1-3 entries, each ≤ 80 chars.
6. No duplicate `repo_url` across entries.
7. `one_line_description` is required and ≤ 200 chars.

### Enforcement (`scripts/validate_catalog.py`)

- Truncatable flaws are auto-repaired first: `use_cases` clipped to 3 × 80 chars, `one_line_description` to 200, bad `stars` coerced to 0.
- Non-protected entries that still fail a rule are **dropped** (logged as `[schema]` warnings).
- Protected entries (`verified` / `favorite` / `manually-added`) are never dropped — they stay with the flaw surfaced. Same protection-first philosophy as the LLM-judging guards.
- Duplicate `repo_url` (rule 6) is always repaired keep-first, matching discovery's by-url dedupe.

CLI: `python scripts/validate_catalog.py` — exit 0 when valid (warnings allowed), 1 on errors.
Tests: `python -m unittest discover -s tests` (18 cases).

## Discovery Defaults

A freshly-discovered entry has:
- `verified: false`
- `favorite: false`
- `use_cases`: derived from topics + description (heuristic, agent-refinable)
- `notes: ""`, `caveats: []`, `workflow_file: null`

A re-discovered entry (already in catalog):
- All `manual`-set fields above are **preserved**.
- Only auto-fields (`stars`, `last_updated`, `topics`, `language`, `match_score`) are refreshed.

## Tag Conventions

Tags are free-form strings but two conventions are load-bearing:

### `chinese-social` (cross-category soft tag)

Marks an entry as a Chinese-social-media collection tool. These entries keep their
primary `category` (usually `dynamic-scraper` or `api-collector`) AND additionally
carry this tag so they aggregate into the 🇨🇳 block in `tool-catalog.md`.

### `platform:<key>` (sub-tag for chinese-social)

Every `chinese-social` entry MUST also carry one or more `platform:<key>` tags
indicating which platform(s) it covers. `key` is one of the registry keys in
`references/chinese-social-platforms.md`:

- Single-platform tool: `tags: ["chinese-social", "platform:weibo"]`
- Multi-platform umbrella: `tags: ["chinese-social", "platform:multi"]`
- Multi-platform with named coverage: `tags: ["chinese-social", "platform:multi", "platform:douyin", "platform:bilibili", ...]`

`build_catalog_md.py` reads these tags to render the 🇨🇳 aggregation block;
`match-and-crawl.md` Step 3B reads `platform:<key>` to filter tools when the user
names a specific platform.

### Other tags

- `manually-added` — set by `scripts/add_repo.py` on all manual additions
- `framework`, `production`, `llm-ready`, `modern`, `reverse-engineering`, etc. — free-form, used only for filtering

## LLM Judging & Safe Pruning

The LLM judge can reassign an entry's `category` and rewrite its `use_cases`; **pruning is never the model's call alone**. The two deterministic guards (collection-signal protection + `agent-skill` cleanup) and the full CLI/endpoint config are documented in **`references/llm-judging.md`** — load that when tuning discovery. Schema-relevant rule: an `agent-skill` entry with no collection signal and no human-curation tag will be pruned on the next re-scan.

## Schema Versioning

If we add fields, bump `schema_version`. There is no automated migrator (yet) — a version bump must update `validate_catalog.py`'s rule set in the same change, so entries missing newly-required fields get flagged. Old fields are kept for one version, then dropped by hand.
