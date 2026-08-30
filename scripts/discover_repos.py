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
                                     [--llm | --no-llm]
                                     [--llm-base-url URL] [--llm-model M]
                                     [--llm-api-key KEY]

Auth: tries $GITHUB_TOKEN, then `gh auth token`. Falls back to unauthenticated
with a warning (much lower rate limit).

LLM judging (optional): when LLM_API_KEY is set, every candidate is sent to an
OpenAI-compatible endpoint to confirm inclusion and (re)assign its category.
Disable with --no-llm. Endpoint defaults to the Sensenova OpenAI-compatible API;
override with LLM_BASE_URL / LLM_MODEL env vars or the CLI flags above.
"""
from __future__ import annotations

import argparse
import json
import os
import random
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

import validate_catalog  # sibling module: schema gate (references/repo-schema.md)

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
        # multiple comma-separated values (topics/exclude are written that way),
        # and may carry a trailing `(annotation)` comment we must discard before
        # it leaks into the GitHub search query.
        item = line.lstrip("- ").strip()
        # split on commas, then strip backticks/quotes/parenthetical notes
        pieces = []
        for p in item.split(","):
            p = p.strip()
            # prefer a backticked span when present:  `value` (note)  ->  value
            m = re.search(r"`([^`]+)`", p)
            if m:
                p = m.group(1)
            else:
                # drop a trailing parenthetical: value (note)  ->  value
                p = re.sub(r"\s*\([^)]*\)\s*$", "", p).strip()
            p = p.strip("`").strip("'\"").strip()
            if p and p != "---":
                pieces.append(p)
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
# LLM judging (OpenAI-compatible)
# ---------------------------------------------------------------------------
# Default to the Sensenova OpenAI-compatible endpoint. Override via
# LLM_BASE_URL / LLM_MODEL / LLM_API_KEY env vars or CLI flags.
LLM_DEFAULT_BASE_URL = "https://token.sensenova.cn/v1"
LLM_DEFAULT_MODEL = "sensenova-6.7-flash-lite"

_JUDGE_SYSTEM = """你是一个技术策展人，负责维护一个 GitHub「数据采集 / 爬虫」工具目录。本目录只收录与「采集、抓取、爬取、数据获取」直接相关的工具、框架、SDK、agent 技能或数据集。
目录只有以下 5 个互斥分类：
- web-scraper：静态 HTML / 简单 HTTP 抓取（BeautifulSoup、httpx、Selectolax）
- dynamic-scraper：JS 动态渲染页面、SPA（Playwright、Selenium、Crawl4AI）
- api-collector：REST/GraphQL、SDK 拉取、ETL 管道
- agent-skill：Claude/GPT agent skills、MCP server、tool-use 框架
- dataset：采集/爬虫直接可用的公开数据集、或以采集/爬虫为核心主题的 awesome-list / 资源汇总

精度优先（宁可漏、不要错）。对给定的候选仓库逐个判断：
1) 是否应纳入本目录。仅当该仓库的核心用途是采集/抓取/爬取/数据获取，或其数据集/资源汇总明确服务于采集场景时才 include=true。
   以下一律 include=false（ false positives ）：
   - 与采集无关的通用 awesome-list / 资源汇总（例如猫图、游戏、通用编程清单、面试题库）；
   - 纯教程、课程、示例代码、脚手架模板、boilerplate、starter；
   - 个人博客、简历、文档站、纯文档仓库；
   - 与数据采集无关的普通应用、库或工具。
2) 若纳入，归入上述最贴切的一个分类；若都不贴切则 category 填 "none"。
3) 给出 1-3 个简短适用场景 use_cases（每条 ≤ 20 字，中文或英文均可）。

