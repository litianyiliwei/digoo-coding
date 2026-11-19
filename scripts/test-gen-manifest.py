#!/usr/bin/env python3
"""Regression tests for gen-manifest.py (vendor-set manifest generation)."""
import importlib.util
import json
import tempfile
import unittest
from hashlib import sha256
from pathlib import Path

SCRIPT = Path(__file__).with_name("gen-manifest.py")


def load(root: Path):
    spec = importlib.util.spec_from_file_location("gen_manifest", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    return module


class GenManifestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for rel in ["scripts", "templates/project-setup", "process/proposals", "prompts"]:
            (self.root / rel).mkdir(parents=True, exist_ok=True)
        (self.root / "VERSION").write_text("2.0.0\n", encoding="utf-8")
        (self.root / "scripts" / "a.py").write_text("print('a')\n", encoding="utf-8")
        (self.root / "templates" / "x.md").write_text("# x\n", encoding="utf-8")
        (self.root / "process" / "WORKFLOW-STAGES.json").write_text("{}\n", encoding="utf-8")
        (self.root / "process" / "proposals" / "p.md").write_text("plan\n", encoding="utf-8")
        (self.root / "prompts" / "01.md").write_text("# p\n", encoding="utf-8")
        (self.root / "README.md").write_text("# r\n", encoding="utf-8")
        (self.root / "templates" / "project-setup" / "toolkit-ci.yml").write_text(
            "name: toolkit-ci\n", encoding="utf-8"
        )

    def tearDown(self):
        self.tmp.cleanup()

    def manifest(self):
        return json.loads((self.root / "process" / "TOOLKIT-MANIFEST.json").read_text(encoding="utf-8"))

    def test_write_then_check_is_stable(self):
        module = load(self.root)
        self.assertEqual(0, module.main(["--write"]))
        first = (self.root / "process" / "TOOLKIT-MANIFEST.json").read_bytes()
        self.assertEqual(0, module.main(["--write"]))
        self.assertEqual(first, (self.root / "process" / "TOOLKIT-MANIFEST.json").read_bytes())
        self.assertEqual(0, module.main(["--check"]))

    def test_check_fails_after_edit(self):
        module = load(self.root)
        self.assertEqual(0, module.main(["--write"]))
        (self.root / "scripts" / "a.py").write_text("print('changed')\n", encoding="utf-8")
        self.assertEqual(1, module.main(["--check"]))

    def test_toolkit_ci_install_path_and_exclusions(self):
        module = load(self.root)
        self.assertEqual(0, module.main(["--write"]))
        data = self.manifest()
        entry = next(f for f in data["files"] if f["path"] == "templates/project-setup/toolkit-ci.yml")
        self.assertEqual(".github/workflows/toolkit-ci.yml", entry["install"])
        self.assertEqual("2.0.0", data["version"])
        self.assertFalse(any(f["path"].startswith("process/proposals/") for f in data["files"]))
        self.assertFalse(any(f["path"].startswith("README") for f in data["files"]))

    def test_crlf_text_hashes_as_lf(self):
        module = load(self.root)
        (self.root / "templates" / "x.md").write_bytes(b"# x\r\n")
        self.assertEqual(0, module.main(["--write"]))
        self.assertEqual(0, module.main(["--check"]))
        data = self.manifest()
        entry = next(f for f in data["files"] if f["path"] == "templates/x.md")
        self.assertEqual(sha256(b"# x\n").hexdigest(), entry["sha256"])


    def test_project_mode_is_skipped(self):
        (self.root / "toolkit-lock.json").write_text("{}", encoding="utf-8")
        (self.root / "docs").mkdir()
        module = load(self.root)
        self.assertEqual(0, module.main(["--check"]))
        self.assertEqual(0, module.main(["--write"]))
        self.assertFalse((self.root / "process" / "TOOLKIT-MANIFEST.json").exists())


if __name__ == "__main__":
    unittest.main()
