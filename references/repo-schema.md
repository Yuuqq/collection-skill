# Catalog Entry Schema

Every entry in `tool-catalog.json` MUST conform to this. The discovery script validates before writing.

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

`scripts/discover_repos.py` can call an OpenAI-compatible model (env `LLM_API_KEY`,
default Sensenova `https://token.sensenova.cn/v1`) to judge every candidate:
include or not, and which category. The model is unreliable at *excluding*
off-topic entries, so pruning is defended deterministically:

1. **Collection-signal protection** (`COLLECTION_SIGNALS` in `discover_repos.py`)
   — any entry whose `name` / `one_line_description` / `topics` contain a
   collection term (`scrap`, `crawl`, `mcp`, `browser`, `parser`, `agentql`,
   `knowledge-graph`, `爬虫`, `采集`, `抓取`, `爬取`, `数据`, …) is never
   auto-removed, even if the model says exclude.
2. **Deterministic `agent-skill` cleanup** — inside `agent-skill`, any entry with
   no collection signal and no human curation (`favorite` / `verified` /
   `manually-added` / `preset` tag) is pruned. This keeps generic "skills" repos
   out of the catalog.

Human-curated entries are always preserved. Rules:

- An `agent-skill` entry **must** carry a collection signal, or it will be pruned
  on the next re-scan. Seed genuinely-collection MCP servers / agent frameworks
  with a `preset` or `manually-added` tag (or a description containing a signal)
  to keep them.
- When `LLM_API_KEY` is unset, discovery falls back to the star/keyword heuristic
  and **never prunes**.
- Full re-scan (judging the whole catalog each run) is on by default when the LLM
  is enabled; `--no-rescan` limits judging to this run's new/updated entries.

## Schema Versioning

If we add fields, bump `schema_version`. The discovery script runs a migrator forward; old fields are kept for one version then dropped.
