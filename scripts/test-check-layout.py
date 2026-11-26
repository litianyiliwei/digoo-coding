#!/usr/bin/env python3
"""Regression tests for check-layout.py (toolkit and project ownership modes)."""
import contextlib
import importlib.util
import io
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("check-layout.py")


def load(root: Path):
    spec = importlib.util.spec_from_file_location("check_layout", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    return module


def make_toolkit_root(root: Path) -> None:
    for rel in [".claude/skills/demo", ".claude/hooks", "prompts", "templates", "scripts",
                "process", ".github/workflows"]:
        (root / rel).mkdir(parents=True, exist_ok=True)
    (root / ".claude/skills/demo/SKILL.md").write_text("---\nname: demo\n---\n", encoding="utf-8")
    (root / ".claude/hooks/h.py").write_text("", encoding="utf-8")
    (root / ".claude/settings.json").write_text("{}", encoding="utf-8")
    (root / "prompts/01.md").write_text("# p\n", encoding="utf-8")
    (root / "templates/x.md").write_text("# t\n", encoding="utf-8")
    (root / "scripts/x.py").write_text("", encoding="utf-8")
    (root / "process/x.md").write_text("# proc\n", encoding="utf-8")
    (root / ".github/workflows/ci.yml").write_text("name: ci\n", encoding="utf-8")
    for name in ["README.md", "LICENSE", ".gitattributes", ".gitignore", "AGENTS.md",
                 "AGENTS-zh.md", "VERSION"]:
        (root / name).write_text("x\n", encoding="utf-8")


GITIGNORE_BLOCK = "# project\n<!-- toolkit:begin -->\nblock\n<!-- toolkit:end -->\n"


def git_init(root: Path) -> bool:
    """Make the fixture a Git work tree and stage its content."""
    if not shutil.which("git"):
        return False
    subprocess.run(["git", "-C", str(root), "init", "-q"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True, capture_output=True)
    return True


def make_project_root(root: Path) -> None:
    make_toolkit_root(root)
    (root / "VERSION").unlink()
    lock = {"version": "2.0.0", "files": {
        "prompts/01.md": "0" * 64,
        "templates/x.md": "0" * 64,
        "scripts/x.py": "0" * 64,
        "process/x.md": "0" * 64,
        ".claude/skills/demo/SKILL.md": "0" * 64,
        ".claude/hooks/h.py": "0" * 64,
        ".claude/settings.json": "0" * 64,
    }}
    (root / "toolkit-lock.json").write_text(json.dumps(lock), encoding="utf-8")
    for managed in ["AGENTS.md", "AGENTS-zh.md", ".gitignore"]:
        (root / managed).write_text(
            "# project\n<!-- toolkit:begin -->\nblock\n<!-- toolkit:end -->\n", encoding="utf-8"
        )


class CheckLayoutTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_toolkit_mode_rejects_docs_directory(self):
        make_toolkit_root(self.root)
        (self.root / "docs/product").mkdir(parents=True)
        (self.root / "docs/product/x.md").write_text("x\n", encoding="utf-8")
        module = load(self.root)
        self.assertEqual(1, module.main(["--mode", "toolkit"]))

    def test_toolkit_mode_allows_process_only(self):
        make_toolkit_root(self.root)
        (self.root / "_trash").mkdir()
        module = load(self.root)
        self.assertEqual(0, module.main(["--mode", "toolkit"]))

    def test_project_mode_requires_lock(self):
        make_toolkit_root(self.root)
        module = load(self.root)
        self.assertEqual(1, module.main(["--mode", "project"]))

    def test_project_mode_rejects_unknown_docs_child(self):
        make_project_root(self.root)
        (self.root / "docs/random").mkdir(parents=True)
        (self.root / "docs/random/x.md").write_text("x\n", encoding="utf-8")
        module = load(self.root)
        self.assertEqual(1, module.main(["--mode", "project"]))

    def test_project_mode_accepts_extension_registry(self):
        make_project_root(self.root)
        (self.root / "docs/product").mkdir(parents=True)
        (self.root / "notes").mkdir()
        (self.root / "notes/x.md").write_text("x\n", encoding="utf-8")
        (self.root / "project-extensions.json").write_text(
            json.dumps({"root": ["notes"], "paths": []}), encoding="utf-8"
        )
        module = load(self.root)
        self.assertEqual(0, module.main(["--mode", "project"]))

    def test_project_mode_ignores_gitignored_root_entry(self):
        make_project_root(self.root)
        (self.root / ".gitignore").write_text(GITIGNORE_BLOCK + "node_modules/\n", encoding="utf-8")
        (self.root / "node_modules").mkdir()
        if not git_init(self.root):
            self.skipTest("git is required")
        module = load(self.root)
        self.assertEqual(0, module.main(["--mode", "project"]))

    def test_project_mode_flags_untracked_undeclared_root_entry(self):
        make_project_root(self.root)
        if not git_init(self.root):
            self.skipTest("git is required")
        (self.root / "backend").mkdir()
        module = load(self.root)
        self.assertEqual(1, module.main(["--mode", "project"]))

    def test_project_mode_ignores_gitignored_docs_child(self):
        make_project_root(self.root)
        (self.root / "docs/product").mkdir(parents=True)
        (self.root / "docs/node_modules").mkdir(parents=True)
        (self.root / ".gitignore").write_text(GITIGNORE_BLOCK + "docs/node_modules/\n", encoding="utf-8")
        if not git_init(self.root):
            self.skipTest("git is required")
        module = load(self.root)
        self.assertEqual(0, module.main(["--mode", "project"]))

    def test_project_mode_without_git_still_flags_working_tree_entries(self):
        make_project_root(self.root)
        (self.root / "node_modules").mkdir()
        module = load(self.root)
        self.assertEqual(1, module.main(["--mode", "project"]))

    def test_project_mode_accepts_docs_path_with_first_child_only(self):
        make_project_root(self.root)
        (self.root / "docs/api").mkdir(parents=True)
        (self.root / "project-extensions.json").write_text(
            json.dumps({"root": [], "paths": ["docs/api"]}), encoding="utf-8"
        )
        module = load(self.root)
        self.assertEqual(0, module.main(["--mode", "project"]))

    def test_project_mode_error_shows_extension_registry_hint(self):
        make_project_root(self.root)
        (self.root / "backend").mkdir()
        module = load(self.root)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = module.main(["--mode", "project"])
        self.assertEqual(1, code)
        self.assertIn("project-extensions.json", output.getvalue())


if __name__ == "__main__":
    unittest.main()
