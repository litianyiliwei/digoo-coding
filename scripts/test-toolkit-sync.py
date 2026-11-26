#!/usr/bin/env python3
"""Regression tests for toolkit-sync init/verify and the managed-block composer."""
import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("toolkit-sync.py")

AGENTS_EN = "# managed EN\nrule one\n"
AGENTS_ZH = "# 托管 ZH\n规则一\n"
GITIGNORE_BLOCK = "# toolkit:begin\n*.tmp\n# toolkit:end\n"
OPENSPEC_TEMPLATE = (
    "# toolkit:begin\n"
    "schema: spec-driven\n"
    "rules:\n"
    "  proposal:\n"
    "    - read existing changes\n"
    "# toolkit:end\n"
    "context: |\n"
    "  PENDING — written by the project at Stage 01.\n"
)
STATE = {
    "project_name": "PENDING", "active_change_id": "", "completed_steps": [],
    "current_step": "01-project-bootstrap", "skipped_steps": [], "skip_history": [],
    "abandoned_changes": [], "pending_approvals": [], "blocked_items": [],
    "last_completed_outputs": [], "notes": "", "state_schema_version": "1.0",
    "transition_history": [], "topology_migrations": [], "completed_substeps": [],
    "current_substep": "", "reopen_history": [], "reset_history": [],
    "baseline": {}, "approvals_history": [], "last_transition": None,
}


