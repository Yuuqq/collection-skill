#!/usr/bin/env python3
"""Keep README catalog statistics in sync with tool-catalog.json.

The README files show a few numbers that must track the catalog: the badge
total, the per-category counts in the snapshot table + category-card captions,
the leading language, and the last-refreshed date. These used to be hand-edited
and drifted (README said 183 tools while the catalog had 154).

This script recomputes them from references/tool-catalog.json and rewrites the
known dynamic spans in each README by regex replacement — no markers needed.
Idempotent: running twice yields the same bytes.

Usage:
    python scripts/sync_readme_stats.py [--json PATH] [--dry-run]

Exit code: 0 if any README was changed (or --dry-run clean), 1 on error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
DEFAULT_JSON = SKILL_ROOT / "references" / "tool-catalog.json"

# README files and the per-category caption suffix (localized "tools"/"个工具"/"herramientas"/etc.)
# The snapshot table rows use the same emoji+key pattern across all languages.
README_FILES = [
    "README.md",
    "README.zh-CN.md",
    "README.ja.md",
    "README.es.md",
]

CATEGORY_ORDER = [
    "web-scraper",
    "api-collector",
    "dynamic-scraper",
    "agent-skill",
    "dataset",
]

CAT_EMOJI = {
    "web-scraper": "🕸️",
    "api-collector": "🔌",
    "dynamic-scraper": "⚡",
    "agent-skill": "🤖",
    "dataset": "📚",
}


def compute_stats(doc: dict) -> dict:
    entries = doc.get("entries", [])
    by_cat: dict[str, list] = defaultdict(list)
    for e in entries:
        by_cat[e.get("category", "")].append(e)
    per_cat = {c: len(by_cat.get(c, [])) for c in CATEGORY_ORDER}
    # top 3 languages per category
    top_langs: dict[str, str] = {}
    for c in CATEGORY_ORDER:
        langs = Counter(e.get("language") for e in by_cat.get(c, []) if e.get("language"))
        top_langs[c] = " · ".join(l for l, _ in langs.most_common(3))
    # overall lead language
    all_langs = Counter(e.get("language") for e in entries if e.get("language"))
    lead_lang, lead_n = (all_langs.most_common(1)[0] if all_langs else ("—", 0))
    return {
        "total": len(entries),
        "per_cat": per_cat,
        "top_langs": top_langs,
        "lead_lang": lead_lang,
        "lead_n": lead_n,
        "date": (doc.get("last_refreshed", "") or "")[:10] or "—",
    }


def _patch_badge(text: str, total: int) -> tuple[str, bool]:
    """Catalog badge is the only one colored 8b5cf6; its value slot is `-<N>-8b5cf6`
    in every locale (labels are localized, so don't match on them)."""
    new = re.sub(r"-\d+-8b5cf6", f"-{total}-8b5cf6", text)
    return new, new != text


def _patch_date(text: str, date: str) -> tuple[str, bool]:
    r"""`last refreshed `YYYY-MM-DD`` (any locale prefix before the backtick) -> date."""
    new = re.sub(r"(last refreshed\s*|最近刷新\s*|最終更新\s*|última actualización\s*)`[0-9-]{10}`",
                 lambda m: m.group(1) + f"`{date}`", text)
    return new, new != text


def _patch_snapshot_table(text: str, stats: dict) -> tuple[str, bool]:
    """Replace each per-category snapshot row + the total/lead row."""
    changed = False
    # per-category rows: | <emoji> <key> | <N> | | <langs> |
    for cat in CATEGORY_ORDER:
        emoji = CAT_EMOJI[cat]
        n = stats["per_cat"][cat]
        langs = stats["top_langs"][cat] or "—"
        pat = re.compile(
            r"(\|\s*" + re.escape(emoji) + r"\s+" + re.escape(cat) + r"\s*\|\s*)\d+(\s*\|\s*\|)"
            r"([^\n|]*?)(\s*\|)"
        )
        def repl(m: re.Match, n=n, langs=langs) -> str:
            return f"{m.group(1)}{n}{m.group(2)} {langs}{m.group(4)}"
        new = pat.sub(repl, text)
        if new != text:
            text = new
            changed = True
    # total row: | **Total**/**合计**/合計/... | **<N>** | | ... |
    new = re.sub(
        r"(\|\s*\*\*(?:Total|合计|合計|Total de herramientas)\*\*\s*\|\s*\*\*)\d+(\*\*\s*\|\s*\|)",
        lambda m: f"{m.group(1)}{stats['total']}{m.group(2)}",
        text,
    )
    if new != text:
        text = new
        changed = True
    # lead language count in the total row: e.g. **Python (89)** / **Python(89)** -> new count
    new = re.sub(
        r"(\*\*" + re.escape(stats["lead_lang"]) + r"\s*\()\s*\d+(\)\s*\*\*)",
        lambda m: f"{m.group(1)}{stats['lead_n']}{m.group(2)}",
        text,
    )
    if new != text:
        text = new
        changed = True
    return text, changed


def _patch_card_captions(text: str, stats: dict) -> tuple[str, bool]:
    """Card caption: '<emoji> <key> · <N> <suffix>' -> new count."""
    changed = False
    for cat in CATEGORY_ORDER:
        emoji = CAT_EMOJI[cat]
        n = stats["per_cat"][cat]
        # matches "🕸️ web-scraper · 42 tools", "· 42 个工具", "· 42 herramientas", etc.
        pat = re.compile(
            r"(" + re.escape(emoji) + r"\s+" + re.escape(cat) + r"\s*·\s*)\d+(\s*[^<\n]*?)(</a>)"
        )
        new = pat.sub(lambda m: f"{m.group(1)}{n}{m.group(2)}{m.group(3)}", text)
        if new != text:
            text = new
            changed = True
    return text, changed


def sync_file(path: Path, stats: dict, dry_run: bool) -> bool:
    text = path.read_text(encoding="utf-8")
    orig = text
    text, _ = _patch_badge(text, stats["total"])
    text, _ = _patch_date(text, stats["date"])
    text, _ = _patch_snapshot_table(text, stats)
    text, _ = _patch_card_captions(text, stats)
    changed = text != orig
    if changed and not dry_run:
        path.write_text(text, encoding="utf-8")
    return changed


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", type=Path, default=DEFAULT_JSON)
    p.add_argument("--dry-run", action="store_true", help="Report changes without writing")
    args = p.parse_args()

    doc = json.loads(args.json.read_text(encoding="utf-8"))
    stats = compute_stats(doc)
    print(f"stats: total={stats['total']} per_cat={stats['per_cat']} "
          f"lead={stats['lead_lang']}({stats['lead_n']}) date={stats['date']}")

    any_changed = False
    for name in README_FILES:
        rp = SKILL_ROOT / name
        if not rp.exists():
            print(f"  skip {name} (not found)")
            continue
        changed = sync_file(rp, stats, args.dry_run)
        tag = "would update" if args.dry_run else "updated"
        print(f"  {tag}: {name}" if changed else f"  ok:      {name}")
        any_changed = any_changed or changed

    print("done" + (" (dry-run)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
