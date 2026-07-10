# Discovery Log

Append-only history of catalog refresh runs. Newest at top.

## Schedule

- _No schedule installed yet._ Use `workflows/schedule-refresh.md` to install a periodic refresh (Windows Task Scheduler).

---


## 2026-07-10 05:11 (UTC)

- **Categories:** web-scraper, dynamic-scraper, api-collector, agent-skill, dataset
- **New entries:** 50
- **Updated entries:** 100
- **Skipped (dedupe / filtered):** 1441
- **LLM excluded:** 16
- **Errors:** see stderr above
- **Auth mode:** token
- **Triggered by:** scheduled (GitHub Actions)

- **Per category:**
  - `web-scraper`: +4 new, ~26 updated, 136 filtered
  - `dynamic-scraper`: +1 new, ~29 updated, 705 filtered
  - `api-collector`: +17 new, ~13 updated, 513 filtered
  - `agent-skill`: +2 new, ~28 updated, 26 filtered
  - `dataset`: +26 new, ~4 updated, 61 filtered


## 2026-07-09 13:39 (UTC)

- **Categories:** web-scraper, dynamic-scraper, api-collector, agent-skill, dataset
- **New entries:** 4
- **Updated entries:** 146
- **Skipped (dedupe / filtered):** 1426
- **LLM excluded:** 48
- **Errors:** see stderr above
- **Auth mode:** token
- **Triggered by:** scheduled (GitHub Actions)

- **Per category:**
  - `web-scraper`: +0 new, ~30 updated, 136 filtered
  - `dynamic-scraper`: +3 new, ~27 updated, 705 filtered
  - `api-collector`: +0 new, ~30 updated, 513 filtered
  - `agent-skill`: +1 new, ~29 updated, 12 filtered
  - `dataset`: +0 new, ~30 updated, 60 filtered


## 2026-07-06 00:45 (中国标准时间)

- **Manual add:** `NanmiCoder/MediaCrawler` ⭐55,351 → `dynamic-scraper`
- **Reason:** missed by English-only discovery keywords; high-value Chinese social-platform crawler (小红书/抖音/B站/微博/知乎/贴吧/快手)
- **Action:** also added Chinese platform keywords (小红书/抖音/bilibili/微博/知乎/贴吧 爬虫) to `references/category-keywords.md` → future discovery runs should catch similar repos
- **Verified:** true (manually curated)
- **Favorite:** true
- **Tool used:** `scripts/add_repo.py`


## 2026-07-06 00:32 (中国标准时间)

- **Categories:** web-scraper, dynamic-scraper, api-collector, agent-skill, dataset
- **New entries:** 140
- **Updated entries:** 10
- **Skipped (dedupe / filtered):** 1624
- **Errors:** see stderr above
- **Auth mode:** token
- **Triggered by:** manual (`scripts/discover_repos.py`)

- **Per category:**
  - `web-scraper`: +25 new, ~5 updated, 136 filtered
  - `dynamic-scraper`: +26 new, ~4 updated, 903 filtered
  - `api-collector`: +30 new, ~0 updated, 513 filtered
  - `agent-skill`: +30 new, ~0 updated, 12 filtered
  - `dataset`: +29 new, ~1 updated, 60 filtered


## 2026-07-06 00:22 (中国标准时间)

- **Categories:** web-scraper
- **New entries:** 4
- **Updated entries:** 1
- **Skipped (dedupe / filtered):** 136
- **Errors:** see stderr above
- **Auth mode:** token
- **Triggered by:** manual (`scripts/discover_repos.py`)

- **Per category:**
  - `web-scraper`: +4 new, ~1 updated, 136 filtered

## 2026-07-05 (initial seed)

- **Categories:** all five (web-scraper, dynamic-scraper, api-collector, agent-skill, dataset)
- **New entries:** 7 (manually seeded — scrapy, crawl4ai, playwright, httpx, mcp-servers, posthog, awesome-public-datasets)
- **Updated entries:** 0
- **Skipped:** 0
- **Errors:** none
- **Runtime:** manual seed, no API calls
- **Triggered by:** manual (skill creation)
- **Notes:** Initial seed to make the skill usable before the first real discovery run. Run `/collection-skill discover` to expand with real GitHub search results.
