---
name: collection-skill
description: Discovers and catalogs collection/scraping related skills and repos on GitHub, then progressively recommends the right tool and begins crawling when the user wants to fetch data. Use when the user wants to find scraping tools, browse a curated catalog of crawlers/collectors, or actually scrape/fetch specific data.
---

<essential_principles>
<principle name="Catalog First, Crawl Second">
This skill has two halves that share one knowledge base:
- **Discover & catalog** — periodically scan GitHub for "collection-class" repos (scrapers, API collectors, agent skills/MCP, datasets/awesome-lists) and store them in `references/tool-catalog.{md,json}`.
- **Match & crawl** — when the user names a target, recommend tools from the catalog via progressive disclosure, then start crawling.

Always check the catalog freshness before recommending. If stale (> N days), surface that to the user.
</principle>

<principle name="Progressive Disclosure">
Never dump the whole catalog. Show a **category menu** first, then drill into tool cards within the chosen category, then load the matching workflow only after the user picks a tool. Load references lazily — only what the current step needs.
</principle>

<principle name="Five Canonical Categories">
Every repo in the catalog is tagged with exactly one primary category:

| Tag | Means |
|-----|-------|
| `web-scraper` | Static HTML / simple HTTP fetch (BeautifulSoup, httpx, Selectolax) |
| `dynamic-scraper` | JS-rendered pages, SPAs (Playwright, Selenium, Crawl4AI) |
| `api-collector` | REST/GraphQL endpoints, SDK-driven pulls, ETL pipelines |
| `agent-skill` | Claude/GPT agent skills, MCP servers, tool-use frameworks |
| `dataset` | Public datasets, awesome-lists, curated resource repos |

Categories drive both discovery keywords and the matching menu.
</principle>

<principle name="Catalog Is the Source of Truth">
- `references/tool-catalog.json` — structured data, the canonical source.
- `references/tool-catalog.md` — human-readable view, **regenerated from JSON** by `scripts/build_catalog_md.py`. Never hand-edit the markdown.
- `references/discovery-log.md` — append-only run history (when, what, how many, errors).
</principle>

<principle name="Safety & Boundaries">
- Respect `robots.txt`, rate limits, and ToS. Default to authenticated GitHub API calls (higher limits) when scanning repos.
- Never store credentials in the repo. Read tokens from env vars (`GITHUB_TOKEN`) or the `gh` CLI keyring.
- Always confirm scope with the user before the first network request against a new target domain.
</principle>

<principle name="LLM Judging &amp; Safe Pruning">
Discovery can call an OpenAI-compatible LLM (env `LLM_API_KEY`, default Sensenova
`https://token.sensenova.cn/v1`) to judge every candidate: *should it be
included*, and *which of the five categories fits*. The model is **unreliable at
excluding** off-topic entries (it tends to keep generic "skills" repos), so
pruning is defended by two deterministic guards — never by the model alone:

- **Collection-signal protection** — any entry whose name / description / topics
  contain a collection term (`scrap`, `crawl`, `mcp`, `browser`, `parser`,
  `agentql`, `knowledge-graph`, `爬虫`, `采集`, `抓取`, `爬取`, `数据`, …) is
  **never** auto-removed, even if the model mislabels it.
- **Deterministic `agent-skill` cleanup** — inside `agent-skill`, any entry with
  no collection signal and no human curation (`favorite` / `verified` /
  `manually-added` / `preset` tag) is pruned. This is what keeps generic
  "skills" repos (career, marketing, ui-ux, obsidian, tutorials, …) out.

Human-curated entries are always preserved. When `LLM_API_KEY` is unset the
pipeline falls back to the star/keyword heuristic and never prunes anything.
The full re-scan (judging the *entire* catalog each run, not just fresh hits)
is enabled by default when the LLM is on; use `--no-rescan` to limit judging to
this run's new/updated entries.
</principle>
</essential_principles>

<intake>
On invocation, determine the user's intent. Most messages fall into one of:

1. **"Find/discover tools"** — refresh the catalog, search GitHub for collection-class repos.
2. **"I want to scrape/fetch X"** — match a tool from the catalog to a target and start crawling.
3. **"Browse the catalog"** — show categories / tool cards without scraping.
4. **"Schedule / automate"** — set up the periodic refresh hook.

If the message is ambiguous, ask **one** minimal question to disambiguate, then route.
</intake>

<routing>
Map user intent to a workflow:

| User says | Route to |
|-----------|----------|
| "refresh", "discover", "find new repos", "update catalog" | `workflows/discover-catalog.md` |
| "I want to scrape/fetch/collect X", "抓 X 数据" | `workflows/match-and-crawl.md` |
| "show me the catalog", "what tools do we have", "browse" | `workflows/browse-catalog.md` |
| "schedule", "automate refresh", "定时", "cron" | `workflows/schedule-refresh.md` |

After routing, the workflow tells you which references to load. Do not preload everything.
</routing>

<reference_index>
All in `references/`:

- `tool-catalog.json` — canonical structured catalog (data source)
- `tool-catalog.md` — human-readable catalog (generated, do not edit)
- `discovery-log.md` — append-only run log
- `category-keywords.md` — search keywords + GitHub topic mapping per category
- `repo-schema.md` — the JSON schema every catalog entry must satisfy
- `rate-limit-guide.md` — GitHub API quota, pagination, retry/backoff patterns
</reference_index>

<workflows_index>
All in `workflows/`:

| Workflow | Purpose |
|----------|---------|
| `discover-catalog.md` | Scan GitHub, dedupe, update catalog JSON + MD |
| `match-and-crawl.md` | Progressive-disclosure matching → tool selection → crawl |
| `browse-catalog.md` | Read-only category/card view, no network crawling |
| `schedule-refresh.md` | Install a periodic refresh hook (cron / Task Scheduler) |
</workflows_index>

<success_criteria>
This skill works when:
- The catalog contains real, recently-verified entries across all four categories.
- `tool-catalog.md` and `tool-catalog.json` stay in sync (MD regenerated from JSON).
- A user asking "I want to scrape X" gets a category menu → tool card → workflow in ≤ 2 turns.
- Discovery runs are idempotent and logged in `discovery-log.md`.
- No credentials are committed; tokens come from env or `gh` keyring.
</success_criteria>
