#!/usr/bin/env python3
"""Validate references/tool-catalog.json against references/repo-schema.md.

`repo-schema.md` says "The discovery script validates before writing" — this
module IS that validator. It encodes the documented Validation Rules plus the
required-fields table:

    R1  category is exactly one of the five canonical enum values
    R2  repo_url starts with https://github.com/
    R3  stars is a non-negative integer
    R4  last_updated parses as ISO date and is within the last 5 years
        (older = abandoned, non-protected entries are dropped)
    R5  use_cases is a list of 1-3 non-empty strings, each <= 80 chars
    R6  no duplicate repo_url across entries
    R7  one_line_description is a non-empty string <= 200 chars
    RF  every required field from the schema table is present
        (language/license/homepage may be null)

Severity model — protection beats pruning, mirroring the LLM-judging guards:

    ERROR    hard violation on a non-protected entry. discover_repos.py
             drops such entries before writing; the CLI exits 1.
    WARNING  same violation on a protected entry (verified / favorite /
             manually-added) — never dropped, flaw is surfaced instead.
             Truncatable fields (use_cases, one_line_description, stars)
             are auto-repaired first, protected or not.
    R6 duplicates are always repaired (keep first), matching discovery's
    by_url dedupe semantics.

CLI:
    python scripts/validate_catalog.py [--json PATH]
Exit 0 = valid (warnings allowed), 1 = errors or unreadable file.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
DEFAULT_JSON = SKILL_ROOT / "references" / "tool-catalog.json"

CATEGORIES = ("web-scraper", "dynamic-scraper", "api-collector", "agent-skill", "dataset")
REQUIRED_FIELDS = (
    "repo_url", "full_name", "name", "category", "one_line_description",
    "stars", "language", "topics", "last_updated", "discovered_at",
    "license", "homepage", "verified", "use_cases",
)
NULLABLE_FIELDS = {"language", "license", "homepage"}
STALE_DAYS = 5 * 365      # R4: older than ~5 years = abandoned
MAX_DESC = 200            # R7
MAX_USE_CASES = 3         # R5
MAX_USE_CASE_LEN = 80     # R5


def is_protected(entry: dict) -> bool:
    """Human-curated entries are never dropped, only warned about."""
    return bool(entry.get("verified") or entry.get("favorite")
                or "manually-added" in (entry.get("tags") or []))


def _parse_day(value) -> date | None:
    try:
        return date.fromisoformat(str(value)[:10])
    except (TypeError, ValueError):
        return None


def validate_entry(entry: dict, today: date | None = None) -> list[tuple[str, str, str]]:
    """Check one entry. Returns [(severity, rule, message), ...]."""
    today = today or date.today()
    issues: list[tuple[str, str, str]] = []
    sev = "WARNING" if is_protected(entry) else "ERROR"
    name = entry.get("full_name") or entry.get("repo_url") or "<unnamed>"

    for field in REQUIRED_FIELDS:
        if field not in entry:
            issues.append((sev, "RF", f"{name}: missing required field '{field}'"))
        elif entry[field] is None and field not in NULLABLE_FIELDS:
            issues.append((sev, "RF", f"{name}: required field '{field}' is null"))

    if entry.get("category") not in CATEGORIES:
        issues.append((sev, "R1", f"{name}: category {entry.get('category')!r} not in {CATEGORIES}"))

    url = entry.get("repo_url") or ""
    if not url.startswith("https://github.com/"):
        issues.append((sev, "R2", f"{name}: repo_url {url!r} does not start with https://github.com/"))

    stars = entry.get("stars")
    if isinstance(stars, bool) or not isinstance(stars, int) or stars < 0:
        issues.append((sev, "R3", f"{name}: stars {stars!r} is not a non-negative integer"))

    updated = _parse_day(entry.get("last_updated"))
    if updated is None:
        issues.append((sev, "R4", f"{name}: last_updated {entry.get('last_updated')!r} is not an ISO date"))
    elif (today - updated).days > STALE_DAYS:
        issues.append((sev, "R4", f"{name}: last_updated {updated} is stale (> {STALE_DAYS // 365} years, abandoned)"))

    uc = entry.get("use_cases")
    if (not isinstance(uc, list) or not uc or len(uc) > MAX_USE_CASES
            or any(not isinstance(u, str) or not u.strip() for u in uc)):
        issues.append((sev, "R5", f"{name}: use_cases must be 1-{MAX_USE_CASES} non-empty strings, got {uc!r}"))
    elif any(len(u) > MAX_USE_CASE_LEN for u in uc):
        issues.append((sev, "R5", f"{name}: a use case exceeds {MAX_USE_CASE_LEN} chars"))

    desc = entry.get("one_line_description")
    if not isinstance(desc, str) or not desc.strip():
        issues.append((sev, "R7", f"{name}: one_line_description is empty"))
    elif len(desc) > MAX_DESC:
        issues.append((sev, "R7", f"{name}: one_line_description is {len(desc)} chars (max {MAX_DESC})"))

    return issues


def validate_doc(doc, today: date | None = None) -> list[tuple[str, str, str]]:
    """Validate the whole catalog document, including duplicates (R6)."""
    if not isinstance(doc, dict):
        return [("ERROR", "DOC", "catalog root is not a JSON object")]
    issues: list[tuple[str, str, str]] = []
    version = doc.get("schema_version")
    if version is None:
        issues.append(("ERROR", "DOC", "missing top-level schema_version"))
    elif version != 1:
        issues.append(("WARNING", "DOC", f"schema_version {version!r} != 1; validator implements v1"))
    entries = doc.get("entries")
    if not isinstance(entries, list):
        issues.append(("ERROR", "DOC", "'entries' is not a list"))
        return issues
    seen: dict[str, int] = {}
    for i, entry in enumerate(entries):
        issues.extend(validate_entry(entry, today))
        url = entry.get("repo_url")
        if url:
            if url in seen:
                issues.append(("ERROR", "R6", f"duplicate repo_url {url} (entries #{seen[url]} and #{i})"))
            else:
                seen[url] = i
    return issues


def _repair(entry: dict) -> bool:
    """Auto-repair truncatable/type-coercible fields in place. True if changed."""
    changed = False
    uc = entry.get("use_cases")
    if isinstance(uc, list):
        fixed = [u[:MAX_USE_CASE_LEN] for u in uc[:MAX_USE_CASES]]
        if fixed != uc:
            entry["use_cases"] = fixed
            changed = True
    desc = entry.get("one_line_description")
    if isinstance(desc, str) and len(desc) > MAX_DESC:
        entry["one_line_description"] = desc[:MAX_DESC]
        changed = True
    stars = entry.get("stars")
    if isinstance(stars, bool) or not isinstance(stars, int) or stars < 0:
        entry["stars"] = 0
        changed = True
    return changed


def enforce(doc: dict, today: date | None = None) -> tuple[dict, list[str]]:
    """Make the catalog conform: repair, drop failing non-protected entries,
    keep protected ones with a warning. Returns (doc, warnings)."""
    warnings: list[str] = []
    entries = doc.get("entries")
    if not isinstance(entries, list):
        return doc, ["catalog 'entries' is not a list; nothing to enforce"]

    kept: list[dict] = []
    seen: set[str] = set()
    for entry in entries:
        name = entry.get("full_name") or entry.get("repo_url") or "<unnamed>"
        url = entry.get("repo_url")
        if url:
            if url in seen:
                warnings.append(f"R6 duplicate dropped: {name}")
                continue
            seen.add(url)
        if _repair(entry):
            warnings.append(f"auto-repaired (truncated/coerced): {name}")
        issues = validate_entry(entry, today)
        if not issues:
            kept.append(entry)
            continue
        errors = [m for s, _, m in issues if s == "ERROR"]
        if errors and not is_protected(entry):
            warnings.append(f"dropped (schema): {name} — {'; '.join(errors)}")
            continue
        warnings.append(f"kept with flaws (protected): {name} — {'; '.join(m for _, _, m in issues)}")
        kept.append(entry)

    doc["entries"] = kept
    return doc, warnings


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--json", type=Path, default=DEFAULT_JSON,
                   help="catalog JSON to validate (default: references/tool-catalog.json)")
    args = p.parse_args(argv)

    try:
        doc = json.loads(args.json.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001 — any read/parse failure is a CLI failure
        print(f"error: cannot read {args.json}: {e}")
        return 1

    issues = validate_doc(doc)
    for severity, rule, message in issues:
        print(f"{severity:7} [{rule}] {message}")
    n = len(doc.get("entries", [])) if isinstance(doc, dict) else "?"
    errors = sum(1 for s, _, _ in issues if s == "ERROR")
    warns = sum(1 for s, _, _ in issues if s == "WARNING")
    print(f"{n} entries checked: {errors} error(s), {warns} warning(s)")
    if errors:
        print("INVALID — fix the repo-schema.md violations above")
        return 1
    print("valid against references/repo-schema.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
