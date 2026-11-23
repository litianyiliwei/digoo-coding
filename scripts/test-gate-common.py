#!/usr/bin/env python3
"""Regression tests for gate_common.py (shared parsers for capability/Change gates)."""
import hashlib
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).with_name("gate_common.py")


def load(root: Path):
    spec = importlib.util.spec_from_file_location("gate_common", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    return module


class GateCommonTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.gm = load(self.root)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel: str, text: str):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    def git(self, *args):
        proc = subprocess.run(
            ["git", *args], cwd=self.root, capture_output=True, text=True, encoding="utf-8"
        )
        self.assertEqual(0, proc.returncode, proc.stderr)
        return proc.stdout

    def test_glob_double_star_crosses_directories(self):
        self.assertTrue(self.gm.path_matches("server/a/b/C.java", "server/**"))
        self.assertFalse(self.gm.path_matches("web/a.ts", "server/**"))
        self.assertTrue(self.gm.path_matches("a/b/c.md", "**/*.md"))
        self.assertTrue(self.gm.path_matches("top.md", "**/*.md"))
        self.assertFalse(self.gm.path_matches("a/b/c.txt", "**/*.md"))

    def test_glob_single_star_does_not_cross_directories(self):
        self.assertTrue(self.gm.path_matches("web/a.ts", "web/*.ts"))
        self.assertFalse(self.gm.path_matches("web/x/a.ts", "web/*.ts"))

    def test_glob_question_mark_matches_one_non_slash_character(self):
        self.assertTrue(self.gm.path_matches("src/b1.ts", "src/b?.ts"))
        self.assertFalse(self.gm.path_matches("src/b10.ts", "src/b?.ts"))
        self.assertFalse(self.gm.path_matches("src/b/1.ts", "src/b?.ts"))

    def test_strategy_defaults_to_none_without_layout_file(self):
        self.assertEqual("none", self.gm.strategy())
        self.assertIsNone(self.gm.load_code_layout())

    def test_strategy_reads_code_layout(self):
        self.write(
            "docs/architecture/code-layout.json",
            json.dumps({"version": 1, "strategy": "module-packages"}),
        )
        self.assertEqual("module-packages", self.gm.strategy())
        self.assertEqual("module-packages", self.gm.load_code_layout()["strategy"])
        self.write(
            "docs/architecture/code-layout.json",
            json.dumps({"version": 1, "strategy": "none"}),
        )
        self.assertEqual("none", self.gm.strategy())

    def test_strategy_accepts_module_packages(self):
        self.assertEqual({"none", "footprint", "module-packages"}, self.gm.STRATEGIES)
        for value in ("module-packages", "footprint"):
            self.write(
                "docs/architecture/code-layout.json",
                json.dumps({"version": 1, "strategy": value}),
            )
            with self.subTest(value=value):
                self.assertEqual(value, self.gm.strategy())

    def test_strategy_rejects_capability_packages(self):
        self.write(
            "docs/architecture/code-layout.json",
            json.dumps({"version": 1, "strategy": "capability-packages"}),
        )
        with self.assertRaises(RuntimeError) as ctx:
            self.gm.strategy()
        message = str(ctx.exception)
        self.assertIn("code-layout.json", message)
        self.assertIn(repr("capability-packages"), message)
        self.assertIn("module-packages", message)

    def test_strategy_rejects_blank_value(self):
        self.write(
            "docs/architecture/code-layout.json",
            json.dumps({"version": 1, "strategy": "   "}),
        )
        with self.assertRaises(RuntimeError) as ctx:
            self.gm.strategy()
        message = str(ctx.exception)
        self.assertIn("code-layout.json", message)
        self.assertIn(repr("   "), message)

    def test_strategy_rejects_missing_key(self):
        self.write("docs/architecture/code-layout.json", json.dumps({"version": 1}))
        with self.assertRaises(RuntimeError) as ctx:
            self.gm.strategy()
        message = str(ctx.exception)
        self.assertIn("code-layout.json", message)
        self.assertIn("None", message)

    def test_strategy_rejects_invalid_types_and_values(self):
        for value in (3, "hybrid"):
            self.write(
                "docs/architecture/code-layout.json",
                json.dumps({"version": 1, "strategy": value}),
            )
            with self.subTest(value=value):
                with self.assertRaises(RuntimeError) as ctx:
                    self.gm.strategy()
                message = str(ctx.exception)
                self.assertIn("code-layout.json", message)
                self.assertIn(repr(value), message)

    def test_load_capabilities_splits_semicolon_packages(self):
        self.write(
            "docs/product/capabilities.csv",
            "capability_slug,capability_name,domain_id,owner_module,related_modules,"
            "code_packages,status,delivered_slices,remaining_slices,active_changes,notes\n"
            "billing,Billing,orders,billing,report;audit,server/billing/;web/billing/,"
            "ACTIVE,N/A,N/A,demo,N/A\n",
        )
        rows = self.gm.load_capabilities()
        self.assertEqual(1, len(rows))
        self.assertEqual("billing", rows[0]["capability_slug"])
        self.assertEqual("billing", rows[0]["owner_module"])
        self.assertEqual(["report", "audit"], rows[0]["related_modules"])
        self.assertEqual(["server/billing/", "web/billing/"], rows[0]["code_packages"])

    def test_load_capabilities_missing_file_returns_empty_list(self):
        self.assertEqual([], self.gm.load_capabilities())

    def test_load_modules_splits_path_lists_and_capabilities(self):
        self.write(
            "docs/product/modules.csv",
            "module_slug,module_name,domain_id,frontend_paths,backend_paths,shared_paths,"
            "capabilities,status,notes\n"
            "order,Order,DOM-001,"
            "web/src/features/sales/order/;web/src/features/sales/order-report/,"
            "server/src/main/java/com/demo/sales/order/,"
            "server/src/main/java/com/demo/sales/order/shared/,"
            "order-create;order-status,PLANNED,example row\n",
        )
        rows = self.gm.load_modules()
        self.assertEqual(1, len(rows))
        row = rows[0]
        self.assertEqual("order", row["module_slug"])
        self.assertEqual("Order", row["module_name"])
        self.assertEqual("DOM-001", row["domain_id"])
        self.assertEqual(
            [
                "web/src/features/sales/order/",
                "web/src/features/sales/order-report/",
            ],
            row["frontend_paths"],
        )
        self.assertEqual(
            ["server/src/main/java/com/demo/sales/order/"], row["backend_paths"]
        )
        self.assertEqual(
            ["server/src/main/java/com/demo/sales/order/shared/"], row["shared_paths"]
        )
        self.assertEqual(["order-create", "order-status"], row["capabilities"])
        self.assertEqual("PLANNED", row["status"])
        self.assertEqual("example row", row["notes"])

    def test_load_modules_missing_file_returns_empty_list(self):
        self.assertEqual([], self.gm.load_modules())

    def test_module_rows_matches_slug(self):
        registry = [
            {"module_slug": "order", "backend_paths": ["server/order/"]},
            {"module_slug": "audit", "backend_paths": ["server/audit/"]},
            {"module_slug": "order", "backend_paths": ["server/order-ext/"]},
        ]
        self.assertEqual(2, len(self.gm.module_rows(registry, "order")))
        self.assertEqual(1, len(self.gm.module_rows(registry, "audit")))
        self.assertEqual([], self.gm.module_rows(registry, "unknown"))

    def test_module_paths_multi_root(self):
        registry = [
            {
                "module_slug": "order",
                "frontend_paths": ["web/src/features/sales/order/"],
                "backend_paths": ["server/src/main/java/demo/sales/order/"],
            },
            {
                "module_slug": "audit",
                "frontend_paths": ["N/A"],
                "backend_paths": ["server/src/main/java/demo/audit/"],
            },
            {
                "module_slug": "order",
                "frontend_paths": ["web/src/features/sales/order/"],
                "backend_paths": [],
            },
        ]
        self.assertEqual(
            [
                "web/src/features/sales/order/",
                "server/src/main/java/demo/sales/order/",
                "server/src/main/java/demo/audit/",
            ],
            self.gm.module_paths(registry, ["order", "audit", "order"]),
        )
        self.assertEqual([], self.gm.module_paths(registry, ["unknown"]))
        string_paths = [{"module_slug": "audit", "backend_paths": "server/audit/"}]
        self.assertEqual(["server/audit/"], self.gm.module_paths(string_paths, ["audit"]))
        self.assertEqual(
            self.gm.module_paths(registry, ["order", "audit"]),
            self.gm.package_paths(registry, ["order", "audit"]),
        )

    def test_capability_rows_matches_slug(self):
        registry = [
            {"capability_slug": "billing", "code_packages": ["server/billing/"]},
            {"capability_slug": "report-export", "code_packages": ["server/report/"]},
            {"capability_slug": "billing", "code_packages": ["server/billing-ext/"]},
        ]
        self.assertEqual(2, len(self.gm.capability_rows(registry, "billing")))
        self.assertEqual(1, len(self.gm.capability_rows(registry, "report-export")))
        self.assertEqual([], self.gm.capability_rows(registry, "unknown"))

    def test_parse_slice_reads_english_and_chinese_headings(self):
        english = """# Design

## Design Decisions

### Implementation Slice
- Primary capability: report-export
- Owner module: report
- Related modules: audit; notification
- Slice type/coverage: initial / partial
- Code packages: server/src/main/java/com/demo/report-export/; web/src/features/report-export/
- Owned paths: server/src/main/java/com/demo/report-export/**; web/src/features/report-export/**
- Integration paths:
  - web/src/router/routes.ts — register route; task T-003
  - server/src/main/java/com/demo/config/ApplicationConfig.java - register bean; task T-004
- Module card: create web/src/features/report-export/MODULE.md
- Frozen approvals:
  - BCR-001 — web/src/ui/**
- Out of context (do not read unless blocked): server/src/main/java/com/demo/billing/**

### Next Decision

Nothing.
"""
        parsed = self.gm.parse_slice(english)
        self.assertEqual("report-export", parsed["primary"])
        self.assertEqual("report", parsed["owner_module"])
        self.assertEqual(["audit", "notification"], parsed["related_modules"])
        self.assertEqual("initial / partial", parsed["shape"])
        self.assertEqual(
            [
                "server/src/main/java/com/demo/report-export/",
                "web/src/features/report-export/",
            ],
            parsed["packages"],
        )
        self.assertEqual(
            [
                "server/src/main/java/com/demo/report-export/**",
                "web/src/features/report-export/**",
            ],
            parsed["owned"],
        )
        self.assertEqual(
            [
                {"path": "web/src/router/routes.ts", "reason": "register route", "task": "T-003"},
                {
                    "path": "server/src/main/java/com/demo/config/ApplicationConfig.java",
                    "reason": "register bean",
                    "task": "T-004",
                },
            ],
            parsed["integration"],
        )
        self.assertEqual(
            "create web/src/features/report-export/MODULE.md", parsed["module_card"]
        )
        self.assertEqual(
            [{"id": "BCR-001", "path": "web/src/ui/**"}], parsed["frozen"]
        )
        self.assertIn("billing/**", parsed["out_of_context"])
        self.assertEqual(
            {
                "primary",
                "owner_module",
                "related_modules",
                "shape",
                "packages",
                "owned",
                "integration",
                "module_card",
                "frozen",
                "out_of_context",
            },
            set(parsed["present"]),
        )

        chinese = """## 设计决策

### 实现切片
- Primary capability: sample
- Owner module: sample
- Related modules: N/A + reason
- Code packages: server/sample/
"""
        parsed = self.gm.parse_slice(chinese)
        self.assertEqual("sample", parsed["primary"])
        self.assertEqual("sample", parsed["owner_module"])
        self.assertEqual([], parsed["related_modules"])
        self.assertEqual(["server/sample/"], parsed["packages"])
        self.assertEqual(
            {"primary", "owner_module", "related_modules", "packages"},
            set(parsed["present"]),
        )

    def test_parse_slice_reads_owner_and_related_modules(self):
        text = """### Implementation Slice
- Primary capability: order-create
- Owner module: order
- Related modules: audit;notification
- Slice type/coverage: extend / full
"""
        parsed = self.gm.parse_slice(text)
        self.assertEqual("order", parsed["owner_module"])
        self.assertEqual(["audit", "notification"], parsed["related_modules"])
        self.assertEqual("", parsed["module_card"])
        self.assertEqual([], parsed["frozen"])
        self.assertEqual([], parsed["integration"])

        no_owner = """### 实现切片
- Primary capability: order-create
- Related modules: N/A
"""
        parsed = self.gm.parse_slice(no_owner)
        self.assertEqual("", parsed["owner_module"])
        self.assertEqual([], parsed["related_modules"])
        self.assertEqual({"primary", "related_modules"}, set(parsed["present"]))

    def test_parse_slice_accepts_full_width_colon_separator(self):
        text = """### Implementation Slice
- Primary capability：order-create
- Owner module：order
- Related modules：audit;notification
- Owned paths：server/order/**
- Integration paths：
  - web/src/router/routes.ts — register route; task T-007
"""
        parsed = self.gm.parse_slice(text)
        self.assertEqual("order-create", parsed["primary"])
        self.assertEqual("order", parsed["owner_module"])
        self.assertEqual(["audit", "notification"], parsed["related_modules"])
        self.assertEqual(["server/order/**"], parsed["owned"])
        self.assertEqual(
            [
                {
                    "path": "web/src/router/routes.ts",
                    "reason": "register route",
                    "task": "T-007",
                }
            ],
            parsed["integration"],
        )
        self.assertEqual(
            {
                "primary",
                "owner_module",
                "related_modules",
                "owned",
                "integration",
            },
            set(parsed["present"]),
        )

    def test_parse_slice_without_heading_returns_empty_defaults(self):
        parsed = self.gm.parse_slice("# Design\n\n## Test Design\n\nN/A\n")
        self.assertEqual("", parsed["primary"])
        self.assertEqual("", parsed["owner_module"])
        self.assertEqual([], parsed["related_modules"])
        self.assertEqual([], parsed["integration"])
        self.assertEqual([], parsed["frozen"])
        self.assertEqual([], parsed["present"])

    def test_parse_roadmap_reads_main_and_amendments(self):
        self.write(
            "docs/product/proposal-roadmap.md",
            """# Roadmap

## Candidate Changes

| Change ID | Primary Capability | Extends | Slice Type | Slice Coverage | Code Target |
|---|---|---|---|---|---|
| demo-one | report-export | N/A + reason | initial | full | server/report/ |

## Roadmap Amendments

| Change ID | Primary Capability | Extends | Slice Type | Slice Coverage | Code Target | Reason | Requester | Approver | Date | Baseline Impact |
|---|---|---|---|---|---|---|---|---|---|---|---|
| late-change | billing | N/A + reason | extend | partial | server/billing/ | urgent | Alice | Tech Lead | 2026-11-20 | CHANGE_ONLY |
""",
        )
        roadmap = self.gm.parse_roadmap()
        self.assertEqual(1, len(roadmap["rows"]))
        self.assertEqual("demo-one", roadmap["rows"][0]["Change ID"])
        self.assertEqual("report-export", roadmap["rows"][0]["Primary Capability"])
        self.assertEqual(1, len(roadmap["amendments"]))
        self.assertEqual("late-change", roadmap["amendments"][0]["Change ID"])
        self.assertEqual("Tech Lead", roadmap["amendments"][0]["Approver"])
        self.assertEqual("2026-11-20", roadmap["amendments"][0]["Date"])

    def test_parse_roadmap_accepts_heading_variants(self):
        for heading in (
            "## Candidate Changes",
            "## 1. 路线图总表",
            "## Roadmap Overview",
            "## 1. Roadmap",
        ):
            self.write(
                "docs/product/proposal-roadmap.md",
                f"{heading}\n\n| Change ID | Primary Capability |\n|---|---|\n| demo | cap |\n",
            )
            self.assertEqual("demo", self.gm.parse_roadmap()["rows"][0]["Change ID"])
        for heading in ("## Roadmap Amendments", "## 路线图修订"):
            self.write(
                "docs/product/proposal-roadmap.md",
                f"{heading}\n\n| Change ID | Approver | Date |\n|---|---|---|\n"
                "| late | Tech Lead | 2026-11-20 |\n",
            )
            self.assertEqual("late", self.gm.parse_roadmap()["amendments"][0]["Change ID"])

    def test_parse_roadmap_missing_file_returns_empty_tables(self):
        roadmap = self.gm.parse_roadmap()
        self.assertEqual({"rows": [], "amendments": []}, roadmap)

    def test_registered_change_sees_amendment(self):
        self.write(
            "docs/product/proposal-roadmap.md",
            """## Candidate Changes

| Change ID | Primary Capability |
|---|---|
| planned | planned-cap |

## Roadmap Amendments

| Change ID | Primary Capability | Approver | Date |
|---|---|---|---|
| late-change | late-cap | Tech Lead | 2026-11-20 |
""",
        )
        roadmap = self.gm.parse_roadmap()
        self.assertTrue(self.gm.registered_change(roadmap, "planned"))
        self.assertTrue(self.gm.registered_change(roadmap, "late-change"))
        self.assertFalse(self.gm.registered_change(roadmap, "unknown"))
        self.assertEqual("planned-cap", self.gm.find_change(roadmap, "planned")["Primary Capability"])
        self.assertEqual("late-cap", self.gm.find_change(roadmap, "late-change")["Primary Capability"])
        self.assertIsNone(self.gm.find_change(roadmap, "unknown"))

    def test_excluded_covers_change_dir_and_workflow(self):
        self.assertTrue(self.gm.excluded("openspec/changes/demo/design.md", "demo"))
        self.assertTrue(self.gm.excluded("openspec/changes/demo/evidence/a.json", "demo"))
        self.assertFalse(self.gm.excluded("openspec/changes/demo-other/design.md", "demo"))
        self.assertTrue(self.gm.excluded("openspec/changes/archive/old/x.md", "demo"))
        self.assertTrue(self.gm.excluded("workflow/evidence/r.json", "demo"))
        for relpath in (
            "workflow-state.json",
            "toolkit-lock.json",
            "docs/architecture/baseline-status.md",
            "docs/architecture/baseline-manifest.json",
            "docs/architecture/constraint-registry.json",
            "docs/project/toolchain-report.md",
        ):
            self.assertTrue(self.gm.excluded(relpath, "demo"))
        self.assertFalse(self.gm.excluded("docs/architecture/architecture.md", "demo"))
        self.assertFalse(self.gm.excluded("server/src/main/java/demo/App.java", "demo"))

    def test_enumerate_files_uses_git_and_applies_exclusions(self):
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test User")
        (self.root / ".git/info").mkdir(parents=True, exist_ok=True)
        (self.root / ".git/info/exclude").write_text("ignored.txt\n", encoding="utf-8")
        tracked = {
            "src/a.py": "print('a')\n",
            "src/deleted.py": "print('deleted')\n",
            "docs/keep.md": "# keep\n",
            "docs/architecture/baseline-status.md": "{}\n",
            "docs/architecture/baseline-manifest.json": "{}\n",
            "docs/architecture/constraint-registry.json": "{}\n",
            "docs/project/toolchain-report.md": "# report\n",
            "workflow/log.txt": "log\n",
            "workflow-state.json": "{}\n",
            "toolkit-lock.json": "{}\n",
            "openspec/changes/demo/design.md": "# design\n",
            "openspec/changes/archive/old/x.md": "# old\n",
        }
        for rel, text in tracked.items():
            self.write(rel, text)
        self.git("add", "-A")
        self.git("commit", "-q", "-m", "init")
        (self.root / "src/deleted.py").unlink()
        self.write("src/untracked.py", "print('untracked')\n")
        self.write("ignored.txt", "ignored\n")

        files = self.gm.enumerate_files(self.root, "demo")
        expected_sha = hashlib.sha256(b"print('a')\n").hexdigest()
        self.assertEqual(expected_sha, files["src/a.py"])
        self.assertIn("src/untracked.py", files)
        self.assertIn("docs/keep.md", files)
        self.assertNotIn("src/deleted.py", files)
        self.assertNotIn("ignored.txt", files)
        for rel in tracked:
            if rel in ("src/a.py", "docs/keep.md"):
                continue
            self.assertNotIn(rel, files)

    def test_enumerate_files_git_failure_includes_stderr(self):
        failure = subprocess.CompletedProcess(
            ["git"], 1, stdout="", stderr="fatal: not a git repository\n"
        )
        with mock.patch.object(self.gm.subprocess, "run", return_value=failure):
            with self.assertRaisesRegex(RuntimeError, "fatal: not a git repository"):
                self.gm.enumerate_files(self.root, "demo")

    def test_fingerprint_is_stable(self):
        files = {"src/b.py": "b" * 32, "src/a.py": "a" * 32}
        canonical = json.dumps(files, sort_keys=True, separators=(",", ":"))
        expected = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        self.assertEqual(expected, self.gm.fingerprint(files))
        reordered = {"src/a.py": files["src/a.py"], "src/b.py": files["src/b.py"]}
        self.assertEqual(self.gm.fingerprint(files), self.gm.fingerprint(reordered))
        changed = dict(files)
        changed["src/a.py"] = "c" * 32
        self.assertNotEqual(self.gm.fingerprint(files), self.gm.fingerprint(changed))


if __name__ == "__main__":
    unittest.main()
