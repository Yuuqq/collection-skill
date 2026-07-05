#!/usr/bin/env python3
"""Manually add a single repo to the catalog by full_name.

Use this for repos you want in the catalog that discovery missed
(e.g., non-English keywords, niche tools). Fetches live metadata from
GitHub API, merges into catalog, preserves user-set fields if it exists.

Usage:
    python scripts/add_repo.py owner/name [--category CAT] [--notes "..." [--favorite]

If --category omitted, you'll be prompted to choose from the five canonical
categories (still scriptable — see error output).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
import urllib.request
import urllib.error

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
CATALOG = SKILL_ROOT / "references" / "tool-catalog.json"

ALL_CATEGORIES = [
    "web-scraper", "dynamic-scraper", "api-collector", "agent-skill", "dataset",
]


def gh_get(url: str, token: str | None) -> dict:
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "collection-skill"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    last_err = None
    for attempt in range(4):
        time.sleep(0.5)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (403, 429):
                wait = int(e.headers.get("Retry-After", 60))
                sys.stderr.write(f"[rate] {e.code}, wait {wait}s\n")
                time.sleep(wait)
                continue
            if 500 <= e.code < 600:
                time.sleep(2 ** (attempt + 1))
                continue
            sys.stderr.write(f"[error] {e.code} {e.reason}\n")
            try:
                body = json.loads(e.read().decode("utf-8"))
                return {"_error": body.get("message", str(e))}
            except Exception:
                return {"_error": str(e)}
        except urllib.error.URLError as e:
            last_err = e
            time.sleep(2 ** (attempt + 1))
    return {"_error": f"giving up: {last_err}"}


def repo_to_entry(repo: dict, category: str, notes: str, favorite: bool) -> dict:
    today = datetime.now(timezone.utc).date().isoformat()
    pushed = (repo.get("pushed_at") or "")[:10]
    desc = (repo.get("description") or "").strip()
    lic = repo.get("license")
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
        "license": lic.get("spdx_id") if isinstance(lic, dict) and lic else None,
        "homepage": repo.get("homepage") or None,
        "verified": True,  # manually added → considered verified
        "use_cases": [],   # to be filled below
        "caveats": [],
        "tags": ["manually-added"],
        "favorite": favorite,
        "notes": notes,
        "workflow_file": None,
        "match_score": 90,  # manually curated → high
    }


PRESERVED_FIELDS = {"verified", "use_cases", "caveats", "tags",
                    "favorite", "notes", "workflow_file", "discovered_at"}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("full_name", help="owner/name (e.g. NanmiCoder/MediaCrawler)")
    p.add_argument("--category", choices=ALL_CATEGORIES,
                   help="Canonical category. Required.")
    p.add_argument("--notes", default="", help="Optional user notes")
    p.add_argument("--favorite", action="store_true",
                   help="Mark as favorite")
    p.add_argument("--use-cases", nargs="*", default=[],
                   help="1-3 use case phrases")
    p.add_argument("--caveats", nargs="*", default=[],
                   help="Optional caveats")
    p.add_argument("--platform", default=None,
                   help="Chinese-social platform key (e.g. weibo, xiaohongshu, multi). "
                        "Auto-adds tags: ['chinese-social', 'platform:<key>']")
    p.add_argument("--extra-tags", nargs="*", default=[],
                   help="Additional free-form tags")
    args = p.parse_args()

    full_name = args.full_name.strip().strip("/").lower()
    if "/" not in full_name:
        sys.exit("full_name must be 'owner/name'")

    if not args.category:
        sys.exit(f"--category required. Choose one of: {', '.join(ALL_CATEGORIES)}")

    # --- Auth ---
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        try:
            import subprocess
            out = subprocess.run(["gh", "auth", "token"], capture_output=True,
                                 text=True, timeout=10)
            if out.returncode == 0 and out.stdout.strip():
                token = out.stdout.strip()
        except Exception:
            pass

    # --- Fetch ---
    repo = gh_get(f"https://api.github.com/repos/{full_name}", token)
    if "_error" in repo or "full_name" not in repo:
        sys.exit(f"failed to fetch {full_name}: {repo.get('_error', repo)}")
    if repo.get("archived"):
        sys.stderr.write(f"[warn] {full_name} is archived\n")
    if repo.get("fork"):
        sys.stderr.write(f"[warn] {full_name} is a fork\n")

    # --- Build entry ---
    entry = repo_to_entry(repo, args.category, args.notes, args.favorite)
    if args.use_cases:
        entry["use_cases"] = args.use_cases[:3]
    if args.caveats:
        entry["caveats"] = args.caveats
    # Tags: build fresh each time so add_repo is idempotent on tags
    tags = ["manually-added"]
    if args.platform:
        tags.extend(["chinese-social", f"platform:{args.platform}"])
    tags.extend(args.extra_tags)
    entry["tags"] = tags

    # --- Merge into catalog ---
    doc = json.loads(CATALOG.read_text(encoding="utf-8"))
    by_url = {e["repo_url"]: e for e in doc["entries"]}
    url = entry["repo_url"]
    if url in by_url:
        # merge: refresh auto fields, keep user fields unless overridden by CLI
        existing = by_url[url]
        merged = dict(entry)
        for k in PRESERVED_FIELDS:
            if k in existing:
                merged[k] = existing[k]
        # CLI overrides
        if args.notes:
            merged["notes"] = args.notes
        if args.favorite:
            merged["favorite"] = True
        if args.use_cases:
            merged["use_cases"] = args.use_cases[:3]
        if args.caveats:
            merged["caveats"] = args.caveats
        by_url[url] = merged
        action = "updated"
    else:
        by_url[url] = entry
        action = "added"

    doc["entries"] = list(by_url.values())
    doc["entries"].sort(key=lambda e: (e["category"], -e.get("stars", 0)))
    doc["last_refreshed"] = datetime.now(timezone.utc).isoformat()
    CATALOG.write_text(json.dumps(doc, ensure_ascii=False, indent=2),
                       encoding="utf-8")
    print(f"{action}: {entry['full_name']}  ⭐{entry['stars']:,}  [{entry['category']}]")
    print(f"catalog now has {len(doc['entries'])} entries")
    return 0


if __name__ == "__main__":
    sys.exit(main())
