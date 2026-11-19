#!/usr/bin/env python3
"""Regression tests for quality_gates.py and check-quality-gates.py."""
from __future__ import annotations

import copy
import datetime
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent
CHECKER = SCRIPTS / "check-quality-gates.py"

sys.path.insert(0, str(SCRIPTS))
import quality_gates as qg


def make_gates() -> dict:
    """A minimal structurally valid gates document."""
    return {
        "schema_version": "1.0",
        "project": "demo-project",
        "status": "DRAFT",
        "policy": {
            "blocking_severities": ["error"],
            "require_clean_exit": True,
            "waiver_file": "openspec/changes/add-x/design/static-waivers.json",
            "waiver": {"allowed": True, "requires_approver": True, "max_days": 90},
            "allow_network_install": False,
        },
        "stacks": [
            {
                "id": "frontend",
                "language": "typescript",
                "root": "frontend",
                "tools": [
                    {
                        "id": "eslint",
                        "mode": "blocking",
                        "command": "npx --no-install eslint .",
                        "configs": ["eslint.config.js"],
                    }
                ],
            }
        ],
    }


TECHNOLOGY_DOC = (
    "# Technology Decisions\n\n"
    "## Static Analysis Toolchain\n\n"
    "The selected language is typescript with ESLint.\n"
)


class QualityGatesCliTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=SCRIPTS)
        self.root = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def write_gates(self, data: dict) -> None:
        path = self.root / "docs/architecture/quality-gates.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def write_technology(self, text: str) -> None:
        path = self.root / "docs/architecture/technology-decisions.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def run_checker(self, *flags: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(CHECKER), "--root", str(self.root), *flags],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

    def test_missing_gates_is_not_adopted_without_require_materialized(self):
        result = self.run_checker("--strict")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("QUALITY_GATES_NOT_ADOPTED", result.stdout)

    def test_missing_gates_fails_when_require_materialized(self):
        result = self.run_checker("--strict", "--require-materialized")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("file is missing", result.stdout)

    def test_valid_gates_strict_pass(self):
        self.write_gates(make_gates())
        self.write_technology(TECHNOLOGY_DOC)
        result = self.run_checker("--strict")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("QUALITY_GATES_CHECK_PASSED", result.stdout)

    def test_missing_schema_version_fails(self):
        gates = make_gates()
        del gates["schema_version"]
        self.write_gates(gates)
        result = self.run_checker()
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("ERROR:", result.stdout)
        self.assertIn("schema_version", result.stdout)

    def test_duplicate_stack_id_fails(self):
        gates = make_gates()
        duplicate = copy.deepcopy(gates["stacks"][0])
        duplicate["id"] = gates["stacks"][0]["id"]
        duplicate["tools"][0]["id"] = "tsc"
        gates["stacks"].append(duplicate)
        self.write_gates(gates)
        result = self.run_checker()
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("duplicate stack id", result.stdout)

    def test_absolute_or_parent_stack_root_fails(self):
        for bad_root in ("C:/x", "/x", "../x"):
            with self.subTest(bad_root=bad_root):
                gates = make_gates()
                gates["stacks"][0]["root"] = bad_root
                self.write_gates(gates)
                result = self.run_checker()
                self.assertEqual(1, result.returncode, result.stdout + result.stderr)
                self.assertIn("ERROR:", result.stdout)

    def test_network_command_rejected_unless_policy_allows(self):
        gates = make_gates()
        gates["stacks"][0]["tools"][0]["command"] = "npx eslint ."
        self.write_gates(gates)
        result = self.run_checker()
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("network", result.stdout.lower())

        gates["policy"]["allow_network_install"] = True
        self.write_gates(gates)
        result = self.run_checker()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

        gates = make_gates()
        gates["stacks"][0]["tools"][0]["command"] = "npx --no-install eslint ."
        self.write_gates(gates)
        result = self.run_checker()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_strict_requires_technology_section(self):
        self.write_gates(make_gates())

        result = self.run_checker("--strict")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)

        self.write_technology("This decision mentions typescript but has no heading.\n")
        result = self.run_checker("--strict")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)

        self.write_technology("## Static Analysis Toolchain\n\nNo language is named here.\n")
        result = self.run_checker("--strict")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)

        result = self.run_checker()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_materialized_requires_configs(self):
        self.write_gates(make_gates())

        result = self.run_checker("--require-materialized")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)

        result = self.run_checker()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

        (self.root / "frontend").mkdir()
        result = self.run_checker("--require-materialized")
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)

        (self.root / "frontend/eslint.config.js").write_text(
            "export default [];\n", encoding="utf-8"
        )
        result = self.run_checker("--require-materialized")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_chinese_stack_root_and_config(self):
        gates = make_gates()
        gates["stacks"][0]["root"] = "前端应用"
        gates["stacks"][0]["tools"][0]["configs"] = ["配置/eslint.config.js"]
        self.write_gates(gates)
        self.write_technology("## Static Analysis Toolchain\n\ntypescript\n")
        (self.root / "前端应用/配置").mkdir(parents=True)
        (self.root / "前端应用/配置/eslint.config.js").write_text(
            "export default [];\n", encoding="utf-8"
        )

        result = self.run_checker()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

        result = self.run_checker("--strict", "--require-materialized")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


class WaiverValidationTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=SCRIPTS)
        self.root = Path(self._tmp.name)
        self.gates = make_gates()
        (self.root / "src/legacy").mkdir(parents=True)
        (self.root / "src/legacy/x.ts").write_text("export const x = 1;\n", encoding="utf-8")

    def tearDown(self):
        self._tmp.cleanup()

    def waiver(self, **overrides) -> dict:
        waiver = {
            "id": "WAIVER-001",
            "stack": "frontend",
            "tool": "eslint",
            "file": "src/legacy/x.ts",
            "rule": "no-explicit-any",
            "reason": "Legacy code predates the static analysis gate",
            "owner": "frontend-owner",
            "approved_by": "tech-lead",
            "approved_at": "2026-11-01",
            "expires_at": "2026-12-31",
        }
        waiver.update(overrides)
        return waiver

    def validate(self, waivers, today=None) -> list[str]:
        if today is None:
            today = qg.today_iso()
        return qg.validate_waivers(waivers, self.root, self.gates, today)

    def test_waiver_expiry_boundary(self):
        today = qg.today_iso()
        yesterday = (
            datetime.date.fromisoformat(today) - datetime.timedelta(days=1)
        ).isoformat()

        errors = self.validate([self.waiver(expires_at=yesterday)], today)
        self.assertNotEqual([], errors)

        self.assertEqual([], self.validate([self.waiver(expires_at=today)], today))

        ten_days = (datetime.date.fromisoformat(today) + datetime.timedelta(days=10)).isoformat()
        twenty_days = (datetime.date.fromisoformat(today) + datetime.timedelta(days=20)).isoformat()
        errors = self.validate(
            [self.waiver(approved_at=twenty_days, expires_at=ten_days)], today
        )
        self.assertNotEqual([], errors)
        self.assertIn("approved_at", " ".join(errors))

    def test_waiver_path_escape_fails(self):
        for bad_file in ("../outside.ts", "C:/outside.ts", "/outside.ts"):
            with self.subTest(bad_file=bad_file):
                errors = self.validate([self.waiver(file=bad_file)])
                self.assertNotEqual([], errors)

    def test_waiver_unknown_stack_or_tool_fails(self):
        self.assertNotEqual([], self.validate([self.waiver(stack="unknown-stack")]))
        self.assertNotEqual([], self.validate([self.waiver(tool="unknown-tool")]))


class NetworkPatternTests(unittest.TestCase):
    """Direct coverage for the known auto-fetch command screen."""

    def test_known_fetch_forms_are_rejected(self):
        for command in (
            "pip install ruff",
            "python -m pip install ruff",
            "npm install",
            "npm ci",
            "pnpm install",
            "yarn add eslint",
            "yarn install",
            "go get ./...",
            "cargo install cargo-audit",
            "docker pull node:20",
            "mvn dependency:go-offline",
            "mvn test -U",
        ):
            with self.subTest(command=command):
                self.assertIsNotNone(qg.find_network_command(command))

    def test_offline_forms_are_allowed(self):
        for command in (
            "npx --no-install eslint .",
            "ruff check .",
            "mvn -o test",
            "docker run --rm node:20 --version",
            "pip list",
        ):
            with self.subTest(command=command):
                self.assertIsNone(qg.find_network_command(command))


if __name__ == "__main__":
    unittest.main(verbosity=2)
