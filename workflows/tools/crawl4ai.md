# Workflow: Scrape with Crawl4AI

> Per-tool workflow for **Crawl4AI** (`unclecode/crawl4ai`). Loaded by `workflows/match-and-crawl.md` Step 5 when the user picks Crawl4AI, or when the target is a dynamic page **and** the goal is LLM-ready output (markdown / structured JSON via schema).

Crawl4AI is the right pick when:
- The page is JS-rendered (like Playwright) **but** your downstream is an LLM/RAG/embedding pipeline — you want clean markdown, not raw HTML.
- You want to extract a **structured schema** (list of `{title, price, url}`) from the rendered page without hand-writing selectors — Crawl4AI does LLM-driven extraction.
- You want one tool that does render + chunk + extract in a single call.

Use **Playwright** if you just need the rendered DOM / network capture; use **Scrapy** for large static crawls. Crawl4AI's value-add is the **LLM extraction layer** on top of a headless browser.

<required_reading>
- `references/rate-limit-guide.md`
- The target site's `robots.txt`
</required_reading>

<process>
## 1. Define the Crawl Spec

Confirm **before writing any code**:

- **Target:** seed URL(s); note if JS-rendered
- **Output format:** markdown (for RAG/embedding) **or** structured JSON (for a typed schema). Pick one.
- **Schema** (if structured): the fields + types to extract, e.g. `{title: str, price: float, url: str}`
- **Extraction strategy:** `LLMExtractionStrategy` (needs an LLM API key — read from env) vs. `RegexExtractionStrategy` / CSS (no LLM, cheaper)
- **Output:** `data/crawl4ai-<run>/out.md` or `out.jsonl`
- **LLM cost awareness:** LLM extraction bills per page; confirm scope (N pages × cost) with the user first

## 2. Skeleton Script

```python
# scripts/crawl_crawl4ai_<target>.py
import asyncio, json, pathlib, os
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy

OUTPUT = pathlib.Path("data/crawl4ai-run/out.md")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
SEED = "https://example.com/products"

# Schema-driven extraction (structured). Leave None for plain markdown.
SCHEMA = None  # e.g. {"type":"object","properties":{"title":{"type":"string"},...}}

async def main():
    strategy = None
    if SCHEMA:
        strategy = LLMExtractionStrategy(
            provider=os.environ["LLM_PROVIDER"],  # e.g. "openai/gpt-4o-mini"
            api_token=os.environ["LLM_API_KEY"],   # never hardcode
            schema=SCHEMA,
            instruction="Extract the listed fields from each item on the page.",
        )
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(
            url=SEED,
            word_count_threshold=50,
            extraction_strategy=strategy,
            bypass_cache=False,
        )
        if strategy:
            OUTPUT = OUTPUT.with_suffix(".jsonl")
            OUTPUT.write_text(result.extracted_content or "[]", encoding="utf-8")
        else:
            OUTPUT.write_text(result.markdown, encoding="utf-8")
    print(f"done -> {OUTPUT}")

asyncio.run(main())
```

## 3. Pre-Flight Check

- **robots.txt + ToS:** standard check.
- **Markdown dry run first:** run once with `SCHEMA = None` on 1 URL; eyeball the markdown. If it's clean and complete, **you may not need LLM extraction at all** — parse the markdown with a regex/split and save the LLM cost.
- **Cost check:** if using LLM strategy, confirm `N pages × per-page token cost` is acceptable with the user before scaling.
- **LLM key:** confirm `LLM_API_KEY` is in env, not in code.

## 4. Run

`python scripts/crawl_crawl4ai_<target>.py`. The first run downloads a browser (~100MB) if not cached.

## 5. Validate Output

- **Markdown mode:** open the `.md`, confirm section structure and that main content (not nav/footer boilerplate) survived.
- **Structured mode:** `jq length out.jsonl` matches item count; `jq '.[0]'` has all schema fields non-null; spot-check 1 field against the live page.
- Empty extracted content → instruction too vague, or content is behind interaction (switch to Playwright workflow).

## 6. Report

Same shape. Add the LLM-cost line: "LLM 提取花了约 $X / 用了 Y tokens。如果只要 markdown,关掉 LLM 策略可省这笔。"
</process>

<success_criteria>
- Markdown dry run performed before enabling LLM extraction (cost gate).
- Extraction strategy justified: LLM only if CSS/regex can't do it.
- LLM key read from env, never hardcoded.
- Output format matches the user's downstream (markdown for RAG, JSON for typed schema).
</success_criteria>