只输出一个 JSON 数组，不要任何解释文字。数组每个元素格式：
{"full_name": "owner/name", "url": "https://github.com/owner/name", "include": true/false, "category": "分类或 none", "reason": "简短理由", "use_cases": ["场景1","场景2"]}"""


def _chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def _url_from_fullname(fn):
    return f"https://github.com/{fn}" if fn else ""


def _parse_judge_array(text):
    try:
        s = (text or "").strip()
        if s.startswith("```"):
            parts = s.split("```")
            s = parts[1] if len(parts) > 1 else s
            if s.lstrip().startswith("json"):
                s = s.lstrip()[4:]
        start, end = s.find("["), s.rfind("]")
        if start == -1 or end == -1:
            return []
        arr = json.loads(s[start:end + 1])
        return arr if isinstance(arr, list) else []
    except Exception:
        return []


class LLM:
    """Minimal OpenAI-compatible chat client (stdlib only).

    `api_key` may be a ';'-separated pool; a key is chosen per request so the
    pool shares rate-limit budget. Falls back to heuristic if no key is set.
    """

    def __init__(self, base_url, api_key, model):
        self.base_url = (base_url or LLM_DEFAULT_BASE_URL).rstrip("/")
        self.api_keys = [k.strip() for k in (api_key or "").split(";") if k.strip()]
        self.model = model or LLM_DEFAULT_MODEL

    def chat(self, messages, temperature=0, max_retries=3):
        if not self.api_keys:
            raise RuntimeError("no LLM API key configured")
        payload = {"model": self.model, "messages": messages, "temperature": temperature}
        data = json.dumps(payload).encode("utf-8")
        url = f"{self.base_url}/chat/completions"
        for attempt in range(max_retries):
            key = random.choice(self.api_keys)
            try:
                req = urllib.request.Request(
                    url, data=data,
                    headers={"Content-Type": "application/json",
                             "Authorization": f"Bearer {key}"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as e:
                if e.code in (429, 503):
                    wait = 5 * (2 ** attempt)
                    sys.stderr.write(f"[llm] http {e.code}, wait {wait}s\n")
                    time.sleep(wait)
                    continue
                sys.stderr.write(f"[llm] http {e.code} {e.reason}\n")
                raise
            except Exception as e:
                wait = 5 * (2 ** attempt)
                sys.stderr.write(f"[llm] {e}, wait {wait}s\n")
                time.sleep(wait)
                continue
        raise RuntimeError("llm chat failed after retries")

    def judge(self, repos, categories):
        tasks = [{
            "full_name": r.get("full_name", ""),
            "url": r.get("repo_url", ""),
            "name": r.get("name", ""),
            "description": r.get("one_line_description", "") or "",
            "topics": r.get("topics", []) or [],
            "language": r.get("language"),
            "stars": r.get("stars", 0),
        } for r in repos]
        if not tasks:
            return {}
        out: dict[str, dict] = {}
        for chunk in _chunks(tasks, 20):
            try:
                resp = self.chat([
                    {"role": "system", "content": _JUDGE_SYSTEM},
                    {"role": "user", "content": json.dumps(chunk, ensure_ascii=False)},
                ])
                content = resp["choices"][0]["message"]["content"]
            except Exception as e:
                sys.stderr.write(f"[llm] chunk judge failed: {e}\n")
                continue
            for row in _parse_judge_array(content):
                if not isinstance(row, dict):
                    continue
                key = row.get("url") or _url_from_fullname(row.get("full_name", ""))
                if key:
                    out[key] = row
        return out


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


def _is_protected(entry: dict) -> bool:
    """Human-curated entries are never dropped or re-categorized by the LLM."""
    if entry.get("favorite") or entry.get("verified"):
        return True
    tags = entry.get("tags") or []
    if "manually-added" in tags or "preset" in tags:
        return True
    return False


# Substrings that mark a repo as clearly about data collection / scraping.
# An entry matching one of these is NEVER auto-removed by the LLM re-scan,
# even if the model mistakenly labels it off-topic (guards against an
# unreliable judge nuking legitimate tools).
COLLECTION_SIGNALS = (
    "scrap", "crawl", "collect", "fetch", "playwright", "selenium", "puppeteer",
    "browser", "mcp", "api client", "dataset", "rss", "extract", "parser",
    "spider", "scraper", "爬虫", "采集", "抓取", "爬取", "数据", "web agent",
    "web automation", "agentql", "etl", "sdk", "knowledge graph",
    "knowledge-graph", "graphrag", "open data",
)


def _has_collection_signal(entry: dict) -> bool:
    hay = " ".join([
        entry.get("name", ""),
        entry.get("one_line_description", "") or "",
        " ".join(entry.get("topics", []) or []),
    ]).lower()
    return any(s in hay for s in COLLECTION_SIGNALS)


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
    p.add_argument("--llm", dest="llm", action="store_true", default=None,
                   help="Enable LLM judging (auto-enabled if LLM_API_KEY is set)")
    p.add_argument("--no-llm", dest="llm", action="store_false",
                   help="Disable LLM judging even if LLM_API_KEY is set")
    p.add_argument("--llm-base-url", default=os.environ.get("LLM_BASE_URL", LLM_DEFAULT_BASE_URL))
    p.add_argument("--llm-model", default=os.environ.get("LLM_MODEL", LLM_DEFAULT_MODEL))
    p.add_argument("--llm-api-key", default=os.environ.get("LLM_API_KEY"))
    p.add_argument("--rescan", dest="rescan", action="store_true", default=None,
                   help="Re-judge the ENTIRE catalog with the LLM and prune "
                        "irrelevant entries (default when LLM is enabled)")
    p.add_argument("--no-rescan", dest="rescan", action="store_false",
                   help="Only judge entries discovered/updated in this run")
    args = p.parse_args()

    triggered_by = "scheduled (GitHub Actions)" if os.environ.get("GITHUB_ACTIONS") else "manual"

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

    # --- LLM (optional) ---
    llm_key = args.llm_api_key or os.environ.get("LLM_API_KEY")
    use_llm = args.llm if args.llm is not None else bool(llm_key)
    llm = None
    if use_llm:
        if not llm_key:
            sys.stderr.write(
                "[warn] LLM judging enabled but no LLM_API_KEY — "
                "falling back to heuristic.\n")
        else:
            llm = LLM(args.llm_base_url, llm_key, args.llm_model)
            sys.stderr.write(
                f"[llm] judging enabled ({args.llm_model} @ {args.llm_base_url})\n")

    # Effective judging mode — what *actually* ran, not what was requested.
    # Written to references/.last-run.json so CI/logs/commits report the truth
    # (prevents "LLM-judged" commit messages when LLM_API_KEY was unset).
    if args.dry_run:
        effective_mode = "dry-run"
    elif llm is not None:
        effective_mode = "llm"
    else:
        effective_mode = "heuristic"

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
    run_entries: list[dict] = []

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

        # keep top-N by stars (per search category)
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
            run_entries.append(by_url[url])

    # --- LLM judging (optional): confirm inclusion + reassign category ---
    # When LLM is on, re-scan the WHOLE catalog (default) so stale/off-topic
    # entries from earlier (pre-judge) runs get pruned. Human-curated entries
    # (favorite / verified / manually-added / preset) are never dropped or
    # re-categorized.
    llm_excluded = 0
    if llm is not None:
        rescan = args.rescan if args.rescan is not None else True
        to_judge = list(by_url.values()) if rescan else run_entries
        if to_judge:
            try:
                decisions = llm.judge(to_judge, ALL_CATEGORIES)
            except Exception as e:
                sys.stderr.write(f"[llm] judge failed, keeping heuristic: {e}\n")
                decisions = {}
            for entry in to_judge:
                if _is_protected(entry):
                    continue
                d = decisions.get(entry["repo_url"])
                if not d:
                    continue
                if not d.get("include", True):
                    if _has_collection_signal(entry):
                        # LLM misjudged a clearly collection-related repo;
                        # keep it regardless.
                        sys.stderr.write(
                            f"[llm] kept (collection signal) {entry['full_name']}\n")
                        continue
                    by_url.pop(entry["repo_url"], None)
                    llm_excluded += 1
                    continue
                cat = d.get("category")
                if isinstance(cat, str) and cat in ALL_CATEGORIES:
                    entry["category"] = cat
                uc = d.get("use_cases") or []
                if uc:
                    entry["use_cases"] = [str(u) for u in uc][:3]
                tags = entry.setdefault("tags", [])
                if "llm-reviewed" not in tags:
                    tags.append("llm-reviewed")

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
        _write_last_run(effective_mode, auth_mode, triggered_by,
                        new_total, upd_total, skip_total, dry_run=True)
        return 0

    # --- Schema gate: validate/repair/drop before writing (repo-schema.md) ---
    catalog_doc, schema_warnings = validate_catalog.enforce(catalog_doc)
    for w in schema_warnings:
        sys.stderr.write(f"[schema] {w}\n")

    args.catalog.write_text(
        json.dumps(catalog_doc, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"Catalog updated: {len(catalog_doc['entries'])} entries "
          f"(+{new_total} new, ~{upd_total} updated, {skip_total} filtered)")

    # --- Record effective run mode (read by CI for the commit message) ---
    _write_last_run(effective_mode, auth_mode, triggered_by,
                    new_total, upd_total, skip_total, dry_run=False)

    # --- Append discovery log ---
    _append_log(stats, auth_mode, new_total, upd_total, skip_total,
                llm_excluded=llm_excluded, triggered_by=triggered_by,
                effective_mode=effective_mode)
    return 0


def _write_last_run(mode: str, auth_mode: str, triggered_by: str,
                    new_total: int, upd_total: int, skip_total: int,
                    dry_run: bool) -> None:
    """Record the effective judging mode for this run.

    `references/.last-run.json` is read by `.github/workflows/discover.yml` to
    build an honest commit message (e.g. 'LLM-judged' only when the LLM actually
    ran). This prevents the CI commit message from lying about how the catalog
    was produced when LLM_API_KEY is unset and the run silently fell back.
    """
    LAST_RUN = SKILL_ROOT / "references" / ".last-run.json"
    payload = {
        "effective_mode": mode,          # llm | heuristic | dry-run
        "auth_mode": auth_mode,          # token | unauthenticated
        "triggered_by": triggered_by,    # manual | scheduled (GitHub Actions)
        "dry_run": dry_run,
        "new": new_total,
        "updated": upd_total,
        "skipped": skip_total,
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }
    LAST_RUN.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _append_log(stats: dict, auth_mode: str, new_total: int,
                upd_total: int, skip_total: int,
                llm_excluded: int = 0,
                triggered_by: str = "manual",
                effective_mode: str = "heuristic") -> None:
    now = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M (%Z)")
    lines = [
        f"\n## {now}\n",
        f"- **Categories:** {', '.join(stats.keys())}",
        f"- **New entries:** {new_total}",
        f"- **Updated entries:** {upd_total}",
        f"- **Skipped (dedupe / filtered):** {skip_total}",
        f"- **LLM excluded:** {llm_excluded}",
        f"- **Effective judging mode:** {effective_mode}",
        f"- **Errors:** see stderr above",
        f"- **Auth mode:** {auth_mode}",
        f"- **Triggered by:** {triggered_by}\n",
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
