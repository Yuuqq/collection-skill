# GitHub API Rate Limit & Pagination Guide

## Rate Limits

| Auth mode | Search API | Core API (`/repos/...`) |
|-----------|-----------|-------------------------|
| Unauthenticated | **10 req/min** | 60 req/hour |
| Authenticated (token) | **30 req/min** | 5,000 req/hour |
| GitHub App ( installation ) | 30 req/min | 5,000 req/hour per install |

**Always prefer authenticated calls.** The discovery script tries, in order:
1. `$GITHUB_TOKEN` env var.
2. `gh auth token` (reads from keyring).
3. Falls back to unauthenticated with a warning.

## Search API Pagination

- `/search/repositories` returns up to **1,000 results** per query max (10 pages × 100/page).
- Discovery fetches up to 2 pages of 100 results per query, stopping earlier if there are no more results.
- It stops starting new queries in a category once it has at least twice `--max-per-category` candidates that pass the filters, then keeps the top `--max-per-category` by stars.

## Per-Query Budget

At 30 req/min authenticated, with 5 categories × ~7 queries each = ~35 queries:
- 35 queries × 1-2 pages each ≈ 50-70 search calls.
- Repo metadata (including license, when present) comes from search results; discovery does not make a separate GitHub request per repo.
- Runtime depends on pagination, retries, and whether LLM judging is enabled.

## Backoff Strategy

The script makes up to five attempts per request:
- On a successful response with `X-RateLimit-Remaining: 0` → wait until `X-RateLimit-Reset` before continuing.
- On HTTP 403 or 429 → honor `Retry-After`, or wait 60s if the header is missing.
- On HTTP 5xx or a network error → wait 2^n seconds (n=1..5).
- Other HTTP errors or exhausted attempts → log the problem and return no results for that page.

## Headers to Read

The discovery script reads:
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset` (unix timestamp)
- `Retry-After` (on 403/429)

## Secondary Rate Limits

GitHub also enforces "secondary" limits (content-based, harder to predict) — e.g., too many requests in a short burst. Mitigation:
- Sleep ~500ms between successive requests.
- Disable parallel requests in the script (keep it sequential).
