#!/usr/bin/env python3
"""Regression tests for static-analysis integration in check-code-review.py."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent
CHECKER = SCRIPTS / "check-code-review.py"
CHANGE = "demo-static"
EVIDENCE_REL = f"openspec/changes/{CHANGE}/design/evidence/static-analysis.json"


def make_gates() -> dict:
    return {
        "schema_version": "1.0",
        "project": "demo-project",
        "status": "DRAFT",
        "policy": {
            "blocking_severities": ["error"],
            "require_clean_exit": True,
            "waiver_file": "openspec/changes/<change-id>/design/static-waivers.json",
            "waiver": {"allowed": True, "requires_approver": True, "max_days": 90},
            "allow_network_install": False,
            "command_timeout_seconds": 600,
        },
        "stacks": [
            {
                "id": "app",
                "language": "python",
                "root": "app",
                "tools": [
                    {
                        "id": "lint",
                        "mode": "blocking",
                        "command": "ruff check .",
                        "configs": ["pyproject.toml"],
                    }
                ],
            }
        ],
    }


def make_static_evidence(exit_code: int = 0) -> dict:
    return {
        "schema_version": "1.0",
        "change_id": CHANGE,
        "source_revision": "abc123",
        "run_at": "2026-11-19T00:00:00Z",
        "gates_file": {
            "path": "docs/architecture/quality-gates.json",
            "sha256": "deadbeef",
        },
        "independent": False,
        "verifier_identity": "",
        "builder_identity": "builder",
        "results": [
            {
                "stack_id": "app",
                "tool": "lint",
                "command": "ruff check .",
                "cwd": "app",
                "exit_code": exit_code,
                "timed_out": False,
                "log": (
                    f"openspec/changes/{CHANGE}/design/evidence/static-analysis-logs/"
                    "app-lint.log"
                ),
                "configs": [{"path": "pyproject.toml", "sha256": "deadbeef"}],
                "mode": "blocking",
            }
        ],
        "waivers_applied": [],
        "verdict": "PASS" if exit_code == 0 else "FAIL",
    }


def review_text(static_section: bool = True, static_line: str = "| app | lint | `ruff check .` | exit 0 |") -> str:
    lines = [
        "# Code Review Evidence",
        "",
        f"- Change ID: {CHANGE}",
        "- Reviewer/tool: reviewer",
        "- Review date/commit: abc123",
        "- Review conclusion: PASS",
        "- Findings: none",
        "",
        "## Findings by severity",
        "",
        "| Severity | File/line | Finding | Resolution/evidence | Status |",
        "|---|---|---|---|---|",
        "",
        "## Spec compliance, security, data consistency, failure paths",
        "",
        "Reviewed against the Change spec.",
        "",
    ]
    if static_section:
        lines.extend(
            [
                "## Static analysis",
                "",
                "| Stack | Tool | Command | Exit |",
                "|---|---|---|---|",
                static_line,
                "",
            ]
        )
    return "\n".join(lines)


class CodeReviewStaticTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=SCRIPTS)
        self.root = Path(self._tmp.name)
        self.evidence_dir = self.root / "openspec/changes" / CHANGE / "design" / "evidence"
        self.evidence_dir.mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def write_gates(self) -> Path:
        path = self.root / "docs/architecture/quality-gates.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(make_gates(), ensure_ascii=False, indent=2), encoding="utf-8")
        (self.root / "app").mkdir(exist_ok=True)
        (self.root / "app/pyproject.toml").write_text("[tool.ruff]\n", encoding="utf-8")
        return path

    def write_review(self, static_section: bool = True, static_line: str = "| app | lint | `ruff check .` | exit 0 |") -> Path:
        path = self.evidence_dir / "code-review.md"
        path.write_text(review_text(static_section, static_line), encoding="utf-8")
        return path

    def write_static_evidence(self, exit_code: int = 0) -> Path:
        path = self.root / EVIDENCE_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(make_static_evidence(exit_code), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    def run_checker(self, root: Path | None = None) -> subprocess.CompletedProcess:
        args = [
            sys.executable,
            str(CHECKER),
            "--change",
            CHANGE,
            "--root",
            str(root or self.root),
        ]
        return subprocess.run(
            args, capture_output=True, text=True, encoding="utf-8", cwd=str(REPO_ROOT)
        )

    def assert_fails(self, result: subprocess.CompletedProcess, *needles: str) -> None:
        output = result.stdout + result.stderr
        self.assertEqual(1, result.returncode, output)
        for needle in needles:
            self.assertIn(needle.lower(), output.lower())

    def test_passing_fixture_returns_zero(self):
        self.write_gates()
        self.write_review()
        self.write_static_evidence()

        result = self.run_checker()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("Code review check passed", result.stdout)

    def test_missing_static_section_fails(self):
        self.write_gates()
        self.write_review(static_section=False)
        self.write_static_evidence()

        result = self.run_checker()

        self.assert_fails(result, "Static analysis")

    def test_nonzero_evidence_exit_code_fails(self):
        self.write_gates()
        self.write_review()
        self.write_static_evidence(exit_code=3)

        result = self.run_checker()

        self.assert_fails(result, "exit")

    def test_section_line_reports_wrong_exit_fails(self):
        self.write_gates()
        self.write_review(static_line="| app | lint | `ruff check .` | exit 3 |")
        self.write_static_evidence()

        result = self.run_checker()

        self.assert_fails(result, "exit 0")

    def test_section_line_missing_tool_fails(self):
        self.write_gates()
        self.write_review(static_line="| app | typecheck | `mypy .` | exit 0 |")
        self.write_static_evidence()

        result = self.run_checker()

        self.assert_fails(result, "lint")

    def test_nested_ids_do_not_satisfy_shorter_gate(self):
        # `app-web`/`lint-strict` must not satisfy the blocking `app`/`lint` gate.
        self.write_gates()
        self.write_review(static_line="| app-web | lint-strict | `ruff check .` | exit 0 |")
        self.write_static_evidence()

        result = self.run_checker()

        self.assert_fails(result, "app", "lint", "exit 0")

    def test_missing_static_evidence_fails(self):
        self.write_gates()
        self.write_review()

        result = self.run_checker()

        self.assert_fails(result, "static-analysis.json")

    def test_gates_absent_keeps_legacy_behavior(self):
        # No docs/architecture/quality-gates.json: the Static analysis section is optional.
        self.write_review(static_section=False)

        result = self.run_checker()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_chinese_project_root(self):
        chinese_root = self._tmp.name  # keep temp under scripts; use a non-ASCII subtree
        project = Path(chinese_root) / "项目"
        project.mkdir()
        self.root = project
        self.evidence_dir = project / "openspec/changes" / CHANGE / "design" / "evidence"
        self.evidence_dir.mkdir(parents=True)
        self.write_gates()
        self.write_review()
        self.write_static_evidence()

        result = self.run_checker(root=project)

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
