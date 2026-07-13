# Workflow: Scrape with Playwright

> Per-tool workflow for **Playwright** (`microsoft/playwright`). Loaded by `workflows/match-and-crawl.md` Step 5 when the user picks Playwright, or when the target is a JS-rendered SPA / needs login / needs interaction (click, scroll, wait).

Playwright is the right pick when:
- The content only exists **after JS executes** (React/Vue/Angular SPA, infinite scroll, lazy-loaded lists).
- You need to **interact**: click "load more", log in, dismiss a modal, scroll to trigger loading.
- You need to capture network (XHR/fetch responses) rather than parse the rendered DOM.

Use **Scrapy** for large static multi-page crawls; use **Crawl4AI** when you want LLM-friendly markdown/structured output from rendered pages.

<required_reading>
- `references/rate-limit-guide.md`
- The target site's `robots.txt`
</required_reading>

<process>
## 1. Define the Crawl Spec

Confirm **before writing any code**:

- **Target:** seed URL + the **interaction sequence** needed to surface content (login? scroll N times? click selector? wait for `selector` to appear?)
- **What to extract:** fields + where they live after render (DOM selector or XHR endpoint)
- **Capture mode:** DOM scrape vs. network interception (interception is faster and more robust if the data comes from a JSON API — prefer it when possible)
- **Scope:** max items / max scrolls / stop condition
- **Output:** `data/playwright-<run>/items.jsonl`
- **Auth:** if login required, where credentials live (env var / `gh` keyring — never in repo)
- **Politeness:** headful delay between actions, max concurrency (default 1 browser, 1 page — raise only if site tolerates it)

## 2. Skeleton Script

```python
# scripts/crawl_playwright_<target>.py
import asyncio, json, pathlib
from playwright.async_api import async_playwright

OUTPUT = pathlib.Path("data/playwright-run/items.jsonl")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
SEED = "https://example.com/feed"
POLITENESS = 1.5  # seconds between actions

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(SEED, wait_until="networkidle")

        # Option A: DOM scrape after interaction
        results = []
        for _ in range(10):  # e.g. scroll to load 10 batches
            cards = await page.query_selector_all("div.card")
            for c in cards:
                results.append({
                    "title": await (await c.query_selector("h3")).inner_text(),
                    "url": await c.get_attribute("data-href"),
                })
            await page.mouse.wheel(0, 5000)
            await page.wait_for_timeout(int(POLITENESS * 1000))

        # Option B (preferred when available): intercept the XHR
        # async def on_response(resp):
        #     if "/api/items" in resp.url:
        #         results.extend(await resp.json())
        # page.on("response", on_response)

        with OUTPUT.open("w", encoding="utf-8") as f:
            for r in results:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        await browser.close()
    print(f"done -> {OUTPUT} ({len(results)} items)")

asyncio.run(main())
```

## 3. Pre-Flight Check

- **robots.txt + ToS:** confirm JS-rendered scraping is allowed; some SPAs forbid it in ToS even when `robots.txt` is open.
- **Headful dry run:** run once with `headless=False` and `slow_mo=200` to **see** the interaction — catches selector drift and invisible-cookie-banner blocks.
- **Network check:** open DevTools → Network; if data comes from a clean JSON API, **switch to httpx + that endpoint** (10× faster, no browser needed). Playwright is only worth it when there's no API.
- **1-item dry run:** break after first batch, inspect output.

## 4. Run

`python scripts/crawl_playwright_<target>.py`. Watch for:
- `TimeoutError` on `wait_for_selector` → selector changed or page blocked headless.
- Empty results + no errors → content loads via XHR you didn't intercept.

## 5. Validate Output

- Line count vs. expected.
- Spot-check 3 rows + click 1 URL to confirm it resolves.
- If using DOM mode, re-run once: deterministic counts? volatile counts suggest race conditions — add explicit waits.

## 6. Report

Same shape as Scrapy workflow: items fetched, output path, errors, suggested follow-up. Add: "如果该站有隐藏 API,换 httpx 会快 10 倍,要我重写吗?"
</process>

<success_criteria>
- Crawl spec + interaction sequence confirmed before code.
- Network-mode preferred over DOM-mode when an API exists.
- Headful dry run performed at least once to catch selector/interaction drift.
- Polite delays honored; no headless-detection blocks.
</success_criteria>
