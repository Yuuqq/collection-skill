# Code Review: Yuuqq/collection-skill

Reviewed: 7b464ed (and related tree)

This document provides a concise security and robustness review of the `Yuuqq/collection-skill` repository, focusing on actual risks and logic gaps.

## CI & Security

- **Actions Script Injection (MEDIUM):** `.github/workflows/discover.yml` concatenates `github.event.inputs.categories` directly into the bash run script. This is an injection risk. Fix: Pass via environment variables.
- **Over-scoped Token in Push (MEDIUM):** `discover.yml` pushes using `https://${{ secrets.GH_PAT }}@github.com/...`. This leaks the PAT into Git remote configurations and relies on a long-lived user token. Fix: Rely on the job's `GITHUB_TOKEN` with `contents: write`.
- **Markdown Injection (LOW):** User-generated data (e.g., topics, use cases from LLM) is rendered raw into Markdown via `build_catalog_md.py`. Fix: Sanitize strings (e.g. escaping `<` and `>`) before outputting to `.md`.

## Correctness & Business Logic

- **Overbroad Collection Signals (MEDIUM):** In `discover_repos.py`, signals like `数据`, `sdk`, `browser`, `parser`, `fetch` are too common. They prevent the pruning of irrelevant repositories (especially Chinese ones). Fix: Remove them from `COLLECTION_SIGNALS`.
- **Docs-Code Drift on Pruning (MEDIUM):** `references/llm-judging.md` mentions a deterministic sweep of unprotected `agent-skill` entries without a collection signal, but the code only uses the signals to *keep* entries. Fix: Implement the sweep logic in `discover_repos.py`.
- **`add_repo.py` Tag Updates Ignored (MEDIUM):** CLI arguments for tags (`--extra-tags`, `--platform`) are dropped when updating an existing entry because `PRESERVED_FIELDS` blindly overwrites them. Fix: Merge tags correctly.
- **`add_repo.py` Docstring Inaccuracy (LOW):** The script docstring says omitting `--category` will prompt the user, but the code simply exits. Fix: Update docstring to match behavior.

## Maintenance & Code Quality

- **Missing Test CI (MEDIUM):** The repository has 18 unit tests, but no GitHub Actions workflow runs them on Pull Requests. Fix: Add a PR workflow to run `python -m unittest discover -s tests`.
- **Code Duplication (LOW):** `add_repo.py` and `discover_repos.py` duplicate `GITHUB_TOKEN` resolution and `urllib` retry logic. Fix: Extract shared utilities into `scripts/http_gh.py`.
