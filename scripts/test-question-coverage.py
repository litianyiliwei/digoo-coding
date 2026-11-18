#!/usr/bin/env python3
"""Regression tests for the stage question-coverage checker."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from question_coverage import DEFAULT_POLICY

CHECKER = Path(__file__).with_name("check-question-coverage.py")
STEP = "02-requirements-analysis"
ITEMS = DEFAULT_POLICY["stages"][STEP]["required_items"]
LANDING = "docs/product/requirements-analysis.md#6. Non-Functional Requirements"


def base_items():
    items = []
    for index, item_id in enumerate(ITEMS):
        if index == 0:
            items.append({
                "item_id": item_id,
                "status": "answered",
                "landing": LANDING,
                "owner": "product-owner",
                "date": "2026-11-18",
            })
        elif index == 1:
            items.append({
                "item_id": item_id,
                "status": "open",
                "owner": "product-owner",
                "blocking": "Pilot site not confirmed",
                "open_question": "docs/product/open-questions.md",
            })
        elif index == 2:
            items.append({
                "item_id": item_id,
                "status": "n/a",
                "reason": "Not applicable in this release",
            })
        else:
            items.append({
                "item_id": item_id,
                "status": "answered",
                "landing": "docs/product/requirements-analysis.md",
            })
    return items


def run_checker(items):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "docs/product").mkdir(parents=True, exist_ok=True)
        (root / "docs/product/requirements-analysis.md").write_text(
            "# Requirements\n\n## 6. Non-Functional Requirements\n\nPENDING\n",
            encoding="utf-8",
        )
        (root / "docs/product/open-questions.md").write_text(
            "# Open Questions\n\n| Q-001 | PENDING | owner | condition |\n",
            encoding="utf-8",
        )
        evidence = {
            "step_id": STEP,
            "change_id": None,
            "question_coverage": items,
        }
        ev_path = root / "workflow/evidence/02.json"
        ev_path.parent.mkdir(parents=True, exist_ok=True)
        ev_path.write_text(json.dumps(evidence, ensure_ascii=False), encoding="utf-8")
        return subprocess.run(
            [
                sys.executable,
                str(CHECKER),
                "--root",
                str(root),
                "--step",
                STEP,
                "--evidence",
                str(ev_path),
            ],
            capture_output=True,
            text=True,
        )


class QuestionCoverageTests(unittest.TestCase):
    def test_valid_coverage_passes(self):
        result = run_checker(base_items())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("QUESTION_COVERAGE_PASSED", result.stdout)

    def test_missing_item_fails(self):
        items = base_items()[:-1]
        result = run_checker(items)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing required items", result.stdout)

    def test_duplicate_item_fails(self):
        items = base_items() + [base_items()[0]]
        result = run_checker(items)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate item_id", result.stdout)

    def test_unknown_item_fails(self):
        items = base_items() + [{"item_id": "02-T99-99", "status": "answered", "landing": LANDING}]
        result = run_checker(items)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unknown item_id", result.stdout)

    def test_answered_requires_landing(self):
        items = base_items()
        items[0] = {"item_id": ITEMS[0], "status": "answered"}
        result = run_checker(items)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("landing is required", result.stdout)

    def test_answered_landing_file_must_exist(self):
        items = base_items()
        items[0] = {"item_id": ITEMS[0], "status": "answered", "landing": "docs/product/missing.md"}
        result = run_checker(items)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("landing file missing", result.stdout)

    def test_answered_landing_heading_must_exist(self):
        items = base_items()
        items[0] = {"item_id": ITEMS[0], "status": "answered", "landing": LANDING + "-missing"}
        result = run_checker(items)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("heading not found", result.stdout)

    def test_open_requires_owner_blocking_and_question(self):
        items = base_items()
        items[1] = {"item_id": ITEMS[1], "status": "open"}
        result = run_checker(items)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("open requires owner", result.stdout)
        self.assertIn("open requires blocking", result.stdout)
        self.assertIn("open_question is required", result.stdout)

    def test_open_question_file_must_exist(self):
        items = base_items()
        items[1] = {
            "item_id": ITEMS[1],
            "status": "open",
            "owner": "product-owner",
            "blocking": "Pilot site not confirmed",
            "open_question": "docs/product/missing-questions.md",
        }
        result = run_checker(items)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("open_question file missing", result.stdout)

    def test_na_requires_reason(self):
        items = base_items()
        items[2] = {"item_id": ITEMS[2], "status": "n/a"}
        result = run_checker(items)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("n/a requires reason", result.stdout)

    def test_deferred_requires_reason_approver_and_target(self):
        items = base_items()
        items[3] = {"item_id": ITEMS[3], "status": "deferred"}
        result = run_checker(items)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("deferred requires reason", result.stdout)
        self.assertIn("deferred requires approver", result.stdout)
        self.assertIn("deferred requires target_step", result.stdout)

    def test_chinese_status_alias_is_accepted(self):
        items = base_items()
        items[0] = {"item_id": ITEMS[0], "status": "已答", "landing": LANDING}
        result = run_checker(items)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_bad_date_fails(self):
        items = base_items()
        items[0] = {"item_id": ITEMS[0], "status": "answered", "landing": LANDING, "date": "2026/11/18"}
        result = run_checker(items)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("date must be YYYY-MM-DD", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
