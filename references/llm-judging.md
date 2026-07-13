# LLM Judging & Safe Pruning

> Consolidated reference for how discovery can use an OpenAI-compatible LLM to judge candidates, and why pruning is **never** left to the model alone.
>
> **Load this when:** you are running/improving discovery (`workflows/discover-catalog.md`), debugging why an entry was kept or pruned, or tuning the keywords / collection signals. Not needed for the match-and-crawl path.

## Overview

`scripts/discover_repos.py` can optionally call an LLM to judge every candidate:
1. **Should it be included** in the catalog?
2. **Which of the five categories** fits? (overrides the keyword-inferred category)
3. Give 1–3 short **use cases**.

The model is good at **reassigning categories** and **enriching use cases**, but **unreliable at excluding** off-topic entries — it tends to keep generic "skills" / awesome-lists. So inclusion *enrichment* is trusted; *pruning* is defended deterministically.

## Endpoint / config

| Var / flag | Default | Purpose |
|---|---|---|
| `LLM_API_KEY` | — | Required to enable judging. Supports `;`-separated **key pool**; one key is picked per request to share rate-limit budget. |
| `LLM_BASE_URL` | `https://token.sensenova.cn/v1` | OpenAI-compatible endpoint. |
| `LLM_MODEL` | `sensenova-6.7-flash-lite` | Model id. |
| `--llm` / `--no-llm` | auto (on iff key set) | Force enable/disable. |
| `--rescan` / `--no-rescan` | `--rescan` when LLM on | Re-judge the **entire** catalog each run (default), or only this run's new/updated entries. |

When `LLM_API_KEY` is unset → falls back to the star/keyword heuristic and **never prunes**.

## The judging prompt (system)

The model is told: you are a curator for a data-collection / scraping tool catalog; only 5 mutually-exclusive categories; **precision over recall** (better to miss than mis-include); output a JSON array only. The full prompt lives in `_JUDGE_SYSTEM` in `discover_repos.py`.

## Safe pruning — two deterministic guards

Because the model over-keeps, pruning is **never** the model's call alone. Two guards run after the model returns:

### 1. Collection-signal protection (`COLLECTION_SIGNALS`)

Any entry whose `name` / `one_line_description` / `topics` contains a collection term is **never auto-removed**, even if the model says exclude. Signals include:

`scrap`, `crawl`, `collect`, `fetch`, `playwright`, `selenium`, `puppeteer`, `browser`, `mcp`, `api client`, `dataset`, `rss`, `extract`, `parser`, `spider`, `scraper`, `爬虫`, `采集`, `抓取`, `爬取`, `数据`, `web agent`, `web automation`, `agentql`, `etl`, `sdk`, `knowledge graph`, `knowledge-graph`, `graphrag`, `open data`

If the model flags such an entry as exclude, the run logs `[llm] kept (collection signal) <name>` and keeps it.

### 2. Deterministic `agent-skill` cleanup

Inside the `agent-skill` category, any entry with **no collection signal AND no human curation** is pruned. Human curation = any of: `favorite` / `verified` / `manually-added` tag / `preset` tag. This is what keeps generic "skills" repos (career, marketing, ui-ux, obsidian, tutorials, …) out of the catalog.

## What is always preserved

Human-curated entries are never dropped or re-categorized by the model. An `agent-skill` entry **must** carry a collection signal, or it will be pruned on the next re-scan. Seed genuinely-collection MCP servers / agent frameworks with a `preset` / `manually-added` tag (or a description containing a signal) to keep them.

## CLI / CI surface

- **CLI:** `python scripts/discover_repos.py [--llm|--no-llm] [--rescan|--no-rescan] ...`
- **CI:** `.github/workflows/discover.yml` has a `workflow_dispatch` input `llm` (default `true`). Configure `LLM_API_KEY` (and optionally `LLM_BASE_URL` / `LLM_MODEL`) in repo **Settings → Secrets**.

The script records the **effective** judging mode (one of `llm` / `heuristic` / `dry-run`) in `references/.last-run.json` so CI and logs report what actually happened, not what was requested.
