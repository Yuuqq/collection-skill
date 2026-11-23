# LLM Judging & Safe Pruning

> Consolidated reference for how discovery can use an OpenAI-compatible LLM to judge candidates, and why pruning is **never** left to the model alone.
>
> **Load this when:** you are running/improving discovery (`workflows/discover-catalog.md`), debugging why an entry was kept or pruned, or tuning the keywords / collection signals. Not needed for the match-and-crawl path.

## Overview

`scripts/discover_repos.py` can optionally call an LLM to judge entries in the merged catalog:
1. **Should it be included** in the catalog?
2. **Which of the five categories** fits? (overrides the keyword-inferred category)
3. Give 1–3 short **use cases**.

The model is good at **reassigning categories** and **enriching use cases**, but **unreliable at excluding** off-topic entries — it tends to keep generic "skills" / awesome-lists. So inclusion *enrichment* is trusted; *pruning* is defended deterministically.

## Endpoint / config

| Var / flag | Default | Purpose |
|---|---|---|
| `LLM_API_KEY` / `--llm-api-key` | — | A key is required to enable judging. Supports a `;`-separated **key pool**; one key is picked per request. Prefer the environment variable to keep keys out of shell history. |
| `LLM_BASE_URL` / `--llm-base-url` | `https://token.sensenova.cn/v1` | OpenAI-compatible endpoint. |
| `LLM_MODEL` / `--llm-model` | `sensenova-6.7-flash-lite` | Model id. |
| `--llm` / `--no-llm` | auto (on iff key set) | Force enable/disable. |
| `--rescan` / `--no-rescan` | `--rescan` when LLM on | Re-judge the **entire** catalog each run (default), or only this run's new/updated entries. |

Without a key, discovery falls back to the star/keyword heuristic. No LLM pruning occurs, but schema enforcement can still drop invalid entries.

## The judging prompt (system)

The model is told: you are a curator for a data-collection / scraping tool catalog; only 5 mutually-exclusive categories; **precision over recall** (better to miss than mis-include); output a JSON array only. The full prompt lives in `_JUDGE_SYSTEM` in `discover_repos.py`.

## Safe pruning — two deterministic guards

An LLM exclusion only removes an entry if neither of these guards applies:

### 1. Collection-signal protection (`COLLECTION_SIGNALS`)

An entry whose `name` / `one_line_description` / `topics` contains a collection term is **not removed by the LLM pass**, even if the model says exclude. Signals include:

`scrap`, `crawl`, `collect`, `fetch`, `playwright`, `selenium`, `puppeteer`, `browser`, `mcp`, `api client`, `dataset`, `rss`, `extract`, `parser`, `spider`, `scraper`, `爬虫`, `采集`, `抓取`, `爬取`, `数据`, `web agent`, `web automation`, `agentql`, `etl`, `sdk`, `knowledge graph`, `knowledge-graph`, `graphrag`, `open data`

If the model flags such an entry as exclude, the run logs `[llm] kept (collection signal) <name>` and keeps it.

### 2. Human curation protection

Entries marked `favorite` or `verified`, or tagged `manually-added` or `preset`, are sent to the judge when in scope, but the script ignores the model's decisions for them. There is no separate automatic cleanup for `agent-skill`: an entry with no collection signal can still be kept if the model does not exclude it.

## CLI / CI surface

- **CLI:** `python scripts/discover_repos.py [--llm|--no-llm] [--rescan|--no-rescan] ...`
- **CI:** `.github/workflows/discover.yml` has a `workflow_dispatch` input `llm` (default `true`). Configure `LLM_API_KEY` (and optionally `LLM_BASE_URL` / `LLM_MODEL`) in repo **Settings → Secrets**.

The script records the **effective** judging mode (one of `llm` / `heuristic` / `dry-run`) in `references/.last-run.json` for CI and logs. `llm` means the judge was configured for the run; it does not guarantee every request succeeded. Entries without a decision retain their pre-judge values.
