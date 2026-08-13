<p align="center">
  <img src="docs/banner.svg" alt="collection-skill banner" width="100%"/>
</p>

<h3 align="center">
  Discover · Catalog · Match · Crawl
</h3>

<p align="center">
  <a href="README.md">English</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.es.md">Español</a>
</p>

<p align="center">
  <img alt="status" src="https://img.shields.io/badge/status-active-22c55e?style=flat-square">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-blue?style=flat-square">
  <img alt="catalog" src="https://img.shields.io/badge/tools%20cataloged-155-8b5cf6?style=flat-square">
  <img alt="language" src="https://img.shields.io/badge/top%20lang-Python-3776AB?style=flat-square">
  <img alt="platform" src="https://img.shields.io/badge/platform-cross--platform-475569?style=flat-square">
  <a href="https://github.com/Yuuqq/collection-skill/actions/workflows/discover.yml"><img alt="Discover &amp; Catalog" src="https://github.com/Yuuqq/collection-skill/actions/workflows/discover.yml/badge.svg"></a>
</p>

---

> A skill that **discovers and catalogs collection/scraping-related skills and repos on GitHub**, then **progressively recommends the right tool and begins crawling** when you want to fetch data.

## ✨ Highlights

| | |
|:--|:--|
| 🗂️ **Curated catalog** | Auto-discovers GitHub repos into **five canonical categories**, deduped and score-ranked. |
| 🧭 **Progressive disclosure** | Never dumps the whole catalog — category menu → tool card → workflow → crawl. |
| 🗃️ **JSON is canonical** | `tool-catalog.json` is the single source of truth; the markdown view is generated. |
| 🔐 **Safe by default** | Reads tokens from `gh` keyring / env — no credentials in the repo. |
| ⏱️ **Schedulable** | Install a periodic refresh via cron / Task Scheduler. |

## 📥 Install

