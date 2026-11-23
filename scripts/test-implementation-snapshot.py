#!/usr/bin/env python3
"""Regression tests for implementation-snapshot.py (stage 08 entry evidence)."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from unittest import mock

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

SNAPSHOT = SCRIPTS_DIR / "implementation-snapshot.py"
EVIDENCE_REL = "openspec/changes/demo/design/evidence/implementation-base.json"

import gate_common as gm  # noqa: E402


def load(root: Path):
    spec = importlib.util.spec_from_file_location("implementation_snapshot", SNAPSHOT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    return module


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


class ImplementationSnapshotTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.mod = load(self.root)
        self.evidence = self.root / EVIDENCE_REL

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel: str, text: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    def git(self, *args: str) -> subprocess.CompletedProcess:
        proc = subprocess.run(
            ["git", *args],
            cwd=self.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(0, proc.returncode, proc.stderr)
        return proc

    def init_repo(self) -> None:
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test User")

    def commit(self, message: str = "init") -> None:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def read_evidence(self) -> dict:
        return json.loads(self.evidence.read_text(encoding="utf-8"))

    # -- write contract -------------------------------------------------

    def test_writes_head_hashes_and_fingerprint(self):
        self.init_repo()
        self.write("src/app.py", "print('app')\n")
        self.write("README.md", "# demo\n")
        self.commit()
        head = self.git("rev-parse", "HEAD").stdout.strip()

        path, doc = self.mod.write_snapshot("demo")

        self.assertEqual(self.evidence.resolve(), Path(path).resolve())
        self.assertTrue(self.evidence.is_file())
        data = self.read_evidence()
        self.assertEqual("1.0", data["schema_version"])
        self.assertEqual("demo", data["change_id"])
        self.assertEqual(head, data["head"])
        self.assertEqual(sha256("print('app')\n"), data["files"]["src/app.py"])
        self.assertEqual(sha256("# demo\n"), data["files"]["README.md"])
        captured = datetime.fromisoformat(data["captured_at"])
        self.assertIsNotNone(captured.tzinfo)
        self.assertEqual(timezone.utc.utcoffset(captured), captured.utcoffset())
        self.assertEqual(gm.fingerprint(data["files"]), data["fingerprint"])
        self.assertEqual(data["files"], doc["files"])
        self.assertEqual(2, len(data["files"]))

    def test_creates_evidence_directory(self):
        self.init_repo()
        self.write("src/app.py", "x\n")
        self.commit()
        self.assertFalse(self.evidence.parent.exists())
        path, _ = self.mod.write_snapshot("demo")
        self.assertTrue(self.evidence.parent.is_dir())
        self.assertTrue(Path(path).is_file())

    def test_untracked_file_is_captured(self):
        self.init_repo()
        self.write("src/tracked.py", "tracked\n")
        self.commit()
        self.write("src/untracked.py", "untracked\n")
        _, doc = self.mod.write_snapshot("demo")
        self.assertEqual(sha256("untracked\n"), doc["files"]["src/untracked.py"])
        self.assertEqual(sha256("tracked\n"), doc["files"]["src/tracked.py"])

    # -- exclusions -----------------------------------------------------

    def test_change_design_and_volatile_paths_are_excluded(self):
        self.init_repo()
        self.write("src/keep.py", "keep\n")
        self.write("openspec/changes/demo/design.md", "# design\n")
        self.write("openspec/changes/demo/design/evidence/old.json", "{}\n")
        self.write("openspec/changes/archive/old/design.md", "# old\n")
        self.write("workflow/evidence/run.json", "{}\n")
        self.write("workflow-state.json", "{}\n")
        self.write("toolkit-lock.json", "{}\n")
        self.write("docs/architecture/baseline-status.md", "# status\n")
        self.write("docs/architecture/baseline-manifest.json", "{}\n")
        self.write("docs/architecture/constraint-registry.json", "{}\n")
        self.write("docs/project/toolchain-report.md", "# report\n")
        self.commit()

        _, doc = self.mod.write_snapshot("demo")

        excluded = {
            "openspec/changes/demo/design.md",
            "openspec/changes/demo/design/evidence/old.json",
            "openspec/changes/archive/old/design.md",
            "workflow/evidence/run.json",
            "workflow-state.json",
            "toolkit-lock.json",
            "docs/architecture/baseline-status.md",
            "docs/architecture/baseline-manifest.json",
            "docs/architecture/constraint-registry.json",
            "docs/project/toolchain-report.md",
        }
        for relpath in excluded:
            self.assertNotIn(relpath, doc["files"])
        self.assertIn("src/keep.py", doc["files"])
        self.assertNotIn(EVIDENCE_REL, doc["files"])

    # -- refusal / force ------------------------------------------------

    def test_second_run_refuses_without_force_and_keeps_file(self):
        self.init_repo()
        self.write("src/app.py", "first\n")
        self.commit()
        self.mod.write_snapshot("demo")
        before = self.evidence.read_text(encoding="utf-8")

        with self.assertRaises(RuntimeError) as ctx:
            self.mod.write_snapshot("demo")

        message = str(ctx.exception)
        self.assertIn(EVIDENCE_REL, message)
        self.assertIn("--force", message)
        self.assertEqual(before, self.evidence.read_text(encoding="utf-8"))

    def test_force_requires_non_empty_reason(self):
        self.init_repo()
        self.write("src/app.py", "first\n")
        self.commit()
        self.mod.write_snapshot("demo")
        before = self.evidence.read_text(encoding="utf-8")

        for reason in ("", "   "):
            with self.subTest(reason=repr(reason)):
                with self.assertRaises(RuntimeError) as ctx:
                    self.mod.write_snapshot("demo", force=True, reason=reason)
                message = str(ctx.exception)
                self.assertIn("--reason", message)
                self.assertIn(EVIDENCE_REL, message)
        self.assertEqual(before, self.evidence.read_text(encoding="utf-8"))

    def test_force_with_reason_overwrites_and_records_override(self):
        self.init_repo()
        self.write("src/app.py", "first\n")
        self.commit()
        self.mod.write_snapshot("demo")
        self.write("src/app.py", "second\n")
        self.commit("change")

        _, doc = self.mod.write_snapshot("demo", force=True, reason="baseline rebase")

        data = self.read_evidence()
        self.assertEqual("baseline rebase", data["override_reason"])
        self.assertEqual(sha256("second\n"), data["files"]["src/app.py"])
        self.assertEqual(doc["files"], data["files"])

    def test_rejects_empty_or_traversing_change_id(self):
        self.init_repo()
        self.write("src/app.py", "x\n")
        self.commit()
        for change_id in ("", "   ", "../escape", "a/b"):
            with self.subTest(change_id=change_id):
                with self.assertRaises(RuntimeError) as ctx:
                    self.mod.write_snapshot(change_id)
                self.assertIn("change-id", str(ctx.exception).lower())

    # -- git failures ---------------------------------------------------

    def test_non_repo_raises_runtime_error_without_writing(self):
        with mock.patch.dict(
            os.environ, {"GIT_CEILING_DIRECTORIES": str(self.root.parent)}
        ):
            with self.assertRaises(RuntimeError) as ctx:
                self.mod.write_snapshot("demo")
        self.assertIn("git", str(ctx.exception).lower())
        self.assertFalse(self.evidence.exists())
        self.assertFalse(self.evidence.parent.exists())

    def test_git_head_failure_includes_stderr(self):
        failure = subprocess.CompletedProcess(
            ["git"], 128, stdout="", stderr="fatal: not a git repository\n"
        )
        with mock.patch.object(self.mod.subprocess, "run", return_value=failure):
            with self.assertRaisesRegex(RuntimeError, "not a git repository"):
                self.mod.write_snapshot("demo")
        self.assertFalse(self.evidence.exists())

    def test_git_unavailable_raises_runtime_error(self):
        with mock.patch.object(
            self.mod.subprocess, "run", side_effect=FileNotFoundError("git")
        ):
            with self.assertRaises(RuntimeError) as ctx:
                self.mod.write_snapshot("demo")
        self.assertIn("git", str(ctx.exception).lower())
        self.assertFalse(self.evidence.exists())

    # -- CLI ------------------------------------------------------------

    def test_cli_prints_path_and_count_and_exits_zero(self):
        self.init_repo()
        self.write("src/app.py", "x\n")
        self.write("README.md", "y\n")
        self.commit()
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = self.mod.main(["demo"])
        self.assertEqual(0, code)
        self.assertIn(EVIDENCE_REL, out.getvalue())
        self.assertIn("2 file(s)", out.getvalue())
        self.assertEqual("", err.getvalue())
        self.assertTrue(self.evidence.is_file())

    def test_cli_refusal_exits_one_with_path(self):
        self.init_repo()
        self.write("src/app.py", "x\n")
        self.commit()
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            self.mod.main(["demo"])
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = self.mod.main(["demo"])
        self.assertEqual(1, code)
        self.assertIn(EVIDENCE_REL, err.getvalue())

    def test_cli_force_without_reason_exits_one(self):
        self.init_repo()
        self.write("src/app.py", "x\n")
        self.commit()
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = self.mod.main(["demo", "--force"])
        self.assertEqual(1, code)
        self.assertIn("--reason", err.getvalue())
        self.assertFalse(self.evidence.exists())

    def test_cli_force_with_reason_succeeds(self):
        self.init_repo()
        self.write("src/app.py", "x\n")
        self.commit()
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            self.mod.main(["demo"])
        out, err = StringIO(), StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = self.mod.main(["demo", "--force", "--reason", "rebase"])
        self.assertEqual(0, code)
        self.assertEqual("rebase", self.read_evidence()["override_reason"])

    def test_cli_requires_change_id(self):
        with redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                self.mod.main([])
        self.assertEqual(2, ctx.exception.code)


if __name__ == "__main__":
    unittest.main()
