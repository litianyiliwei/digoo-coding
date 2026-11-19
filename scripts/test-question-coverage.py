#!/usr/bin/env python3
"""Regression tests for the optional stage question-coverage checker."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECKER = Path(__file__).with_name("check-question-coverage.py")
STEP = "02-requirements-analysis"
LANDING = "docs/product/requirements-analysis.md#6. Non-Functional Requirements"


def base_items():
    return [
        {
            "item_id": "02-T02-01",
            "status": "answered",
            "landing": LANDING,
            "owner": "product-owner",
            "date": "2026-11-18",
        },
        {
            "item_id": "02-T11-01",
            "status": "open",
            "owner": "product-owner",
            "blocking": "Pilot site not confirmed",
            "open_question": "docs/product/open-questions.md",
        },
        {
            "item_id": "02-T08-01",
            "status": "n/a",
            "reason": "Not applicable in this release",
        },
        {
            "item_id": "03-T10-01",
            "status": "deferred",
            "reason": "No migration in this release",
            "approver": "technical-lead",
            "target_step": "07-detailed-design",
        },
        {
            "item_id": "CUSTOM-01",
            "status": "answered",
            "landing": "docs/product/requirements-analysis.md",
        },
    ]


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
        }
        if items is not None:
            evidence["question_coverage"] = items
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
    def test_omitted_block_passes(self):
        result = run_checker(None)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("QUESTION_COVERAGE_PASSED", result.stdout)

    def test_empty_block_passes(self):
        result = run_checker([])
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("QUESTION_COVERAGE_PASSED", result.stdout)

    def test_valid_block_passes(self):
        result = run_checker(base_items())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("QUESTION_COVERAGE_PASSED", result.stdout)

    def test_unknown_item_id_is_allowed(self):
        result = run_checker(base_items())
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_non_array_block_fails(self):
        result = run_checker("not-a-list")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must be an array", result.stdout)

    def test_duplicate_item_fails(self):
        items = base_items() + [base_items()[0]]
        result = run_checker(items)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate item_id", result.stdout)

    def test_entry_without_item_id_fails(self):
        items = base_items() + [{"status": "n/a", "reason": "x"}]
        result = run_checker(items)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("item_id is required", result.stdout)

    def test_answered_requires_landing(self):
        items = [{"item_id": "02-T02-01", "status": "answered"}]
        result = run_checker(items)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("landing is required", result.stdout)

    def test_answered_landing_file_must_exist(self):
        items = [{"item_id": "02-T02-01", "status": "answered", "landing": "docs/product/missing.md"}]
        result = run_checker(items)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("landing file missing", result.stdout)

    def test_answered_landing_heading_must_exist(self):
        items = [{"item_id": "02-T02-01", "status": "answered", "landing": LANDING + "-missing"}]
        result = run_checker(items)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("heading not found", result.stdout)

    def test_open_requires_owner_blocking_and_question(self):
        items = [{"item_id": "02-T11-01", "status": "open"}]
        result = run_checker(items)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("open requires owner", result.stdout)
        self.assertIn("open requires blocking", result.stdout)
        self.assertIn("open_question is required", result.stdout)

    def test_open_question_file_must_exist(self):
        items = [{
            "item_id": "02-T11-01",
            "status": "open",
            "owner": "product-owner",
            "blocking": "Pilot site not confirmed",
            "open_question": "docs/product/missing-questions.md",
        }]
        result = run_checker(items)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("open_question file missing", result.stdout)

    def test_na_requires_reason(self):
        items = [{"item_id": "02-T08-01", "status": "n/a"}]
        result = run_checker(items)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("n/a requires reason", result.stdout)

    def test_deferred_requires_reason_approver_and_target(self):
        items = [{"item_id": "03-T10-01", "status": "deferred"}]
        result = run_checker(items)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("deferred requires reason", result.stdout)
        self.assertIn("deferred requires approver", result.stdout)
        self.assertIn("deferred requires target_step", result.stdout)

    def test_chinese_status_alias_is_accepted(self):
        items = [{"item_id": "02-T02-01", "status": "已答", "landing": LANDING}]
        result = run_checker(items)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_bad_date_fails(self):
        items = [{
            "item_id": "02-T02-01",
            "status": "answered",
            "landing": LANDING,
            "date": "2026/11/18",
        }]
        result = run_checker(items)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("date must be YYYY-MM-DD", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