Works with any agent that speaks the open [Agent Skills](https://agentskills.io) format — Claude Code, Cursor, Codex, and friends:

```bash
npx skills add Yuuqq/collection-skill
```

<details>
<summary>Manual install (git clone)</summary>

Clone into your agent's skills directory:

```bash
# Claude Code (personal)
git clone https://github.com/Yuuqq/collection-skill.git ~/.claude/skills/collection-skill

# Cursor
git clone https://github.com/Yuuqq/collection-skill.git ~/.cursor/skills/collection-skill

# Codex
git clone https://github.com/Yuuqq/collection-skill.git ~/.codex/skills/collection-skill

# or per-project: .claude/skills/ · .cursor/skills/ · .codex/skills/
```

</details>

> Discovery scripts need Python 3.10+; authenticate via the [`gh` CLI](https://cli.github.com/) or `GITHUB_TOKEN` for higher GitHub API limits.

## 📦 What it does

Two halves sharing **one knowledge base**:

<p align="center">
  <img src="docs/flow.svg" alt="How collection-skill works" width="92%"/>
</p>

### ① Discover & Catalog
Periodically scans GitHub for *collection-class* repos across five categories:

| Tag | Means | Examples |
|-----|-------|----------|
| 🕸️ `web-scraper` | Static HTML / simple HTTP fetch | BeautifulSoup, httpx, Selectolax, Scrapy |
| ⚡ `dynamic-scraper` | JS-rendered pages, SPAs | Playwright, Selenium, Crawl4AI |
| 🔌 `api-collector` | REST/GraphQL, SDK pulls, ETL | SDK-driven collectors, pipelines |
| 🤖 `agent-skill` | Claude/GPT skills, MCP servers | tool-use frameworks |
| 📚 `dataset` | Public datasets, awesome-lists | curated resource repos |

### ② Match & Crawl
When you say *"I want to scrape X"*, it walks a short funnel:

```
category menu  →  tool card  →  load workflow  →  confirm scope  →  crawl
```

## 📊 Catalog snapshot

> Auto-generated from `tool-catalog.json` · last refreshed `2026-08-13`

| Category | Count | | Top languages |
|----------|------:|---|---------------|
| 🕸️ web-scraper | 36 | | Python · Java · Jupyter Notebook |
| 🔌 api-collector | 27 | | Python · TypeScript · Go |
| ⚡ dynamic-scraper | 47 | | Python · TypeScript · HTML |
| 🤖 agent-skill | 17 | | Python · TypeScript · JavaScript |
| 📚 dataset | 28 | | Python · HTML · JavaScript |
| **Total** | **155** | | **Python (83)** leads |

> 🆕 **New tools land every week.** The catalog auto-refreshes weekly — see what's newly added in each [weekly digest](../../releases). **Watch** the repo to get notified.

## 🎴 Category cards

<table>
  <tr>
    <td width="50%" align="center"><img src="docs/card-web-scraper.svg" alt="web-scraper card"/><br><sub><a href="docs/card-web-scraper.svg">🕸️ web-scraper · 36 tools</a></sub></td>
    <td width="50%" align="center"><img src="docs/card-dynamic-scraper.svg" alt="dynamic-scraper card"/><br><sub><a href="docs/card-dynamic-scraper.svg">⚡ dynamic-scraper · 47 tools</a></sub></td>
  </tr>
  <tr>
    <td width="50%" align="center"><img src="docs/card-api-collector.svg" alt="api-collector card"/><br><sub><a href="docs/card-api-collector.svg">🔌 api-collector · 27 tools</a></sub></td>
    <td width="50%" align="center"><img src="docs/card-agent-skill.svg" alt="agent-skill card"/><br><sub><a href="docs/card-agent-skill.svg">🤖 agent-skill · 17 tools</a></sub></td>
  </tr>
  <tr>
    <td colspan="2" align="center"><img src="docs/card-dataset.svg" alt="dataset card"/><br><sub><a href="docs/card-dataset.svg">📚 dataset · 28 tools</a></sub></td>
  </tr>
</table>

## 🚀 Usage

Invoke the skill, then speak naturally:

| You say | What happens |
|---------|--------------|
| `refresh` / `discover` | Runs `scripts/discover_repos.py`, updates the catalog |
| `I want to scrape X` / `抓 X 数据` | Progressive disclosure → category menu → card → crawl |
| `browse` / `show catalog` | Read-only category/card view |
| `schedule` / `定时` | Installs a periodic refresh (cron / Task Scheduler) |

## 🛠️ Quick start

```bash
# 1. (recommended) authenticate — 30 search req/min vs 10 unauthenticated
gh auth login

# 2. first refresh
python scripts/discover_repos.py
python scripts/build_catalog_md.py

# 3. (optional) schedule a weekly refresh — invoke the skill and say "schedule"
```

## 🤖 LLM judging (optional)

Set `LLM_API_KEY` and the discovery pipeline sends every candidate repo to an
**OpenAI-compatible endpoint**, which decides **whether to include it** and
**which category it belongs to** (overriding the keyword-based guess), and fills
in 1–3 usage scenarios. The default endpoint is a Sensenova-compatible API;
override with `LLM_BASE_URL` / `LLM_MODEL`. Without a key it falls back to
star/keyword heuristics. The key accepts a `;`-separated pool, picked at random
per request to spread rate limits.

A bundled GitHub Action (`.github/workflows/discover.yml`) refreshes the catalog
weekly on `cron`; set `GH_PAT` and `LLM_API_KEY` (plus optional `LLM_BASE_URL` /
`LLM_MODEL`) under **Settings → Secrets** to enable it, or trigger it manually
via `workflow_dispatch` from the Actions tab.

## 🗺️ Project structure

```
collection-skill/
├── SKILL.md                       # Router + essential principles
├── workflows/
│   ├── discover-catalog.md        # Refresh from GitHub
│   ├── match-and-crawl.md         # Progressive disclosure → crawl
│   ├── browse-catalog.md          # Read-only view
│   └── schedule-refresh.md        # Install periodic refresh
├── references/
│   ├── tool-catalog.json          # Canonical data (edit this)
│   ├── tool-catalog.md            # Generated view (do not edit)
│   ├── discovery-log.md           # Append-only run history
│   ├── category-keywords.md       # Search terms per category
│   ├── repo-schema.md             # Entry schema
│   └── rate-limit-guide.md        # GitHub API limits
├── templates/
│   ├── crawl-template.md          # Generic crawl workflow
│   ├── discovery-log-entry.md
│   └── run_scheduled_refresh.sh.template
├── scripts/
│   ├── discover_repos.py          # GitHub search → catalog
│   ├── build_catalog_md.py        # JSON → markdown
│   └── add_repo.py                # Manually add an entry
└── docs/                          # README banners & diagrams
```

## ⚖️ Design rules

- **JSON is canonical.** `tool-catalog.md` is regenerated by `build_catalog_md.py` — never hand-edit it.
- **Progressive disclosure.** Categories first, tool cards next, workflow only after a tool is picked.
- **No credentials in repo.** Tokens come from `$GITHUB_TOKEN` or `gh auth token`.
- **User fields preserved.** Re-discovery never overwrites `notes`, `verified`, `favorite`, `workflow_file`.
- **Respect boundaries.** Honor `robots.txt`, rate limits, and Terms of Service; confirm scope before crawling a new domain.

## 🤝 Contribute a tool

Know a great scraper, collector, agent skill, or dataset that's missing? It takes 30 seconds:

- **Open a [tool submission](../../issues/new?template=submit-tool.yml)** — we vet and add it (the weekly run picks it up too).
- **Or send a PR** — see [CONTRIBUTING.md](CONTRIBUTING.md) for the catalog rules and the per-tool workflow pattern.

Every submission makes the catalog better for everyone. 🙌

## 🌍 Translations

| Language | File |
|----------|------|
| English | [`README.md`](README.md) |
| 简体中文 | [`README.zh-CN.md`](README.zh-CN.md) |
| 日本語 | [`README.ja.md`](README.ja.md) |
| Español | [`README.es.md`](README.es.md) |

## 📄 License

MIT — see [LICENSE](LICENSE).
