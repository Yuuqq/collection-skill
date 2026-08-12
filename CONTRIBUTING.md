# Contributing

Thanks for helping grow the catalog! There are three easy ways to contribute.

## 1. Submit a tool to the catalog

The fastest path: open a [tool submission issue](../../issues/new?template=submit-tool.yml)
with the repo URL and category — we (or the weekly discovery run) will vet and add it.

Prefer a PR? Add the entry yourself:

```bash
python scripts/add_repo.py owner/repo --category web-scraper   # one of the five categories
python scripts/build_catalog_md.py                              # regenerate the markdown view
python scripts/sync_readme_stats.py                             # sync README counters
```

Catalog rules:

- `references/tool-catalog.json` is canonical — never hand-edit `tool-catalog.md` (generated).
- Every entry must satisfy `references/repo-schema.md` and carry exactly one of the five
  categories: `web-scraper`, `dynamic-scraper`, `api-collector`, `agent-skill`, `dataset`.
- Curated fields (`notes`, `verified`, `favorite`, `workflow_file`) survive re-discovery —
  safe to fill in by hand.

## 2. Add a per-tool crawl workflow

Pick a cataloged tool that has no `workflow_file` yet, copy the pattern in
`workflows/tools/mediacrawler.md` (spec → skeleton → pre-flight → run → validate → report),
and point the catalog entry's `workflow_file` at your new file under `workflows/tools/`.

## 3. Fix bugs / improve scripts

Standard flow: fork → branch → PR.

- Follow conventional commits (`feat:`, `fix:`, `docs:`, `chore:`), matching the git log style.
- If you touched `scripts/`, run a `--dry-run` discovery locally before opening the PR.

## Ground rules

- **No credentials in the repo.** Tokens come from env vars or the `gh` keyring.
- **Respect boundaries.** Any workflow you contribute must honor `robots.txt`, rate limits,
  and the target's Terms of Service.
- **Never commit collected data.** `data/` is gitignored for a reason.
