# Crawl Workflow Template

Use this when a catalog entry has no per-tool `workflow_file`. Copy this template and fill in the bracketed fields based on the chosen tool + user's target.

<required_reading>
- The chosen tool's catalog entry in `references/tool-catalog.json` (filter by `repo_url`)
- `references/rate-limit-guide.md` (if scraping, not API)
</required_reading>

<process>
## 1. Define the Crawl Spec

Fill these in with the user before any request:

- **Target:** `[URL or API endpoint pattern]`
- **Tool:** `[name]` (`[repo_url]`)
- **Scope:** `[how many pages/items/endpoints, approximate]`
- **Output:** `[path + format — e.g., data/run-YYYYMMDD/items.jsonl]`
- **Auth needed:** `[yes/no; if yes, where stored — never in repo]`
- **Politeness:** `delay between requests = [N]s, respect robots.txt = yes`

## 2. Skeleton Code

Adapt to the tool. Pattern:

```python
# scripts/crawl_[tool]_[target].py
import time, json, pathlib

OUTPUT = pathlib.Path("data/run-YYYYMMDD/items.jsonl")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

def fetch_one(url_or_endpoint):
    # TOOL-SPECIFIC: use the chosen library to fetch
    ...

def main():
    targets = [...]  # generate or read
    with OUTPUT.open("w", encoding="utf-8") as f:
        for t in targets:
            try:
                item = fetch_one(t)
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
            except Exception as e:
                print(f"skip {t}: {e}")
            time.sleep(POLITENESS_DELAY)
    print(f"done -> {OUTPUT}")

if __name__ == "__main__":
    main()
```

## 3. Pre-Flight Check

Before the real run:
- Dry run on **1 sample target** — confirm output shape matches expectation.
- Confirm `robots.txt` allows the path (if scraping).
- Confirm rate limit / quota headroom.

## 4. Run

Execute the script. Stream progress (every N items, print count + last URL).

## 5. Validate Output

- Count items vs. expected.
- Spot-check 3 random items.
- Check for systematic skips (e.g., all 404s → wrong URL pattern).

## 6. Report

Tell the user:
- Items fetched: N
- Output: `[path]`
- Errors: …
- Suggested follow-up: feed to LLM / index / schedule incremental refresh.
</process>

<success_criteria>
- Crawl spec was confirmed with the user before the first request.
- Output file written, count matches expectation ±10%.
- No credentials in code or output.
- Polite delay honored; no rate-limit errors.
</success_criteria>
