# Category Keywords & GitHub Topic Mapping

This file drives `scripts/discover_repos.py`. Each category has:
- `search_queries` — strings passed to GitHub Search API (`/search/repositories?q=...`).
- `topics` — GitHub topics to also match (`topic:foo`).
- `must_have_any_in_desc` — fallback regex; if a repo matches keywords but lacks these in description, lower its score.
- `exclude` — substring filters to drop false positives.

Tune these freely — they directly control discovery quality. After editing, run `discover-catalog.md` to see the effect.

---

## web-scraper

**Search queries (try each, dedupe later):**
- `web scraping python`
- `html parser scraper`
- `beautifulsoup`
- `selectolax`
- `httpx scraper`
- `static site scraper`
- `lightweight crawler`

**Topics:**
- `web-scraping`, `scraper`, `html-parser`, `crawler`, `beautifulsoup`

**Description hints (regex, case-insensitive):**
- `scrape|crawl|extract|parse html`

**Exclude:**
- `tutorial`, `awesome`, `course`, `learning`, `interview`

---

## dynamic-scraper

**Search queries (try each, dedupe later):**
- `playwright scraper`
- `selenium crawler`
- `crawl4ai`
- `headless browser scraper`
- `spa scraper`
- `javascript rendering scraper`
- `browser automation scrape`
- `小红书 爬虫` (Chinese platform scrapers — Xiaohongshu)
- `抖音 爬虫` (Douyin)
- `bilibili 爬虫` (Bilibili)
- `微博 爬虫` (Weibo)
- `知乎 爬虫` (Zhihu)
- `贴吧 爬虫` (Baidu Tieba)
- `快手 爬虫` (Kuaishou)
- `微信公众号 爬虫` (WeChat Official Account)
- `视频号 爬虫` (WeChat Channels)
- `豆瓣 爬虫` (Douban)
- `雪球 爬虫` (Xueqiu)
- `weibo crawler`, `xiaohongshu crawler`, `bilibili crawler`, `douyin crawler`

**Topics:**
- `playwright`, `selenium`, `puppeteer`, `headless`, `crawl4ai`, `browser-automation`

**Description hints (regex, case-insensitive):**
- `dynamic|javascript|spa|render|headless|login`

**Exclude:**
- `tutorial`, `awesome`, `testing framework` (drop pure test frameworks)

---

## api-collector

**Search queries:**
- `api client collector`
- `rest api sdk scraper`
- `graphql client fetcher`
- `etl pipeline python`
- `data ingestion`
- `api pagination collector`
- `微信公众号 api` (WeChat OA API-based collectors)
- `淘宝 评论 采集` (Taobao/review scrapers)
- `京东 评论 采集` (JD.com reviews)
- `豆瓣 api` (Douban API)
- `bilibili api` (Bilibili API SDKs)

**Topics:**
- `api-client`, `sdk`, `graphql`, `etl`, `data-ingestion`, `api-collector`

**Description hints:**
- `api|endpoint|sdk|graphql|etl|ingest`

**Exclude:**
- `awesome`, `boilerplate`, `starter`

---

## api-collector

**Search queries:**
- `api client collector`
- `rest api sdk scraper`
- `graphql client fetcher`
- `etl pipeline python`
- `data ingestion`
- `api pagination collector`

**Topics:**
- `api-client`, `sdk`, `graphql`, `etl`, `data-ingestion`, `api-collector`

**Description hints:**
- `api|endpoint|sdk|graphql|etl|ingest`

**Exclude:**
- `awesome`, `boilerplate`, `starter`

---

## agent-skill

**Search queries:**
- `claude skill`
- `agent skill`
- `mcp server`
- `model context protocol`
- `tool use agent`
- `llm agent tools`
- `agentic scraping`
- `mcp server scraper`
- `playwright mcp`
- `browser mcp`
- `web automation agent`
- `ai web agent`
- `agent browser`
- `mcp crawl`
- `claude skill scraping`

**Topics:**
- `mcp`, `claude-skills`, `agent`, `tool-use`, `mcp-server`, `llm-agent`, `browser-automation`, `web-automation`

**Description hints (regex, case-insensitive):**
- `skill|mcp|agent|tool|model context protocol|scrap|crawl|browser automation`

**Exclude:**
- `awesome`, `list of`, `marketing`, `career`, `resume`, `interview`, `ui ux`, `obsidian`, `tutorial`, `course`, `blog`, `personal`

---

## dataset

**Search queries:**
- `awesome dataset`
- `public dataset`
- `curated resources`
- `data collection list`
- `open data repository`

**Topics:**
- `dataset`, `awesome-list`, `open-data`, `public-dataset`, `resources`

**Description hints:**
- `dataset|awesome|curated|collection|resources|open data`

**Exclude:**
- `personal blog`, `resume`
