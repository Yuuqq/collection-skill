#!/usr/bin/env python3
"""Discover collection-class repos on GitHub and update the catalog.

Reads keywords per category from references/category-keywords.md (parsed inline),
queries GitHub Search API, dedupes against the existing catalog, and writes
updated JSON. Preserves all user-set fields on existing entries.

Usage:
    python scripts/discover_repos.py [--categories C1 C2 ...]
                                     [--max-per-category N]
                                     [--catalog PATH]
                                     [--min-stars N] [--dry-run]

Auth: tries $GITHUB_TOKEN, then `gh auth token`. Falls back to unauthenticated
with a warning (much lower rate limit).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode

try:
    import urllib.request
    import urllib.error
except ImportError:  # pragma: no cover
    sys.exit("This script requires urllib (stdlib).")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
DEFAULT_CATALOG = SKILL_ROOT / "references" / "tool-catalog.json"
KEYWORDS_FILE = SKILL_ROOT / "references" / "category-keywords.md"
LOG_FILE = SKILL_ROOT / "references" / "discovery-log.md"

ALL_CATEGORIES = [
    "web-scraper",
    "dynamic-scraper",
    "api-collector",
    "agent-skill",
    "dataset",
]

# ---------------------------------------------------------------------------
# Keyword file parsing
# ---------------------------------------------------------------------------
def parse_keywords(path: Path) -> dict[str, dict]:
    """Parse references/category-keywords.md into {category: {queries, topics, exclude}}.

    Walks the file line by line: a `## <category>` line opens a block, and within
    the block a `**Header:**` line starts one of the named lists (Search queries /
    Topics / Exclude). The list body is the following bullet or code lines.
    """
    result: dict[str, dict] = {}
    current_cat: str | None = None
    current_list: str | None = None  # one of: queries / topics / exclude / None

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()

        # Category header
        m_cat = re.match(r"^##\s+(\S+)", line)
        if m_cat:
            cat = m_cat.group(1).lower()
            current_cat = cat if cat in ALL_CATEGORIES else None
            if current_cat and current_cat not in result:
                result[current_cat] = {"queries": [], "topics": [], "exclude": []}
            current_list = None
            continue

        if current_cat is None:
            continue

        # Named list header:  **Search queries:** / **Search queries (....):**
        m_head = re.match(r"^\*\*\s*(Search queries|Topics|Exclude)\b.*:\*\*", line)
        if m_head:
            name = m_head.group(1).lower()
            current_list = {"search queries": "queries",
                            "topics": "topics",
                            "exclude": "exclude"}[name]
            continue

        # A blank line or a new **bold** line ends the current list
        if not line.strip():
            current_list = None
            continue
        if line.lstrip().startswith("**") and current_list is not None:
            current_list = None
            # fall through — this line might be another header; re-check next iteration

        if current_list is None:
            continue

        # Collect bullets or backticked code lines. A single bullet may carry
        # multiple comma-separated values (topics/exclude are written that way).
        item = line.lstrip("- ").strip()
        # split on commas, then strip backticks/quotes from each piece
        pieces = [p.strip().strip("`").strip("'\"").strip()
                  for p in item.split(",")]
        pieces = [p for p in pieces if p and p != "---"]
        result[current_cat][current_list].extend(pieces)

    return result


# ---------------------------------------------------------------------------
# GitHub API
# ---------------------------------------------------------------------------
class GH:
    def __init__(self, token: str | None):
        self.token = token
        self.base = "https://api.github.com"
        self._secondary_limit_until = 0.0

    def _headers(self) -> dict[str, str]:
        h = {"Accept": "application/vnd.github+json", "User-Agent": "collection-skill"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def search(self, query: str, per_page: int = 100, max_pages: int = 3) -> list[dict]:
        """Run /search/repositories, paginate up to max_pages, return 'items' merged."""
        items: list[dict] = []
        for page in range(1, max_pages + 1):
            params = {"q": query, "sort": "stars", "order": "desc",
                      "per_page": per_page, "page": page}
            url = f"{self.base}/search/repositories?{urlencode(params)}"
            data = self._get_with_backoff(url)
            page_items = data.get("items", [])
            items.extend(page_items)
            if len(page_items) < per_page:
                break
            if data.get("total_count", 0) <= per_page * page:
                break
        return items

    def _get_with_backoff(self, url: str, max_retries: int = 5) -> dict:
        for attempt in range(max_retries):
            # respect secondary limit window
            now = time.time()
            if now < self._secondary_limit_until:
                time.sleep(self._secondary_limit_until - now)
            # polite gap
            time.sleep(0.5)
            req = urllib.request.Request(url, headers=self._headers())
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    remaining = resp.headers.get("X-RateLimit-Remaining")
                    reset = resp.headers.get("X-RateLimit-Reset")
                    if remaining == "0" and reset:
                        sleep_for = max(int(reset) - int(time.time()), 1)
                        sys.stderr.write(
                            f"[rate-limit] exhausted, sleeping {sleep_for}s\n")
                        time.sleep(sleep_for)
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code in (403, 429):
                    retry_after = e.headers.get("Retry-After")
                    if retry_after:
                        wait = int(retry_after)
                    elif e.code == 403:
                        # likely secondary rate limit
                        wait = 60
                        self._secondary_limit_until = time.time() + wait
                    else:
                        wait = 60
                    sys.stderr.write(f"[backoff] {e.code}, wait {wait}s (attempt {attempt+1})\n")
                    time.sleep(wait)
                    continue
                if 500 <= e.code < 600:
                    wait = 2 ** (attempt + 1)
                    sys.stderr.write(f"[5xx] {e.code}, wait {wait}s\n")
                    time.sleep(wait)
                    continue
                sys.stderr.write(f"[error] {e.code} {e.reason} for {url}\n")
                return {}
            except urllib.error.URLError as e:
                wait = 2 ** (attempt + 1)
                sys.stderr.write(f"[network] {e}, wait {wait}s\n")
                time.sleep(wait)
                continue
        sys.stderr.write(f"[giveup] exhausted retries for {url}\n")
        return {}


# ---------------------------------------------------------------------------
# Repo -> entry mapping
# ---------------------------------------------------------------------------
def repo_to_entry(repo: dict, category: str) -> dict:
    today = datetime.now(timezone.utc).date().isoformat()
    pushed = (repo.get("pushed_at") or "")[:10]
    desc = (repo.get("description") or "").strip()
    return {
        "repo_url": repo.get("html_url", ""),
        "full_name": repo.get("full_name", ""),
        "name": repo.get("name", ""),
        "category": category,
        "one_line_description": (desc[:197] + "...") if len(desc) > 200 else desc,
        "stars": repo.get("stargazers_count", 0),
        "language": repo.get("language"),
        "topics": repo.get("topics", [])[:10],
        "last_updated": pushed,
        "discovered_at": today,
        "license": _license(repo),
        "homepage": repo.get("homepage") or None,
        "verified": False,
        "use_cases": _guess_use_cases(repo, category),
        "caveats": [],
        "tags": [],
        "favorite": False,
        "notes": "",
        "workflow_file": None,
        "match_score": _score(repo),
    }


def _license(repo: dict) -> str | None:
    lic = repo.get("license")
    return lic.get("spdx_id") if lic else None


def _guess_use_cases(repo: dict, category: str) -> list[str]:
    """Heuristic 1-3 use case phrases from description + topics."""
    text = ((repo.get("description") or "") + " " + " ".join(repo.get("topics", []))).lower()
    mapping = {
        "web-scraper": ["静态 HTML 抓取", "结构化数据抽取"],
        "dynamic-scraper": ["JS 渲染页面抓取", "SPA / 动态内容"],
        "api-collector": ["REST/GraphQL 数据拉取", "ETL 管道"],
        "agent-skill": ["LLM agent 工具调用", "MCP 接入"],
        "dataset": ["公开数据集", "资源汇总浏览"],
    }
    base = list(mapping.get(category, ["通用采集"]))
    if "async" in text or "asyncio" in text:
        base.append("异步高并发")
    if "llm" in text or "rag" in text:
        base.append("LLM/RAG 数据准备")
    return base[:3]


def _score(repo: dict) -> int:
    stars = repo.get("stargazers_count", 0)
    score = min(60, stars // 100)             # up to 60 from stars
    if repo.get("topics"):
        score += min(15, len(repo["topics"]) * 3)
    if repo.get("description"):
        score += 10
    if repo.get("license"):
        score += 5
    pushed_days = _days_since(repo.get("pushed_at"))
    if pushed_days < 90:
        score += 10
    elif pushed_days < 365:
        score += 5
    return max(0, min(100, score))


def _days_since(iso: str | None) -> int:
    if not iso:
        return 9999
    try:
        d = datetime.fromisoformat(iso.replace("Z", "+00:00")).date()
        return (datetime.now(timezone.utc).date() - d).days
    except Exception:
        return 9999


# ---------------------------------------------------------------------------
# Filtering & merge
# ---------------------------------------------------------------------------
def passes_filter(entry: dict, min_stars: int, exclude_words: list[str]) -> bool:
    if entry["stars"] < min_stars:
        return False
    if not entry["repo_url"].startswith("https://github.com/"):
        return False
    if _days_since(entry["last_updated"]) > 730:  # 2 years
        return False
    haystack = (entry["name"] + " " + entry["one_line_description"]).lower()
    for w in exclude_words:
        if w and w.lower() in haystack:
            return False
    return True


# User-set fields preserved on re-discovery
PRESERVED_FIELDS = {"verified", "use_cases", "caveats", "tags", "favorite",
                    "notes", "workflow_file", "discovered_at"}


def merge(existing: dict, fresh: dict) -> dict:
    """Refresh auto fields; keep user-set fields from existing."""
    merged = dict(fresh)
    for k in PRESERVED_FIELDS:
        if k in existing:
            merged[k] = existing[k]
    return merged


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--categories", nargs="+", default=ALL_CATEGORIES,
                   choices=ALL_CATEGORIES)
    p.add_argument("--max-per-category", type=int, default=30)
    p.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    p.add_argument("--min-stars", type=int, default=50)
    p.add_argument("--dry-run", action="store_true",
                   help="Run without writing the catalog file")
    args = p.parse_args()

    # --- Auth ---
    token = os.environ.get("GITHUB_TOKEN")
    auth_mode = "token"
    if not token:
        try:
            import subprocess
            out = subprocess.run(["gh", "auth", "token"], capture_output=True,
                                 text=True, timeout=10)
            if out.returncode == 0 and out.stdout.strip():
                token = out.stdout.strip()
                os.environ["GITHUB_TOKEN"] = token
        except Exception:
            pass
    if not token:
        auth_mode = "unauthenticated"
        sys.stderr.write(
            "[warn] no token — unauthenticated mode (10 search req/min).\n"
            "       Run `gh auth login` or set GITHUB_TOKEN.\n")

    # --- Load catalog ---
    catalog_doc = json.loads(args.catalog.read_text(encoding="utf-8"))
    by_url = {e["repo_url"]: e for e in catalog_doc.get("entries", [])}

    # --- Load keywords ---
    keywords = parse_keywords(KEYWORDS_FILE)
    missing = [c for c in args.categories if c not in keywords]
    if missing:
        sys.stderr.write(f"[warn] no keywords parsed for: {missing}\n")

    gh = GH(token)
    stats = {c: {"new": 0, "updated": 0, "skipped": 0} for c in args.categories}

    for cat in args.categories:
        kw = keywords.get(cat, {"queries": [], "topics": [], "exclude": []})
        queries = list(kw.get("queries", []))
        for topic in kw.get("topics", []):
            queries.append(f"topic:{topic}")
        if not queries:
            continue

        seen_fullnames: set[str] = set()
        collected: list[dict] = []
        for q in queries:
            if len(collected) >= args.max_per_category * 2:
                break
            try:
                items = gh.search(q, max_pages=2)
            except Exception as e:
                sys.stderr.write(f"[error] query '{q}': {e}\n")
                continue
            for repo in items:
                fn = repo.get("full_name")
                if not fn or fn in seen_fullnames:
                    continue
                seen_fullnames.add(fn)
                entry = repo_to_entry(repo, cat)
                if not passes_filter(entry, args.min_stars, kw.get("exclude", [])):
                    stats[cat]["skipped"] += 1
                    continue
                collected.append(entry)

        # keep top-N by stars
        collected.sort(key=lambda e: e["stars"], reverse=True)
        collected = collected[: args.max_per_category]

        for entry in collected:
            url = entry["repo_url"]
            if url in by_url:
                by_url[url] = merge(by_url[url], entry)
                stats[cat]["updated"] += 1
            else:
                by_url[url] = entry
                stats[cat]["new"] += 1

    # --- Write back ---
    catalog_doc["entries"] = list(by_url.values())
    catalog_doc["entries"].sort(key=lambda e: (e["category"], -e.get("stars", 0)))
    catalog_doc["last_refreshed"] = datetime.now(timezone.utc).isoformat()

    new_total = sum(s["new"] for s in stats.values())
    upd_total = sum(s["updated"] for s in stats.values())
    skip_total = sum(s["skipped"] for s in stats.values())

    if args.dry_run:
        sys.stderr.write(f"[dry-run] would write {len(catalog_doc['entries'])} entries "
                         f"(+{new_total} new, ~{upd_total} updated)\n")
        return 0

    args.catalog.write_text(
        json.dumps(catalog_doc, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"Catalog updated: {len(catalog_doc['entries'])} entries "
          f"(+{new_total} new, ~{upd_total} updated, {skip_total} filtered)")

    # --- Append discovery log ---
    _append_log(stats, auth_mode, new_total, upd_total, skip_total)
    return 0


def _append_log(stats: dict, auth_mode: str, new_total: int,
                upd_total: int, skip_total: int) -> None:
    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M (%Z)")
    lines = [
        f"\n## {now}\n",
        f"- **Categories:** {', '.join(stats.keys())}",
        f"- **New entries:** {new_total}",
        f"- **Updated entries:** {upd_total}",
        f"- **Skipped (dedupe / filtered):** {skip_total}",
        f"- **Errors:** see stderr above",
        f"- **Auth mode:** {auth_mode}",
        f"- **Triggered by:** manual (`scripts/discover_repos.py`)\n",
    ]
    per_cat = ["- **Per category:**"]
    for cat, s in stats.items():
        per_cat.append(f"  - `{cat}`: +{s['new']} new, ~{s['updated']} updated, {s['skipped']} filtered")
    # Insert after the topmost `## Schedule` block (find first `## ` after preamble)
    text = LOG_FILE.read_text(encoding="utf-8")
    # find the line right after the header preamble
    # simplest: prepend after the schedule section
    insert_block = "\n" + "\n".join(lines + per_cat) + "\n"
    # Put new entries under the topmost dated section by inserting just after the
    # "---\n" divider that separates the Schedule block from the entries.
    marker = "\n---\n"
    if marker in text:
        idx = text.index(marker) + len(marker)
        text = text[:idx] + insert_block + text[idx:]
    else:
        text = text + insert_block
    LOG_FILE.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    sys.exit(main())
