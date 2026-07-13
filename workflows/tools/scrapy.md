# Workflow: Scrape with Scrapy

> Per-tool workflow for **Scrapy** (`scrapy/scrapy`). Loaded by `workflows/match-and-crawl.md` Step 5 when the user picks Scrapy, or when a target is a large/static multi-page site needing a spider + pipeline.

Scrapy is the right pick when:
- The site is mostly static HTML (no heavy JS rendering), OR paginated/linked deeply.
- You want a **spider** (structured crawl with link-following rules) rather than a one-shot fetch.
- You want a built-in pipeline (dedupe, JSON/CSV export, retry, throttling).

Use **Playwright** instead if the page is a JS SPA; use **httpx + BeautifulSoup** for a single page.

<required_reading>
- `references/rate-limit-guide.md` — politeness + concurrency settings
- The target site's `robots.txt` (Step 1 below)
</required_reading>

<process>
## 1. Define the Crawl Spec

Confirm with the user **before writing any code**:

- **Target domain + seed URLs:** e.g. `https://example.com/list?page=1`
- **What to extract:** item fields (title, price, url, date, …) — get one example URL the user points at and pin the selectors there
- **Scope:** how many pages/items max, or a stop condition
- **Output:** `data/scrapy-<run>/items.jsonl` (JSON Lines = streamable, resumable)
- **Auth needed:** yes/no (login cookies, API key)
- **Politeness:** `DOWNLOAD_DELAY` (default 1.0s), `CONCURRENT_REQUESTS_PER_DOMAIN` (default 2), `ROBOTSTXT_OBEY = True`

## 2. Skeleton Spider

```python
# spiders/<target>_spider.py
import scrapy, json, pathlib

OUTPUT = pathlib.Path("data/scrapy-run/items.jsonl")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

class TargetSpider(scrapy.Spider):
    name = "target"
    start_urls = ["https://example.com/list?page=1"]

    # settings honored by Scrapy at runtime
    custom_settings = {
        "DOWNLOAD_DELAY": 1.0,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 2,
        "ROBOTSTXT_OBEY": True,
        "AUTOTHROTTLE_ENABLED": True,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
        "FEEDS": {str(OUTPUT): {"format": "jsonlines", "encoding": "utf-8",
                                "overwrite": True}},
        "USER_AGENT": "collection-skill/1.0 (+contact@example.com)",
        "RETRY_TIMES": 3,
        "HTTPCACHE_ENABLED": True,  # dev only — speeds up re-runs
    }

    def parse(self, response):
        # 1. yield items on this page
        for card in response.css("div.item-card"):
            yield {
                "url": response.urljoin(card.css("a::attr(href)").get()),
                "title": card.css("h3::text").get(),
                "price": card.css(".price::text").get(),
            }
        # 2. follow pagination / detail pages
        next_page = response.css("a.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, self.parse)
```

Run: `scrapy runspider spiders/target_spider.py`

## 3. Pre-Flight Check

- **robots.txt:** run `scrapy fetch --nolog <robots_url>` or `curl`; if disallowed, stop and tell the user — do not override.
- **1-page dry run:** set `CLOSESPIDER_PAGECOUNT = 1`, run, inspect `items.jsonl` (field shapes, encoding, missing values).
- **Confirm selectors survive:** if 3 sample URLs have different DOM shapes, write `parse_detail` + item loaders instead of one `parse`.

## 4. Run

`scrapy runspider ...` streams items to the feed as they arrive. Tail the log for `item_scraped_count` and any `Filtered`/`Retry` noise.

## 5. Validate Output

- `wc -l items.jsonl` ≈ expected (±10%).
- Spot-check 3 random rows: `shuf -n 3 items.jsonl | jq .`
- Grep for systematic failures: all-None fields → wrong selector; duplicate URLs → `dupefilter` off or `dont_filter=True` leaking.
- Confirm `scrapy` exit code 0; non-zero = pipeline error or unhandled exception.

## 6. Report

Tell the user:
- Items scraped: N (vs. expected M)
- Output: `data/scrapy-run/items.jsonl`
- Skips/errors: count + category (404, timeout, filtered)
- Suggestion: "要不要把站点加进 catalog 标记 favorite / 设个增量 crawl 的 cron？"
</process>

<success_criteria>
- Crawl spec confirmed before the first request.
- `ROBOTSTXT_OBEY = True` and a real `DOWNLOAD_DELAY` ≥ 0.5s.
- Output file exists, line count within ±10% of expectation, fields non-empty.
- No credentials in spider code or output.
</success_criteria>