def load():
    spec = importlib.util.spec_from_file_location("toolkit_sync", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def norm_sha(data: bytes) -> str:
    return hashlib.sha256(data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def write_source(base: Path, crlf: bool = False, version: str = "2.0.0") -> None:
    files = {
        "prompts/01.md": b"# prompt\n",
        "scripts/a.py": b"print('a')\n",
        "templates/project-setup/gitignore-block.txt": GITIGNORE_BLOCK.encode(),
        "templates/project-setup/openspec-config.yaml": OPENSPEC_TEMPLATE.encode(),
        "templates/workflow/agents-managed.md": AGENTS_EN.encode(),
        "templates/workflow/agents-managed-zh.md": AGENTS_ZH.encode(),
        "templates/workflow/workflow-state.default.json": json.dumps(STATE).encode(),
    }
    if crlf:
        files["prompts/01.md"] = b"# prompt\r\n"
    entries = []
    for rel, data in sorted(files.items()):
        path = base / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        entries.append({"path": rel, "install": rel, "sha256": norm_sha(data),
                        "class": "toolkit", "vendor": True})
    manifest = {"version": version, "state_schema": "1.0", "files": entries, "exclude": []}
    (base / "process").mkdir(parents=True, exist_ok=True)
    (base / "process/TOOLKIT-MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
    (base / "VERSION").write_text(version + "\n", encoding="utf-8")


class ToolkitSyncInitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / "toolkit"
        self.project = self.root / "project"
        self.source.mkdir()
        self.project.mkdir()
        write_source(self.source)
        self.m = load()

    def tearDown(self):
        self.tmp.cleanup()

    def source_obj(self):
        return self.m.open_source(str(self.source), None, self.root / "work")

    def init(self):
        return self.m.init(self.project, self.source_obj(), "", "abc123")

    def test_init_writes_vendored_files_and_lock(self):
        lock_path = self.init()
        data = json.loads(lock_path.read_text(encoding="utf-8"))
        self.assertEqual("2.0.0", data["version"])
        self.assertIn("prompts/01.md", data["files"])
        self.assertTrue((self.project / "scripts/a.py").is_file())
        self.assertTrue((self.project / "workflow-state.json").is_file())
        self.assertIn("toolkit:begin", (self.project / "AGENTS.md").read_text(encoding="utf-8"))
        self.assertIn("toolkit:begin", (self.project / "AGENTS-zh.md").read_text(encoding="utf-8"))
        self.assertIn("toolkit:begin", (self.project / "openspec/config.yaml").read_text(encoding="utf-8"))
        self.assertIn("toolkit:begin", (self.project / ".gitignore").read_text(encoding="utf-8"))

    def test_init_refuses_existing_lock(self):
        self.init()
        with self.assertRaises(ValueError):
            self.init()

    def test_init_preserves_existing_project_sections(self):
        (self.project / "AGENTS.md").write_text("# Project\n\n## Project Goal\nKeep me.\n", encoding="utf-8")
        self.init()
        text = (self.project / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("Keep me.", text)
        self.assertIn("toolkit:begin", text)

    def test_init_preserves_openspec_context(self):
        (self.project / "openspec").mkdir(parents=True)
        (self.project / "openspec/config.yaml").write_text(
            "context: |\n  This project writes in Chinese.\n", encoding="utf-8"
        )
        self.init()
        text = (self.project / "openspec/config.yaml").read_text(encoding="utf-8")
        self.assertIn("This project writes in Chinese.", text)
        self.assertIn("toolkit:begin", text)

    def test_verify_detects_edited_vendor_file(self):
        self.init()
        (self.project / "prompts/01.md").write_text("# edited\n", encoding="utf-8")
        errors = self.m.verify(self.project, require_lock=True)
        self.assertTrue(any("prompts/01.md" in error for error in errors), errors)

    def test_verify_accepts_clean_install(self):
        self.init()
        self.assertEqual([], self.m.verify(self.project, require_lock=True))

    def test_crlf_source_hashes_as_lf(self):
        write_source(self.source, crlf=True)
        lock_path = self.init()
        data = json.loads(lock_path.read_text(encoding="utf-8"))
        self.assertEqual(hashlib.sha256(b"# prompt\n").hexdigest(), data["files"]["prompts/01.md"])
        self.assertEqual([], self.m.verify(self.project, require_lock=True))


def rewrite_source_v2(base: Path) -> None:
    write_source(base, version="2.1.0")
    (base / "prompts/01.md").write_bytes(b"# prompt v2\n")
    (base / "prompts/02.md").write_bytes(b"# prompt two\n")
    (base / "scripts/a.py").unlink()
    manifest = json.loads((base / "process/TOOLKIT-MANIFEST.json").read_text(encoding="utf-8"))
    entries = []
    for entry in manifest["files"]:
        path = base / entry["path"]
        if not path.is_file():
            continue
        entries.append({**entry, "sha256": norm_sha(path.read_bytes())})
    entries.append({"path": "prompts/02.md", "install": "prompts/02.md",
                    "sha256": norm_sha(b"# prompt two\n"), "class": "toolkit", "vendor": True})
    manifest["files"] = sorted(entries, key=lambda e: e["path"])
    manifest["version"] = "2.1.0"
    (base / "process/TOOLKIT-MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")


class ToolkitSyncUpgradeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / "toolkit"
        self.project = self.root / "project"
        self.source.mkdir()
        self.project.mkdir()
        write_source(self.source)
        self.m = load()
        self.m.init(self.project, self.m.open_source(str(self.source), None, self.root / "work"), "", "abc123")

    def tearDown(self):
        self.tmp.cleanup()

    def target(self):
        return self.m.open_source(str(self.source), None, self.root / "work2")

    def test_plan_lists_upgrade_diff(self):
        rewrite_source_v2(self.source)
        plan = self.m.plan(self.project, self.target())
        self.assertEqual("2.0.0", plan["from_version"])
        self.assertEqual("2.1.0", plan["to_version"])
        self.assertIn("prompts/02.md", plan["added"])
        self.assertIn("prompts/01.md", plan["changed"])
        self.assertIn("scripts/a.py", plan["removed"])

    def test_apply_upgrades_and_writes_lock(self):
        rewrite_source_v2(self.source)
        self.assertEqual(0, self.m.apply(self.project, self.target(), "v2.1.0"))
        data = json.loads((self.project / "toolkit-lock.json").read_text(encoding="utf-8"))
        self.assertEqual("2.1.0", data["version"])
        self.assertEqual("# prompt v2\n", (self.project / "prompts/01.md").read_text(encoding="utf-8"))
        self.assertFalse((self.project / "scripts/a.py").exists())
        self.assertIn("prompts/02.md", data["files"])

    def test_apply_never_touches_project_outputs(self):
        (self.project / "docs/product").mkdir(parents=True)
        (self.project / "docs/product/baseline.md").write_text("keep\n", encoding="utf-8")
        rewrite_source_v2(self.source)
        self.assertEqual(0, self.m.apply(self.project, self.target(), "v2.1.0"))
        self.assertEqual("keep\n", (self.project / "docs/product/baseline.md").read_text(encoding="utf-8"))

    def test_local_edit_aborts_without_flags(self):
        rewrite_source_v2(self.source)
        (self.project / "prompts/01.md").write_text("# local edit\n", encoding="utf-8")
        self.assertEqual(2, self.m.apply(self.project, self.target(), "v2.1.0"))
        self.assertEqual("# local edit\n", (self.project / "prompts/01.md").read_text(encoding="utf-8"))

    def test_keep_local_records_fork(self):
        rewrite_source_v2(self.source)
        (self.project / "prompts/01.md").write_text("# local edit\n", encoding="utf-8")
        self.assertEqual(0, self.m.apply(self.project, self.target(), "v2.1.0", keep_local=True))
        data = json.loads((self.project / "toolkit-lock.json").read_text(encoding="utf-8"))
        self.assertIn("prompts/01.md", data["forks"])
        self.assertEqual("# local edit\n", (self.project / "prompts/01.md").read_text(encoding="utf-8"))

    def test_apply_refuses_with_pending_approvals(self):
        state = json.loads((self.project / "workflow-state.json").read_text(encoding="utf-8"))
        state["pending_approvals"] = [{"step_id": "01-project-bootstrap"}]
        (self.project / "workflow-state.json").write_text(json.dumps(state), encoding="utf-8")
        rewrite_source_v2(self.source)
        self.assertEqual(2, self.m.apply(self.project, self.target(), "v2.1.0"))

    def test_apply_refuses_with_v2_lane_pending_approvals(self):
        state = {
            "state_schema_version": "2.0",
            "project": {"current_step": "PROJECT_COMPLETE", "completed_steps": [],
                        "skipped_steps": [], "pending_approvals": [], "blocked_items": []},
            "changes": {"chg-a": {"status": "ACTIVE", "current_step": "07-detailed-design",
                                  "completed_steps": [], "skipped_steps": [],
                                  "pending_approvals": [{"step_id": "07-detailed-design",
                                                         "change_id": "chg-a"}],
                                  "blocked_items": []}},
        }
        (self.project / "workflow-state.json").write_text(json.dumps(state), encoding="utf-8")
        rewrite_source_v2(self.source)
        self.assertEqual(2, self.m.apply(self.project, self.target(), "v2.1.0"))

    def test_backup_and_repair_restores_state(self):
        rewrite_source_v2(self.source)
        self.assertEqual(0, self.m.apply(self.project, self.target(), "v2.1.0"))
        backups = list((self.project / "workflow/state-backups").glob("*.json"))
        self.assertTrue(backups, "apply should back up workflow-state.json")
        (self.project / "workflow-state.json").write_text("{ broken", encoding="utf-8")
        self.assertEqual(0, self.m.repair(self.project))
        state = json.loads((self.project / "workflow-state.json").read_text(encoding="utf-8"))
        self.assertEqual("01-project-bootstrap", state["current_step"])


def add_migration_source(base: Path) -> None:
    rewrite_source_v2(base)
    (base / "scripts/migrate.py").write_text(
        "from pathlib import Path\nPath('migrated.flag').write_text('1')\n", encoding="utf-8"
    )
    manifest = json.loads((base / "process/TOOLKIT-MANIFEST.json").read_text(encoding="utf-8"))
    manifest["files"].append({"path": "scripts/migrate.py", "install": "scripts/migrate.py",
                              "sha256": norm_sha((base / "scripts/migrate.py").read_bytes()),
                              "class": "toolkit", "vendor": True})
    manifest["files"] = sorted(manifest["files"], key=lambda e: e["path"])
    manifest["state_schema"] = "2.0"
    manifest["migrations"] = [{"command": "python scripts/migrate.py", "reason": "schema bump"}]
    (base / "process/TOOLKIT-MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")


def add_layout_checker(base: Path, body: bytes | None = None) -> None:
    """Add the project layout checker to a fixture release and record its hash."""
    body = body if body is not None else SCRIPT.with_name("check-layout.py").read_bytes()
    (base / "scripts/check-layout.py").write_bytes(body)
    manifest_path = base / "process/TOOLKIT-MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = [entry for entry in manifest["files"] if entry["path"] != "scripts/check-layout.py"]
    entries.append({"path": "scripts/check-layout.py", "install": "scripts/check-layout.py",
                    "sha256": norm_sha(body), "class": "toolkit", "vendor": True})
    manifest["files"] = sorted(entries, key=lambda entry: entry["path"])
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


class ToolkitSyncHardeningTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.source = self.root / "toolkit"
        self.project = self.root / "project"
        self.source.mkdir()
        self.project.mkdir()
        write_source(self.source)
        self.m = load()
        self.m.init(self.project, self.m.open_source(str(self.source), None, self.root / "work"), "", "abc123")

    def tearDown(self):
        self.tmp.cleanup()

    def target(self):
        return self.m.open_source(str(self.source), None, self.root / "work2")

    def lock(self):
        return json.loads((self.project / "toolkit-lock.json").read_text(encoding="utf-8"))

    def test_lock_records_local_origin(self):
        data = self.lock()
        self.assertTrue(data["source"].startswith("local:"), data["source"])
        self.assertIn(str(self.source.resolve()), data["source"])

    def test_resolve_source_uses_lock_origin(self):
        source = self.m.resolve_source(self.project, "", "")
        self.assertEqual(b"# prompt\n", source.read("prompts/01.md"))

    def test_source_manifest_mismatch_is_rejected(self):
        manifest = json.loads((self.source / "process/TOOLKIT-MANIFEST.json").read_text(encoding="utf-8"))
        manifest["files"][0]["sha256"] = "0" * 64
        (self.source / "process/TOOLKIT-MANIFEST.json").write_text(json.dumps(manifest), encoding="utf-8")
        other = self.root / "other-project"
        other.mkdir()
        with self.assertRaises(ValueError):
            self.m.init(other, self.m.open_source(str(self.source), None, self.root / "work3"), "", "")

    def test_local_ref_reads_committed_version(self):
        repo = self.root / "gitrepo"
        (repo / "prompts").mkdir(parents=True)
        (repo / "prompts/01.md").write_text("# committed\n", encoding="utf-8")
        run = lambda *a: subprocess.run(a, check=True, capture_output=True)
        run("git", "-C", str(repo), "init", "-q")
        run("git", "-C", str(repo), "config", "user.email", "t@example.com")
        run("git", "-C", str(repo), "config", "user.name", "t")
        run("git", "-C", str(repo), "add", ".")
        run("git", "-C", str(repo), "commit", "-q", "-m", "one")
        first = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
        (repo / "prompts/01.md").write_text("# working tree\n", encoding="utf-8")
        source = self.m.open_source(str(repo), first)
        self.assertEqual(b"# committed\n", source.read("prompts/01.md"))
        self.assertEqual(first, source.git_commit())

    def test_migrations_run_when_requested(self):
        add_migration_source(self.source)
        target = self.target()
        self.assertEqual(2, self.m.apply(self.project, target, "v2.1.0"))
        self.assertEqual(0, self.m.apply(self.project, self.target(), "v2.1.0", run_migrations=True))
        self.assertTrue((self.project / "migrated.flag").is_file())

    def test_apply_aborts_before_writing_when_layout_check_fails(self):
        rewrite_source_v2(self.source)
        add_layout_checker(self.source)
        (self.project / "backend").mkdir()
        self.assertEqual(2, self.m.apply(self.project, self.target(), "v2.1.0"))
        self.assertEqual("# prompt\n", (self.project / "prompts/01.md").read_text(encoding="utf-8"))
        self.assertEqual("2.0.0", self.lock()["version"])

    def test_apply_preflight_passes_green_layout(self):
        rewrite_source_v2(self.source)
        add_layout_checker(self.source)
        self.assertEqual(0, self.m.apply(self.project, self.target(), "v2.1.0"))
        self.assertEqual("2.1.0", self.lock()["version"])

    def test_verify_detects_extra_vendored_file(self):
        (self.project / "prompts/99-extra.md").write_text("# extra\n", encoding="utf-8")
        errors = self.m.verify(self.project, require_lock=True)
        self.assertTrue(any("99-extra.md" in error for error in errors), errors)

    def test_repair_restores_vendored_files(self):
        (self.project / "prompts/01.md").write_text("# drifted\n", encoding="utf-8")
        self.assertEqual(0, self.m.repair(self.project))
        self.assertEqual("# prompt\n", (self.project / "prompts/01.md").read_text(encoding="utf-8"))
        self.assertEqual([], self.m.verify(self.project, require_lock=True))


if __name__ == "__main__":
    unittest.main()
