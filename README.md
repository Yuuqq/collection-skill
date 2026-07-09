<p align="center">
  <img src="docs/banner.svg" alt="collection-skill banner" width="100%"/>
</p>

<h3 align="center">
  Discover · Catalog · Match · Crawl
</h3>

<p align="center">
  <a href="https://github.com/Yuuqq/collection-skill/blob/main/README.md">English</a> ·
  <a href="README.zh-CN.md">简体中文</a> ·
  <a href="README.ja.md">日本語</a> ·
  <a href="README.es.md">Español</a>
</p>

<p align="center">
  <img alt="status" src="https://img.shields.io/badge/status-active-22c55e?style=flat-square">
  <img alt="license" src="https://img.shields.io/badge/license-MIT-blue?style=flat-square">
  <img alt="catalog" src="https://img.shields.io/badge/tools%20cataloged-183-8b5cf6?style=flat-square">
  <img alt="language" src="https://img.shields.io/badge/top%20lang-Python-3776AB?style=flat-square">
  <img alt="platform" src="https://img.shields.io/badge/platform-cross--platform-475569?style=flat-square">
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

> Auto-generated from `tool-catalog.json` · last refreshed `2026-07-05`

| Category | Count | | Top languages |
|----------|------:|---|---------------|
| 🕸️ web-scraper | 42 | | Python · Go · JS |
| 🔌 api-collector | 41 | | Python · TypeScript |
| ⚡ dynamic-scraper | 39 | | Python · TypeScript |
| 🤖 agent-skill | 31 | | JavaScript · Python |
| 📚 dataset | 30 | | HTML · Markdown |
| **Total** | **183** | | **Python (89)** leads |

## 🎴 Category cards

<table>
  <tr>
    <td width="50%" align="center"><img src="docs/card-web-scraper.svg" alt="web-scraper card"/><br><sub><a href="docs/card-web-scraper.svg">🕸️ web-scraper · 42 tools</a></sub></td>
    <td width="50%" align="center"><img src="docs/card-dynamic-scraper.svg" alt="dynamic-scraper card"/><br><sub><a href="docs/card-dynamic-scraper.svg">⚡ dynamic-scraper · 39 tools</a></sub></td>
  </tr>
  <tr>
    <td width="50%" align="center"><img src="docs/card-api-collector.svg" alt="api-collector card"/><br><sub><a href="docs/card-api-collector.svg">🔌 api-collector · 41 tools</a></sub></td>
    <td width="50%" align="center"><img src="docs/card-agent-skill.svg" alt="agent-skill card"/><br><sub><a href="docs/card-agent-skill.svg">🤖 agent-skill · 31 tools</a></sub></td>
  </tr>
  <tr>
    <td colspan="2" align="center"><img src="docs/card-dataset.svg" alt="dataset card"/><br><sub><a href="docs/card-dataset.svg">📚 dataset · 30 tools</a></sub></td>
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

## 🤖 LLM 智能判级（可选）

设置 `LLM_API_KEY` 后，发现流程会把每个候选仓库发给 **OpenAI 兼容接口**，
由其判断 **是否纳入** 并 **归入哪个分类**（覆盖搜索关键词推测的分类），
同时补全 1–3 条适用场景。默认端点为 Sensenova 兼容 API，可用
`LLM_BASE_URL` / `LLM_MODEL` 覆盖；未设置 key 时自动退回基于星标与关键词的启发式逻辑。
Key 支持 `;` 分隔的密钥池，按请求随机选取以摊匀限流。

仓库已内置 GitHub Action（`.github/workflows/discover.yml`），按 `cron` 每周自动检索并刷新目录；
在仓库 **Settings → Secrets** 中配置 `GH_PAT`、`LLM_API_KEY`（及可选的 `LLM_BASE_URL` / `LLM_MODEL`）即可启用，
也可在 Actions 页面手动 `workflow_dispatch` 触发并勾选是否启用 LLM。

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

## 🌍 Translations

| Language | File |
|----------|------|
| English | [`README.md`](README.md) |
| 简体中文 | [`README.zh-CN.md`](README.zh-CN.md) |
| 日本語 | [`README.ja.md`](README.ja.md) |
| Español | [`README.es.md`](README.es.md) |

## 📄 License

MIT
