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
- Default page size 30; we use `per_page=100` to minimize calls.
- For each query in `category-keywords.md`, fetch up to N pages until we have `--max-per-category` unfiltered candidates.

## Per-Query Budget

At 30 req/min authenticated, with 5 categories × ~7 queries each = ~35 queries:
- 35 queries × 1-2 pages each ≈ 50-70 search calls.
- Plus ~1 enrichment call per new repo (for license, etc.) — defer most enrichment to lazy load.
- Total: ~3-5 min runtime if we respect limits.

## Backoff Strategy

The script implements exponential backoff:
- On HTTP 403 with `X-RateLimit-Remaining: 0` → sleep until `X-RateLimit-Reset`, retry once.
- On HTTP 429 → wait 60s, retry up to 3 times.
- On 5xx → wait 2^n seconds (n=1..5), retry up to 5 times.
- Any other error → log and skip that query, continue.

## Headers to Read

Always inspect:
- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset` (unix timestamp)
- `Retry-After` (on 429/503)

## Secondary Rate Limits

GitHub also enforces "secondary" limits (content-based, harder to predict) — e.g., too many requests in a short burst. Mitigation:
- Sleep ~500ms between successive requests.
- Disable parallel requests in the script (keep it sequential).

## Token Rotation (Optional)

If running multiple categories heavily, you can rotate between `Yuuqq` and `qcmuu` accounts (both logged in per `gh auth status`). Not needed for typical weekly refresh.
