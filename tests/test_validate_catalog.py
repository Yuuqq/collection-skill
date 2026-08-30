"""Tests for scripts/validate_catalog.py — the repo-schema.md enforcement gate.

Run from the repo root:
    python -m unittest discover -s tests -v
Stdlib-only (unittest), so it runs anywhere Python 3.10+ does.
"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import validate_catalog as vc  # noqa: E402

TODAY = date(2026, 8, 31)


def make_entry(**overrides) -> dict:
    """A fully valid entry; tests override individual fields."""
    entry = {
        "repo_url": "https://github.com/owner/repo",
        "full_name": "owner/repo",
        "name": "repo",
        "category": "web-scraper",
        "one_line_description": "A scraper",
        "stars": 10,
        "language": "Python",
        "topics": ["scraper"],
        "last_updated": (TODAY - timedelta(days=30)).isoformat(),
        "discovered_at": TODAY.isoformat(),
        "license": "MIT",
        "homepage": None,
        "verified": False,
        "use_cases": ["scrape things"],
    }
    entry.update(overrides)
    return entry


def rules(issues) -> list[str]:
    return [r for _sev, r, _msg in issues]


class ValidateEntryTests(unittest.TestCase):
    def test_valid_entry_has_no_issues(self):
        self.assertEqual(vc.validate_entry(make_entry(), TODAY), [])

    def test_rule_ids_map_to_schema_doc(self):
        cases = [
            ("R1", make_entry(category="scraper")),
            ("R2", make_entry(repo_url="https://gitlab.com/owner/repo")),
            ("R3", make_entry(stars=-1)),
            ("R4", make_entry(last_updated=(TODAY - timedelta(days=6 * 365)).isoformat())),
            ("R4", make_entry(last_updated="not-a-date")),
            ("R5", make_entry(use_cases=[])),
            ("R5", make_entry(use_cases=["x" * 81])),
            ("R7", make_entry(one_line_description="")),
            ("R7", make_entry(one_line_description="x" * 201)),
            ("RF", make_entry(stars=None)),
        ]
        for expected_rule, entry in cases:
            with self.subTest(rule=expected_rule, entry=entry):
                self.assertIn(expected_rule, rules(vc.validate_entry(entry, TODAY)))

    def test_nullable_fields_may_be_null(self):
        issues = vc.validate_entry(
            make_entry(language=None, license=None, homepage=None), TODAY)
        self.assertEqual(issues, [])

    def test_unprotected_violations_are_errors(self):
        issues = vc.validate_entry(make_entry(stars=-1), TODAY)
        self.assertTrue(all(s == "ERROR" for s, _r, _m in issues))

    def test_protected_violations_are_warnings(self):
        for protected in ({"verified": True},
                          {"favorite": True},
                          {"tags": ["manually-added"]}):
            with self.subTest(protected=protected):
                entry = make_entry(stars=-1, **protected)
                issues = vc.validate_entry(entry, TODAY)
                self.assertTrue(issues)
                self.assertTrue(all(s == "WARNING" for s, _r, _m in issues))


class ValidateDocTests(unittest.TestCase):
    def test_doc_shape(self):
        self.assertEqual(rules(vc.validate_doc([], TODAY)), ["DOC"])       # not an object
        self.assertIn("DOC", rules(vc.validate_doc({"entries": []}, TODAY)))  # no schema_version

    def test_unknown_schema_version_warns_not_errors(self):
        issues = vc.validate_doc({"schema_version": 2, "entries": []}, TODAY)
        self.assertTrue(all(s == "WARNING" for s, _r, _m in issues))

    def test_duplicate_repo_url_is_r6(self):
        doc = {"schema_version": 1,
               "entries": [make_entry(), make_entry(stars=99)]}
        self.assertIn("R6", rules(vc.validate_doc(doc, TODAY)))


class EnforceTests(unittest.TestCase):
    def test_drops_unprotected_invalid_entry(self):
        doc = {"schema_version": 1,
               "entries": [make_entry(), make_entry(full_name="owner/bad", repo_url="https://github.com/owner/bad", category="nope")]}
        doc, warnings = vc.enforce(doc, TODAY)
        self.assertEqual([e["full_name"] for e in doc["entries"]], ["owner/repo"])
        self.assertTrue(any("dropped" in w for w in warnings))

    def test_keeps_protected_invalid_entry_with_warning(self):
        # category is not auto-repairable, so the protected entry survives with a flaw
        doc = {"schema_version": 1,
               "entries": [make_entry(category="nope", verified=True)]}
        doc, warnings = vc.enforce(doc, TODAY)
        self.assertEqual(len(doc["entries"]), 1)
        self.assertTrue(any("protected" in w for w in warnings))

    def test_repairs_protected_entry_instead_of_warning(self):
        doc = {"schema_version": 1,
               "entries": [make_entry(stars=-1, verified=True)]}
        doc, warnings = vc.enforce(doc, TODAY)
        self.assertEqual(doc["entries"][0]["stars"], 0)
        self.assertTrue(any("auto-repaired" in w for w in warnings))

    def test_repairs_truncatable_fields(self):
        entry = make_entry(use_cases=["a" * 100, "b", "c", "d"],
                           one_line_description="x" * 250)
        doc = {"schema_version": 1, "entries": [entry]}
        doc, warnings = vc.enforce(doc, TODAY)
        kept = doc["entries"][0]
        self.assertEqual(len(kept["use_cases"]), 3)
        self.assertEqual(len(kept["use_cases"][0]), 80)
        self.assertEqual(len(kept["one_line_description"]), 200)
        self.assertTrue(any("auto-repaired" in w for w in warnings))

    def test_dedupes_keep_first(self):
        doc = {"schema_version": 1,
               "entries": [make_entry(stars=1), make_entry(stars=99)]}
        doc, warnings = vc.enforce(doc, TODAY)
        self.assertEqual(len(doc["entries"]), 1)
        self.assertEqual(doc["entries"][0]["stars"], 1)  # first wins, like by_url
        self.assertTrue(any("duplicate" in w for w in warnings))

    def test_clean_catalog_passes_untouched(self):
        doc = {"schema_version": 1, "entries": [make_entry(), make_entry(full_name="o/r2", repo_url="https://github.com/o/r2")]}
        doc2, warnings = vc.enforce(doc, TODAY)
        self.assertEqual(len(doc2["entries"]), 2)
        self.assertEqual(warnings, [])


class CliTests(unittest.TestCase):
    def _run_on(self, doc) -> int:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False,
                                         encoding="utf-8") as f:
            json.dump(doc, f, ensure_ascii=False)
            path = f.name
        try:
            with mock.patch.object(sys, "argv", ["validate_catalog.py", "--json", path]):
                return vc.main()
        finally:
            Path(path).unlink(missing_ok=True)

    def test_exit_0_on_valid(self):
        self.assertEqual(self._run_on({"schema_version": 1, "entries": [make_entry()]}), 0)

    def test_exit_1_on_errors(self):
        self.assertEqual(self._run_on({"schema_version": 1, "entries": [make_entry(stars=-1)]}), 1)

    def test_exit_0_on_warnings_only(self):
        self.assertEqual(
            self._run_on({"schema_version": 1, "entries": [make_entry(stars=-1, verified=True)]}), 0)

    def test_exit_1_on_unreadable_file(self):
        with mock.patch.object(sys, "argv", ["validate_catalog.py", "--json", "nope.json"]):
            self.assertEqual(vc.main(), 1)


if __name__ == "__main__":
    unittest.main()
