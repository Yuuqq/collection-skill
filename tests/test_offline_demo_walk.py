"""The offline demo walk must follow the current fast path and stay offline."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "offline_demo_walk.py"


class OfflineDemoWalkTests(unittest.TestCase):
    def test_self_test_exits_clean(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--self-test"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        self.assertIn("SELF-TEST OK", result.stdout)
        self.assertIn("OFFLINE PREVIEW", result.stdout)
        self.assertIn("通用五类菜单: 不展示", result.stdout)
        self.assertIn("未运行", result.stdout)
        self.assertNotIn("Crawled:", result.stdout)


if __name__ == "__main__":
    unittest.main()
