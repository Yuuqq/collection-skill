---
name: collection-skill
description: Chinese-social-media crawler picker — recommends the right tool and actually fetches posts, notes, comments, and reviews from 小红书 / 抖音 / 哔哩哔哩 / 微博 / 知乎 / 贴吧 / 快手 / 微信公众号 / 视频号 / 淘宝 / 京东 / 拼多多 / 豆瓣 / 雪球 (xhs, douyin, bilibili, weibo, zhihu, tieba, kuaishou, wechat, taobao, jd, pdd, douban, xueqiu), behind a compliance gate. Also covers general scraping of any website or API (抓取 / 采集 / 爬取 / 爬虫 / 抓数据 / 获取数据 / 数据采集 / scrape / crawl / collect data). Maintains a curated, auto-refreshed catalog of scrapers, API collectors, MCP/agent skills, and datasets.
---

<essential_principles>
<principle name="Catalog First, Crawl Second">
This skill has two halves that share one knowledge base:
- **Discover & catalog** — periodically scan GitHub for "collection-class" repos (scrapers, API collectors, agent skills/MCP, datasets/awesome-lists) and store them in `references/tool-catalog.{md,json}`.
- **Match & crawl** — when the user names a target, recommend tools from the catalog via progressive disclosure, then start crawling.

Always check the catalog freshness before recommending. If stale (> N days), surface that to the user.
</principle>
<principle name="Chinese-Social First">
The headline use case is Chinese social/e-commerce platforms. When the user names one (小红书/抖音/B站/微博/知乎/贴吧/快手/公众号/视频号/淘宝/京东/拼多多/豆瓣/雪球…), route **directly** to the fast path (`workflows/match-and-crawl.md` Step 3B) via `references/chinese-social-platforms.md` — never show the generic category menu. The general five-category catalog is the fallback breadth for every other target.

**Compliance gate (non-negotiable):** most Chinese-platform tools are reverse-engineered and violate platform ToS. Always show the compliance reminder before tool selection, re-confirm intent before the first network request, never help evade anti-bot / risk-control systems, and default to low request rates + anonymized personal data.
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

<principle name="LLM Judging Is Optional &amp; Safely Guarded">
Discovery *can* use an LLM (`LLM_API_KEY`) to judge candidates and reassign categories, but **pruning is never the model's call alone** — deterministic collection-signal and human-curation guards defend it. Full mechanism in `references/llm-judging.md`. Not needed for the match-and-crawl path.
</principle>
</essential_principles>

<intake>
On invocation, determine the user's intent. Most messages fall into one of:

1. **"抓小红书 / 抖音评论 / 微博热搜…" (Chinese platform named)** — fast path: platform-tagged shortlist + compliance gate, straight to a tool.
2. **"Find/discover tools"** — refresh the catalog, search GitHub for collection-class repos.
3. **"I want to scrape/fetch X" (any other target)** — match a tool from the catalog to a target and start crawling.
4. **"Browse the catalog"** — show categories / tool cards without scraping.
5. **"Schedule / automate"** — set up the periodic refresh hook.

If the message is ambiguous, ask **one** minimal question to disambiguate, then route.
</intake>

<routing>
Map user intent to a workflow:

| User says | Route to |
|-----------|----------|
| any Chinese platform name (小红书/抖音/B站/微博/淘宝…, full alias table in `references/chinese-social-platforms.md`) | `workflows/match-and-crawl.md` (Step 3B fast path) |
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
- `chinese-social-platforms.md` — canonical platform registry: alias → key map, tag conventions, per-platform crawl characteristics (load whenever a Chinese platform is suspected)
- `repo-schema.md` — the JSON schema every catalog entry must satisfy
- `rate-limit-guide.md` — GitHub API quota, pagination, retry/backoff patterns
- `llm-judging.md` — optional LLM judge mechanism + safe-pruning guards (load only when running/tuning discovery)
</reference_index>

<workflows_index>
All in `workflows/`:

| Workflow | Purpose |
|----------|---------|
| `discover-catalog.md` | Scan GitHub, dedupe, update catalog JSON + MD |
| `match-and-crawl.md` | Progressive-disclosure matching → tool selection → crawl |
| `browse-catalog.md` | Read-only category/card view, no network crawling |
| `schedule-refresh.md` | Install a periodic refresh hook (cron / Task Scheduler) |
| `tools/*.md` | **Per-tool crawl workflows** — loaded by `match-and-crawl.md` Step 5 when a catalog entry's `workflow_file` points here. Each is a concrete crawl recipe (spec → skeleton → pre-flight → run → validate → report). See `tools/mediacrawler.md` for the compliance-gated pattern. |

Existing per-tool workflows: `tools/scrapy.md`, `tools/playwright.md`, `tools/crawl4ai.md`, `tools/mediacrawler.md`.
</workflows_index>

<success_criteria>
This skill works when:
- A Chinese-platform request hits the fast path and sees the compliance reminder before any tool card.
- The catalog contains real, recently-verified entries across all five categories.
- `tool-catalog.md` and `tool-catalog.json` stay in sync (MD regenerated from JSON).
- A user asking "I want to scrape X" gets a category menu → tool card → workflow in ≤ 2 turns.
- Discovery runs are idempotent and logged in `discovery-log.md`.
- No credentials are committed; tokens come from env or `gh` keyring.
</success_criteria>
