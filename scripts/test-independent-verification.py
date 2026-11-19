#!/usr/bin/env python3
"""Regression tests for independent-verifier evidence gate.

Covers the legacy report/evidence rules plus static-analysis integration
(`static_checks`) that activates when `docs/architecture/quality-gates.json`
exists. All integration path resolution and fail-closed behavior is exercised
through the real checker subprocess.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent
CHECKER = SCRIPTS / "check-independent-verification.py"
CHANGE = "test-change"
EVIDENCE_REL = f"openspec/changes/{CHANGE}/design/evidence/static-analysis-independent.json"

REPORT_TEXT = (
    "判定：PASS\n"
    "## 1. 验证范围\n"
    "## 2. 验收标准\n"
    "## 3. 测试与检查\n"
    "## 7. 最终判定\n"
)


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


def make_static_evidence(*, independent: bool = True, verdict: str = "PASS",
                         verifier: str = "verifier-session",
                         builder: str = "builder-session") -> dict:
    return {
        "schema_version": "1.0",
        "change_id": CHANGE,
        "source_revision": "abc123",
        "run_at": "2026-11-19T00:00:00Z",
        "gates_file": {
            "path": "docs/architecture/quality-gates.json",
            "sha256": "deadbeef",
        },
        "independent": independent,
        "verifier_identity": verifier,
        "builder_identity": builder,
        "results": [
            {
                "stack_id": "app",
                "tool": "lint",
                "command": "ruff check .",
                "cwd": "app",
                "exit_code": 0,
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
        "verdict": verdict,
    }


def make_static_check(**overrides) -> dict:
    check = {
        "stack_id": "app",
        "tool": "lint",
        "command": "ruff check .",
        "exit_code": 0,
        "result": "PASS",
        "evidence": EVIDENCE_REL,
    }
    check.update(overrides)
    return check


class IndependentVerificationTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=SCRIPTS)
        self.root = Path(self._tmp.name)
        self.report = self.root / "report.md"
        self.report.write_text(REPORT_TEXT, encoding="utf-8")
        self.log = self.root / "test.log"
        self.log.write_text("1 passed\n", encoding="utf-8")
        self.payload = {
            "change_id": CHANGE,
            "verdict": "PASS",
            "source_revision": "abc123",
            "revision_stable": True,
            "read_only": True,
            "verifier_identity": "verifier-session",
            "builder_identity": "builder-session",
            "acceptance_checks": [
                {"id": "AC-1", "result": "PASS", "evidence": "tests/test_ac.py::test_ok"}
            ],
            "test_runs": [{"command": "pytest -q", "exit_code": 0, "log": str(self.log)}],
            "findings": [],
        }
        self.evidence = self.root / "evidence.json"

    def tearDown(self):
        self._tmp.cleanup()

    def write_evidence(self, payload: dict | None = None) -> None:
        self.evidence.write_text(json.dumps(payload or self.payload), encoding="utf-8")

    def run_checker(self, root: Path | None = None) -> subprocess.CompletedProcess:
        args = [
            sys.executable,
            str(CHECKER),
            "--report",
            str(self.report),
            "--evidence",
            str(self.evidence),
            "--root",
            str(root or self.root),
        ]
        return subprocess.run(
            args, capture_output=True, text=True, encoding="utf-8", cwd=str(REPO_ROOT)
        )

    def write_gates(self, root: Path | None = None) -> None:
        root = root or self.root
        path = root / "docs/architecture/quality-gates.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(make_gates(), ensure_ascii=False, indent=2), encoding="utf-8")
        (root / "app").mkdir(exist_ok=True)
        (root / "app/pyproject.toml").write_text("[tool.ruff]\n", encoding="utf-8")

    def write_static_evidence(self, data: dict | None = None, root: Path | None = None) -> None:
        root = root or self.root
        path = root / EVIDENCE_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(data or make_static_evidence(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def assert_fails(self, result: subprocess.CompletedProcess, *needles: str) -> None:
        output = result.stdout + result.stderr
        self.assertNotEqual(0, result.returncode, output)
        for needle in needles:
            self.assertIn(needle.lower(), output.lower())

    # --- legacy behavior -------------------------------------------------
    def test_legacy_fixture_without_gates_passes(self):
        self.write_evidence()

        result = self.run_checker()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_failing_test_run_fails(self):
        self.payload["test_runs"][0]["exit_code"] = 1
        self.write_evidence()

        result = self.run_checker()

        self.assert_fails(result)

    def test_non_read_only_fails(self):
        self.payload["read_only"] = False
        self.write_evidence()

        result = self.run_checker()

        self.assert_fails(result)

    def test_gates_absent_ignores_present_static_checks(self):
        self.payload["static_checks"] = [make_static_check(result="NOT_RUN", exit_code=1)]
        self.write_evidence()

        result = self.run_checker()

        # Without gates the static block is optional and not enforced.
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    # --- static-analysis integration -------------------------------------
    def test_valid_static_checks_pass(self):
        self.payload["static_checks"] = [make_static_check()]
        self.write_evidence()
        self.write_gates()
        self.write_static_evidence()

        result = self.run_checker()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("INDEPENDENT_VERIFICATION_PASS", result.stdout)

    def test_missing_static_checks_fails(self):
        self.write_evidence()
        self.write_gates()
        self.write_static_evidence()

        result = self.run_checker()

        self.assert_fails(result, "static_checks")

    def test_wrong_static_set_fails(self):
        self.payload["static_checks"] = [make_static_check(tool="mypy", command="mypy .")]
        self.write_evidence()
        self.write_gates()
        self.write_static_evidence()

        result = self.run_checker()

        self.assert_fails(result, "mypy", "lint")

    def test_not_run_result_fails(self):
        self.payload["static_checks"] = [make_static_check(result="NOT_RUN")]
        self.write_evidence()
        self.write_gates()
        self.write_static_evidence()

        result = self.run_checker()

        self.assert_fails(result, "NOT_RUN")

    def test_nonzero_exit_code_fails(self):
        self.payload["static_checks"] = [make_static_check(exit_code=2)]
        self.write_evidence()
        self.write_gates()
        self.write_static_evidence()

        result = self.run_checker()

        self.assert_fails(result, "exit_code")

    def test_evidence_without_independent_fails(self):
        self.payload["static_checks"] = [make_static_check()]
        self.write_evidence()
        self.write_gates()
        self.write_static_evidence(make_static_evidence(independent=False))

        result = self.run_checker()

        self.assert_fails(result, "independent")

    def test_static_evidence_verdict_fail_fails(self):
        self.payload["static_checks"] = [make_static_check()]
        self.write_evidence()
        self.write_gates()
        self.write_static_evidence(make_static_evidence(verdict="FAIL"))

        result = self.run_checker()

        self.assert_fails(result, "verdict")

    def test_static_evidence_identical_identities_fail(self):
        self.payload["static_checks"] = [make_static_check()]
        self.write_evidence()
        self.write_gates()
        self.write_static_evidence(make_static_evidence(verifier="same", builder="same"))

        result = self.run_checker()

        self.assert_fails(result, "distinct")

    def test_static_evidence_missing_file_fails(self):
        self.payload["static_checks"] = [make_static_check()]
        self.write_evidence()
        self.write_gates()

        result = self.run_checker()

        self.assert_fails(result, "does not exist")

    def test_static_evidence_path_escape_fails(self):
        self.payload["static_checks"] = [make_static_check(evidence="../../outside.json")]
        self.write_evidence()
        self.write_gates()
        self.write_static_evidence()

        result = self.run_checker()

        self.assert_fails(result, "escape")


if __name__ == "__main__":
    unittest.main(verbosity=2)
