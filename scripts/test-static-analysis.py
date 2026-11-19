#!/usr/bin/env python3
"""Regression tests for run-quality-gates.py (checker cases added in Task 3)."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent
RUNNER = SCRIPTS / "run-quality-gates.py"
CHECKER = SCRIPTS / "check-static-analysis.py"

sys.path.insert(0, str(SCRIPTS))
import quality_gates as qg

CHANGE_ID = "demo"
EVIDENCE_REL = f"openspec/changes/{CHANGE_ID}/design/evidence/static-analysis.json"
INDEPENDENT_EVIDENCE_REL = (
    f"openspec/changes/{CHANGE_ID}/design/evidence/static-analysis-independent.json"
)
WAIVERS_REL = f"openspec/changes/{CHANGE_ID}/design/static-waivers.json"
PYTHON = f'"{sys.executable}"'


def python_command(code: str) -> str:
    """A gate command that runs the current interpreter with ``code``."""
    return f'{PYTHON} -c "{code}"'


def make_gates(stacks: list[dict], *, command_timeout_seconds: int | None = None) -> dict:
    """A minimal, structurally valid gates document."""
    policy = {
        "blocking_severities": ["error"],
        "require_clean_exit": True,
        "waiver_file": "openspec/changes/<change-id>/design/static-waivers.json",
        "waiver": {"allowed": True, "requires_approver": True, "max_days": 90},
        "allow_network_install": False,
    }
    if command_timeout_seconds is not None:
        policy["command_timeout_seconds"] = command_timeout_seconds
    return {
        "schema_version": "1.0",
        "project": "demo-project",
        "status": "DRAFT",
        "policy": policy,
        "stacks": stacks,
    }


class RunnerTestBase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=SCRIPTS)
        self.root = Path(self._tmp.name)
        (self.root / "openspec/changes" / CHANGE_ID).mkdir(parents=True)

    def tearDown(self):
        self._tmp.cleanup()

    def write_gates(self, data: dict) -> Path:
        path = self.root / qg.GATES_REL
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def materialize(self, stack_root: str, configs: list[str]) -> None:
        stack_dir = self.root / stack_root
        stack_dir.mkdir(parents=True, exist_ok=True)
        for config in configs:
            config_path = stack_dir / config
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text("export default [];\n", encoding="utf-8")

    def run_runner(
        self,
        *flags: str,
        output: str = EVIDENCE_REL,
        source_revision: str | None = "test-rev",
    ) -> subprocess.CompletedProcess:
        args = [
            sys.executable,
            str(RUNNER),
            CHANGE_ID,
            "--root",
            str(self.root),
            "--output",
            output,
        ]
        if source_revision is not None:
            args.extend(["--source-revision", source_revision])
        args.extend(flags)
        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(REPO_ROOT),
        )

    def evidence(self, output: str = EVIDENCE_REL) -> dict:
        path = self.root / output
        self.assertTrue(path.is_file(), f"evidence file missing: {path}")
        return json.loads(path.read_text(encoding="utf-8"))

    def one_tool_stack(
        self,
        command: str,
        *,
        stack_id: str = "app",
        stack_root: str = "app",
        mode: str = "blocking",
        configs: list[str] | None = None,
    ) -> dict:
        return {
            "id": stack_id,
            "language": "python",
            "root": stack_root,
            "tools": [
                {
                    "id": "lint",
                    "mode": mode,
                    "command": command,
                    "configs": configs or ["eslint.config.js"],
                }
            ],
        }


class RunnerTests(RunnerTestBase):
    def test_runner_pass_emits_evidence(self):
        gates_path = self.write_gates(
            make_gates([self.one_tool_stack(python_command("import sys; sys.exit(0)"))])
        )
        self.materialize("app", ["eslint.config.js"])

        result = self.run_runner("--identity", "builder")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        evidence = self.evidence()
        self.assertEqual("PASS", evidence["verdict"])
        self.assertEqual(CHANGE_ID, evidence["change_id"])
        self.assertEqual("test-rev", evidence["source_revision"])
        self.assertEqual("builder", evidence["builder_identity"])
        self.assertFalse(evidence["independent"])
        self.assertEqual([], evidence["waivers_applied"])
        self.assertEqual(1, len(evidence["results"]))
        recorded = evidence["results"][0]
        self.assertEqual(0, recorded["exit_code"])
        self.assertFalse(recorded["timed_out"])
        self.assertEqual("app", recorded["cwd"])
        self.assertEqual("blocking", recorded["mode"])
        self.assertIn("path", recorded["configs"][0])
        self.assertNotIn("blocked_reason", recorded)

        log_path = self.root / recorded["log"]
        self.assertTrue(log_path.is_file(), f"log file missing: {log_path}")
        self.assertNotEqual("", log_path.read_text(encoding="utf-8"))

        self.assertEqual(
            qg.sha256_file(gates_path), evidence["gates_file"]["sha256"]
        )
        self.assertEqual(qg.GATES_REL, evidence["gates_file"]["path"])

    def test_runner_failing_tool_returns_nonzero(self):
        self.write_gates(
            make_gates([self.one_tool_stack(python_command("import sys; sys.exit(3)"))])
        )
        self.materialize("app", ["eslint.config.js"])

        result = self.run_runner()

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        evidence = self.evidence()
        self.assertEqual("FAIL", evidence["verdict"])
        self.assertEqual(3, evidence["results"][0]["exit_code"])
        self.assertFalse(evidence["results"][0]["timed_out"])

    def test_runner_missing_tool_is_blocked(self):
        self.write_gates(
            make_gates([self.one_tool_stack("definitely-not-a-real-tool --x")])
        )
        self.materialize("app", ["eslint.config.js"])

        result = self.run_runner()

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        evidence = self.evidence()
        self.assertEqual("BLOCKED", evidence["verdict"])
        recorded = evidence["results"][0]
        self.assertIsNone(recorded["exit_code"])
        self.assertIn("definitely-not-a-real-tool", recorded["blocked_reason"])
        self.assertFalse(recorded["timed_out"])

    def test_runner_timeout_is_failed(self):
        self.write_gates(
            make_gates(
                [self.one_tool_stack(python_command("import time; time.sleep(5)"))],
                command_timeout_seconds=1,
            )
        )
        self.materialize("app", ["eslint.config.js"])

        result = self.run_runner()

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        evidence = self.evidence()
        self.assertEqual("FAIL", evidence["verdict"])
        recorded = evidence["results"][0]
        self.assertTrue(recorded["timed_out"])
        self.assertIsNone(recorded["exit_code"])

    def test_runner_timeout_preserves_printed_output_and_evidence(self):
        command = python_command(
            "import sys,time;"
            "sys.stdout.write('STATIC_MARKER_OUT\\n');sys.stdout.flush();"
            "sys.stderr.write('STATIC_MARKER_ERR\\n');sys.stderr.flush();"
            "time.sleep(5)"
        )
        self.write_gates(
            make_gates([self.one_tool_stack(command)], command_timeout_seconds=1)
        )
        self.materialize("app", ["eslint.config.js"])

        result = self.run_runner()

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        evidence = self.evidence()
        self.assertEqual("FAIL", evidence["verdict"])
        recorded = evidence["results"][0]
        self.assertTrue(recorded["timed_out"])
        self.assertIsNone(recorded["exit_code"])
        log_text = (self.root / recorded["log"]).read_text(encoding="utf-8")
        self.assertIn("STATIC_MARKER_OUT", log_text)
        self.assertIn("STATIC_MARKER_ERR", log_text)
        self.assertIn("timed_out: true", log_text)

    def test_runner_network_command_refused(self):
        self.write_gates(make_gates([self.one_tool_stack("npx eslint .")]))
        self.materialize("app", ["eslint.config.js"])

        result = self.run_runner()

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("ERROR", result.stdout + result.stderr)
        self.assertIn("network", (result.stdout + result.stderr).lower())
        self.assertFalse((self.root / EVIDENCE_REL).exists())

    def test_runner_chinese_root(self):
        self.write_gates(
            make_gates(
                [
                    self.one_tool_stack(
                        python_command("import sys; sys.exit(0)"),
                        stack_id="frontend",
                        stack_root="前端应用",
                    )
                ]
            )
        )
        self.materialize("前端应用", ["eslint.config.js"])

        result = self.run_runner()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        evidence = self.evidence()
        recorded = evidence["results"][0]
        self.assertIn("前端应用", recorded["log"])
        log_path = self.root / recorded["log"]
        self.assertTrue(log_path.is_file(), f"log file missing: {log_path}")
        self.assertEqual("前端应用", recorded["cwd"])

    def test_runner_advisory_tool_does_not_block(self):
        stack = self.one_tool_stack(python_command("import sys; sys.exit(0)"))
        stack["tools"].append(
            {
                "id": "advisory-lint",
                "mode": "advisory",
                "command": python_command("import sys; sys.exit(1)"),
                "configs": ["eslint.config.js"],
            }
        )
        self.write_gates(make_gates([stack]))
        self.materialize("app", ["eslint.config.js"])

        result = self.run_runner()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        evidence = self.evidence()
        self.assertEqual("PASS", evidence["verdict"])
        advisory = [
            item for item in evidence["results"] if item["mode"] == "advisory"
        ]
        self.assertEqual(1, len(advisory))
        self.assertEqual(1, advisory[0]["exit_code"])

    def test_runner_independent_requires_two_identities(self):
        self.write_gates(
            make_gates([self.one_tool_stack(python_command("import sys; sys.exit(0)"))])
        )
        self.materialize("app", ["eslint.config.js"])

        result = self.run_runner("--independent", "--identity", "verifier")
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("ERROR", result.stdout + result.stderr)
        self.assertFalse((self.root / EVIDENCE_REL).exists())

        result = self.run_runner(
            "--independent",
            "--identity",
            "verifier",
            "--builder-identity",
            "verifier",
        )
        self.assertEqual(2, result.returncode, result.stdout + result.stderr)

        result = self.run_runner(
            "--independent",
            "--identity",
            "verifier",
            "--builder-identity",
            "builder",
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        evidence = self.evidence()
        self.assertTrue(evidence["independent"])
        self.assertEqual("verifier", evidence["verifier_identity"])
        self.assertEqual("builder", evidence["builder_identity"])

    def test_runner_output_outside_change_dir_rejected(self):
        self.write_gates(
            make_gates([self.one_tool_stack(python_command("import sys; sys.exit(0)"))])
        )
        self.materialize("app", ["eslint.config.js"])

        result = self.run_runner(output="../x.json")

        self.assertEqual(2, result.returncode, result.stdout + result.stderr)
        self.assertIn("ERROR", result.stdout + result.stderr)
        self.assertFalse((self.root / "openspec/changes" / CHANGE_ID / "design" / "evidence").exists())


class CheckerTestBase(RunnerTestBase):
    """Fixtures for the evidence checker (Tasks 2 and 3)."""

    def run_checker(
        self,
        *flags: str,
        evidence: str | None = None,
    ) -> subprocess.CompletedProcess:
        args = [
            sys.executable,
            str(CHECKER),
            "--change",
            CHANGE_ID,
            "--root",
            str(self.root),
        ]
        if evidence is not None:
            args.extend(["--evidence", evidence])
        args.extend(flags)
        return subprocess.run(
            args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(REPO_ROOT),
        )

    def write_evidence(self, data: dict, output: str = EVIDENCE_REL) -> Path:
        path = self.root / output
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def read_evidence(self, output: str = EVIDENCE_REL) -> dict:
        return json.loads((self.root / output).read_text(encoding="utf-8"))

    def mutate_evidence(self, mutator, output: str = EVIDENCE_REL) -> dict:
        data = self.read_evidence(output)
        mutator(data)
        self.write_evidence(data, output)
        return data

    def write_project_file(self, rel: str, text: str = "// legacy\n") -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def write_waivers(self, waivers: list[dict], rel: str = WAIVERS_REL) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"schema_version": "1.0", "change_id": CHANGE_ID, "waivers": waivers}
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def valid_waiver(self, **overrides) -> dict:
        waiver = {
            "id": "WAIVER-001",
            "stack": "app",
            "tool": "lint",
            "file": "app/src/legacy/x.ts",
            "rule": "no-explicit-any",
            "reason": "temporary legacy exception",
            "owner": "owner",
            "approved_by": "approver",
            "approved_at": date.today().isoformat(),
            "expires_at": (date.today() + timedelta(days=30)).isoformat(),
        }
        waiver.update(overrides)
        return waiver

    def run_fixture(
        self,
        stack: dict,
        *,
        gates: dict | None = None,
        stack_configs: list[str] | None = None,
        runner_flags: tuple[str, ...] = ("--identity", "builder"),
        output: str = EVIDENCE_REL,
        expect_rc: int = 0,
    ) -> subprocess.CompletedProcess:
        """Write a fixture project and invoke the runner; return its result."""
        self.write_gates(gates or make_gates([stack]))
        self.materialize(stack["root"], stack_configs or ["eslint.config.js"])
        result = self.run_runner(*runner_flags, output=output)
        self.assertEqual(expect_rc, result.returncode, result.stdout + result.stderr)
        return result


class CheckerTests(CheckerTestBase):
    def passing_stack(self) -> dict:
        return self.one_tool_stack(python_command("import sys; sys.exit(0)"))

    def assert_check_fails(self, result: subprocess.CompletedProcess, *needles: str) -> None:
        output = result.stdout + result.stderr
        self.assertEqual(1, result.returncode, output)
        self.assertNotIn("STATIC_ANALYSIS_CHECK_PASSED", result.stdout)
        self.assertIn("ERROR:", output)
        for needle in needles:
            self.assertIn(needle.lower(), output.lower())

    def test_checker_accepts_runner_evidence(self):
        self.run_fixture(self.passing_stack())

        result = self.run_checker("--strict")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("STATIC_ANALYSIS_CHECK_PASSED", result.stdout)

    def test_checker_rejects_failing_result(self):
        stack = self.one_tool_stack(python_command("import sys; sys.exit(3)"))
        self.run_fixture(stack, expect_rc=1)

        result = self.run_checker()

        self.assert_check_fails(result, "verdict")

    def test_checker_rejects_missing_result(self):
        stack = self.one_tool_stack(python_command("import sys; sys.exit(0)"))
        stack["tools"].append(
            {
                "id": "types",
                "mode": "blocking",
                "command": python_command("import sys; sys.exit(0)"),
                "configs": ["eslint.config.js"],
            }
        )
        self.run_fixture(stack)
        self.mutate_evidence(lambda data: data["results"].pop())

        result = self.run_checker()

        self.assert_check_fails(result, "exactly one result")

    def test_checker_rejects_gates_drift(self):
        stack = self.passing_stack()
        self.run_fixture(stack)
        recorded = self.read_evidence()["gates_file"]["sha256"]

        changed = make_gates(
            [self.one_tool_stack(python_command("import sys; sys.exit(0); pass"))]
        )
        self.write_gates(changed)
        current = qg.sha256_file(self.root / qg.GATES_REL)
        self.assertNotEqual(recorded, current)

        result = self.run_checker()

        self.assert_check_fails(result, "drift", recorded, current)

    def test_checker_rejects_config_hash_mismatch(self):
        self.run_fixture(self.passing_stack())
        (self.root / "app/eslint.config.js").write_text(
            "export default ['changed'];\n", encoding="utf-8"
        )

        result = self.run_checker()

        self.assert_check_fails(result, "config", "hash mismatch")

    def test_checker_rejects_log_escape_and_missing_log(self):
        self.run_fixture(self.passing_stack())
        original = self.read_evidence()

        escaped = dict(original)
        escaped["results"] = [dict(original["results"][0])]
        escaped["results"][0]["log"] = "../../outside.log"
        self.write_evidence(escaped)

        result = self.run_checker()
        self.assert_check_fails(result, "log", "safe")

        self.write_evidence(original)
        log_rel = original["results"][0]["log"]
        (self.root / log_rel).unlink()

        result = self.run_checker()
        self.assert_check_fails(result, "log", "missing")

    def test_checker_rejects_unknown_stack_tool(self):
        self.run_fixture(self.passing_stack())
        known_log = self.read_evidence()["results"][0]["log"]

        def add_unknown(data):
            data["results"].append(
                {
                    "stack_id": "ghost",
                    "tool": "lint",
                    "mode": "blocking",
                    "command": "true",
                    "cwd": "ghost",
                    "exit_code": 0,
                    "timed_out": False,
                    "log": known_log,
                    "configs": [],
                }
            )

        self.mutate_evidence(add_unknown)

        result = self.run_checker()

        self.assert_check_fails(result, "unknown")

    def test_checker_requires_independent_identity(self):
        stack = self.passing_stack()
        self.run_fixture(stack)

        result = self.run_checker("--expect-independent", evidence=EVIDENCE_REL)
        self.assert_check_fails(result, "independent")

        independent_flags = (
            "--independent",
            "--identity",
            "verifier",
            "--builder-identity",
            "builder",
        )
        self.run_fixture(stack, runner_flags=independent_flags, output=INDEPENDENT_EVIDENCE_REL)
        self.mutate_evidence(
            lambda data: data.__setitem__("builder_identity", "verifier"),
            output=INDEPENDENT_EVIDENCE_REL,
        )

        result = self.run_checker("--expect-independent")
        self.assert_check_fails(result, "verifier_identity")

        self.run_fixture(stack, runner_flags=independent_flags, output=INDEPENDENT_EVIDENCE_REL)

        result = self.run_checker("--expect-independent", "--strict")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("STATIC_ANALYSIS_CHECK_PASSED", result.stdout)

    def test_checker_strict_requires_builder_identity(self):
        stack = self.passing_stack()
        self.run_fixture(stack)
        self.mutate_evidence(lambda data: data.__setitem__("builder_identity", ""))

        result = self.run_checker("--strict")
        self.assert_check_fails(result, "builder_identity")

        result = self.run_checker()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_checker_expired_waiver_fails(self):
        self.write_project_file("app/src/legacy/x.ts")
        self.write_waivers([self.valid_waiver()])
        self.run_fixture(self.passing_stack())
        evidence = self.read_evidence()
        self.assertEqual(1, len(evidence["waivers_applied"]))

        expired = self.valid_waiver(
            approved_at=(date.today() - timedelta(days=40)).isoformat(),
            expires_at=(date.today() - timedelta(days=1)).isoformat(),
        )
        self.write_waivers([expired])

        result = self.run_checker()

        self.assert_check_fails(result, "expired")

    def test_checker_chinese_paths(self):
        stack = self.one_tool_stack(
            python_command("import sys; sys.exit(0)"),
            stack_id="frontend",
            stack_root="前端应用",
        )
        self.run_fixture(stack)

        result = self.run_checker("--strict")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("STATIC_ANALYSIS_CHECK_PASSED", result.stdout)


class WaiverPolicyTests(CheckerTestBase):
    def passing_stack(self) -> dict:
        return self.one_tool_stack(python_command("import sys; sys.exit(0)"))

    def test_runner_valid_waiver_records_projection(self):
        self.write_project_file("app/src/legacy/x.ts")
        waiver = self.valid_waiver()
        self.write_waivers([waiver])
        self.run_fixture(self.passing_stack())

        applied = self.read_evidence()["waivers_applied"]

        self.assertEqual(1, len(applied))
        self.assertEqual(
            {"id", "file", "rule", "approved_by", "expires_at"}, set(applied[0])
        )
        for key in ("id", "file", "rule", "approved_by", "expires_at"):
            self.assertEqual(waiver[key], applied[0][key], key)

    def test_runner_expired_waiver_exits_2(self):
        self.write_project_file("app/src/legacy/x.ts")
        expired = self.valid_waiver(
            approved_at=(date.today() - timedelta(days=40)).isoformat(),
            expires_at=(date.today() - timedelta(days=1)).isoformat(),
        )
        self.write_waivers([expired])
        self.write_gates(make_gates([self.passing_stack()]))
        self.materialize("app", ["eslint.config.js"])

        result = self.run_runner()

        output = result.stdout + result.stderr
        self.assertEqual(2, result.returncode, output)
        self.assertIn("ERROR", output)
        self.assertIn("expired", output.lower())
        self.assertFalse((self.root / EVIDENCE_REL).exists())

    def test_checker_rejects_waiver_when_disallowed(self):
        stack = self.passing_stack()
        gates = make_gates([stack])
        gates["policy"]["waiver"]["allowed"] = False
        self.write_project_file("app/src/legacy/x.ts")
        self.write_waivers([self.valid_waiver()])
        self.run_fixture(stack, gates=gates)

        result = self.run_checker()

        output = result.stdout + result.stderr
        self.assertEqual(1, result.returncode, output)
        self.assertIn("allowed", output.lower())

    def test_checker_rejects_waiver_exceeding_max_days(self):
        stack = self.passing_stack()
        gates = make_gates([stack])
        gates["policy"]["waiver"]["max_days"] = 30
        waiver = self.valid_waiver(
            approved_at=date.today().isoformat(),
            expires_at=(date.today() + timedelta(days=60)).isoformat(),
        )
        self.write_project_file("app/src/legacy/x.ts")
        self.write_waivers([waiver])
        self.run_fixture(stack, gates=gates)

        result = self.run_checker()

        output = result.stdout + result.stderr
        self.assertEqual(1, result.returncode, output)
        self.assertIn("max_days", output.lower())


class StaticTemplateTests(unittest.TestCase):
    def test_shellcheckrc_avoids_cli_only_severity_directive(self):
        rc = (REPO_ROOT / "templates/static-analysis/shell/shellcheckrc").read_text(
            encoding="utf-8"
        )
        self.assertNotRegex(rc, r"(?m)^severity=")
        readme = (REPO_ROOT / "templates/static-analysis/shell/README.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("-S style", readme)

    def test_verify_script_reports_static_skip_as_partial(self):
        script = (REPO_ROOT / "scripts/verify-before-completion.sh").read_text(
            encoding="utf-8"
        )
        self.assertIn("because static analysis was skipped", script)
        self.assertIn("because tests were skipped", script)


if __name__ == "__main__":
    unittest.main(verbosity=2)
