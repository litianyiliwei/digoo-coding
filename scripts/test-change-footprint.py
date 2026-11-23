#!/usr/bin/env python3
"""Regression tests for ``check-change-footprint.py``.

Covers the declaration gate used by stage 07 and the diff/verify gates used by
stages 08 and 09:

* ``--declaration-only`` requires the module-package slice fields and validates
  owned/code-package containment, integration entries and frozen approvals;
* ``footprint`` requires only owned/integration and treats ``Owner module: N/A``
  as absent;
* diff mode diffs the current workspace against ``implementation-base.json``
  (added/modified/deleted), excludes Change/workflow files, ignores files that
  were already dirty at snapshot time, and writes ``implementation-diff.json``;
* module ``shared_paths`` changes need an owned entry inside that shared path;
* frozen layout paths need an approved BCR in ``Frozen approvals``;
* ``--verify`` recomputes the diff from the same base and compares the path set
  and ``diff_sha256``;
* ``strategy=none`` (or a missing layout) skips the whole gate.
"""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

CHECKER = SCRIPTS_DIR / "check-change-footprint.py"
BASE_REL = "openspec/changes/demo/design/evidence/implementation-base.json"
DIFF_REL = "openspec/changes/demo/design/evidence/implementation-diff.json"

import gate_common as gm  # noqa: E402

CAPABILITY_HEADER = (
    "capability_slug,capability_name,domain_id,owner_module,related_modules,"
    "code_packages,status,delivered_slices,remaining_slices,active_changes,notes"
)
MODULE_HEADER = (
    "module_slug,module_name,domain_id,frontend_paths,backend_paths,shared_paths,"
    "capabilities,status,notes"
)

ORDER_FRONTEND = "web/src/features/sales/order/"
ORDER_BACKEND = "server/src/main/java/demo/sales/order/"
ORDER_SHARED = "server/src/main/java/demo/sales/order/shared/"
AUDIT_FRONTEND = "web/src/features/audit/"
AUDIT_BACKEND = "server/src/main/java/demo/audit/"

VALID_SLICE = """### Implementation Slice
- Primary capability: order-create
- Owner module: order
- Related modules: audit
- Slice type/coverage: initial / full
- Code packages: server/src/main/java/demo/sales/order/; web/src/features/sales/order/
- Owned paths: server/src/main/java/demo/sales/order/export/; web/src/features/sales/order/components/
- Integration paths:
  - web/src/router/routes.ts — register order routes; task T-001
  - server/src/main/java/demo/config/ApplicationConfig.java — register beans; task T-001
- Module card: update web/src/features/sales/order/MODULE.md
- Frozen approvals: N/A
"""

DEFAULT_FILES = {
    "web/src/features/sales/order/components/OrderList.vue": "<template>list</template>\n",
    "web/src/features/sales/order/MODULE.md": "# Order module\n",
    "server/src/main/java/demo/sales/order/export/ExportService.java": "class ExportService {}\n",
    "server/src/main/java/demo/sales/order/shared/SharedHelper.java": "class SharedHelper {}\n",
    "server/src/main/java/demo/config/ApplicationConfig.java": "class ApplicationConfig {}\n",
    "web/src/features/audit/components/AuditLog.vue": "<template>audit</template>\n",
    "web/src/router/routes.ts": "export const routes = [];\n",
    "web/src/ui/Button.vue": "<template>button</template>\n",
    "docs/architecture/system-context.md": "# system context\n",
    "README.md": "# demo\n",
    "openspec/changes/demo/proposal.md": "# proposal\n",
}


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load(root: Path):
    spec = importlib.util.spec_from_file_location("check_change_footprint", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    return module


class ChangeFootprintTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.mod = load(self.root)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test User")
        self.write_layout()
        self.write_registries()
        for relpath, text in DEFAULT_FILES.items():
            self.write(relpath, text)
        self.write_design(VALID_SLICE)

    def tearDown(self):
        self._tmp.cleanup()

    # -- helpers -------------------------------------------------------
    def write(self, rel: str, text: str) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    def write_json(self, rel: str, doc: dict) -> Path:
        return self.write(rel, json.dumps(doc, indent=2) + "\n")

    def read_json(self, rel: str) -> dict:
        return json.loads((self.root / rel).read_text(encoding="utf-8"))

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

    def commit(self, message: str = "init") -> None:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)

    def write_layout(self, strategy: str = "module-packages") -> None:
        layout = {
            "version": 1,
            "strategy": strategy,
            "roots": {"backend": "server/", "frontend": "web/"},
            "integration_paths": [
                "web/src/router/routes.ts",
                "server/src/main/java/<org>/config/ApplicationConfig.java",
            ],
            "frozen_paths": [
                "server/src/main/java/<org>/platform/**",
                "web/src/ui/**",
            ],
            "module_card": "MODULE.md",
        }
        self.write("docs/architecture/code-layout.json", json.dumps(layout))

    def write_registries(self) -> None:
        self.write(
            "docs/product/modules.csv",
            "\n".join(
                [
                    MODULE_HEADER,
                    f"order,Order,DOM-001,{ORDER_FRONTEND},{ORDER_BACKEND},"
                    f"{ORDER_SHARED},order-create,ACTIVE,N/A",
                    f"audit,Audit,DOM-001,{AUDIT_FRONTEND},{AUDIT_BACKEND},"
                    "N/A,N/A,ACTIVE,N/A",
                ]
            )
            + "\n",
        )
        self.write(
            "docs/product/capabilities.csv",
            "\n".join(
                [
                    CAPABILITY_HEADER,
                    "order-create,Order Create,DOM-001,order,audit,N/A,"
                    "ACTIVE,N/A,N/A,N/A,N/A",
                ]
            )
            + "\n",
        )

    def write_design(self, slice_text: str) -> None:
        self.write(
            "openspec/changes/demo/design.md",
            "## Design Decisions\n\n" + slice_text + "\n",
        )

    def write_base(self) -> dict:
        files = gm.enumerate_files(self.root, "demo")
        doc = {
            "schema_version": "1.0",
            "change_id": "demo",
            "captured_at": datetime.now(timezone.utc)
            .replace(microsecond=0)
            .isoformat(),
            "head": "0" * 40,
            "files": files,
            "fingerprint": gm.fingerprint(files),
        }
        self.write_json(BASE_REL, doc)
        return doc

    def run_cli(self, *args: str):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = self.mod.main(list(args))
        return code, out.getvalue(), err.getvalue()

    # -- declaration gate ---------------------------------------------
    def test_declaration_only_valid_passes(self):
        code, out, err = self.run_cli("demo", "--declaration-only")
        self.assertEqual(0, code, err)
        self.assertIn("FOOTPRINT_CHECK=PASSED", out)
        self.assertNotIn("ERROR", out + err)

    def test_module_card_change_is_implicitly_owned(self):
        # The slice owns a backend resource directory only; the web module card
        # is not in Owned paths and must still pass the footprint gate.
        self.write_base()
        self.write(f"{ORDER_FRONTEND}MODULE.md", "# Order module v2\n")
        code, out, err = self.run_cli("demo")
        self.assertEqual(0, code, err)
        self.assertEqual(
            [f"{ORDER_FRONTEND}MODULE.md"],
            [item["path"] for item in self.read_json(DIFF_REL)["changed_paths"]],
        )

    def test_custom_layout_module_card_is_implicitly_owned(self):
        layout = self.read_json("docs/architecture/code-layout.json")
        layout["module_card"] = "MODULE-CARD.md"
        self.write_json("docs/architecture/code-layout.json", layout)
        card = f"{ORDER_FRONTEND}MODULE-CARD.md"
        self.write(card, "# Order module card\n")
        self.write_base()
        self.write(card, "# Order module card v2\n")
        code, out, err = self.run_cli("demo")
        self.assertEqual(0, code, err)
        self.assertEqual(
            [card],
            [item["path"] for item in self.read_json(DIFF_REL)["changed_paths"]],
        )

    def test_integration_paths_n_a_or_empty_is_valid(self):
        for value in ("N/A + no thin registration changes", ""):
            with self.subTest(value=value):
                lines = [
                    line
                    for line in VALID_SLICE.splitlines()
                    if not line.strip().startswith(
                        ("- web/src/router/routes.ts", "- server/src/main/java/demo/config")
                    )
                ]
                text = "\n".join(lines).replace(
                    "- Integration paths:", f"- Integration paths: {value}".rstrip()
                ) + "\n"
                self.write_design(text)
                code, out, err = self.run_cli("demo", "--declaration-only")
                self.assertEqual(0, code, err)
                self.assertIn("FOOTPRINT_CHECK=PASSED", out)

    def test_footprint_integration_paths_n_a_is_valid(self):
        self.write_layout("footprint")
        self.write_design(
            "### Implementation Slice\n"
            "- Owner module: N/A\n"
            "- Owned paths: web/src/features/sales/order/**\n"
            "- Integration paths: N/A + no global registration changed\n"
        )
        code, out, err = self.run_cli("demo", "--declaration-only")
        self.assertEqual(0, code, err)

    def test_integration_n_a_does_not_cover_integration_changes(self):
        text = VALID_SLICE
        for line in (
            "  - web/src/router/routes.ts — register order routes; task T-001",
            "  - server/src/main/java/demo/config/ApplicationConfig.java — register beans; task T-001",
        ):
            text = text.replace(line + "\n", "")
        text = text.replace(
            "- Integration paths:", "- Integration paths: N/A + no thin registration changes"
        )
        self.write_design(text)
        self.write_base()
        self.write("web/src/router/routes.ts", "export const routes = [2];\n")
        code, out, err = self.run_cli("demo")
        self.assertEqual(1, code)
        self.assertIn("not owned", out + err)
        self.assertFalse((self.root / DIFF_REL).exists())

    def test_missing_required_field_fails(self):
        text = VALID_SLICE.replace(
            "- Owned paths: server/src/main/java/demo/sales/order/export/; "
            "web/src/features/sales/order/components/\n",
            "",
        )
        self.assertNotEqual(VALID_SLICE, text)
        self.write_design(text)
        code, out, err = self.run_cli("demo", "--declaration-only")
        self.assertEqual(1, code)
        self.assertIn("Owned paths", out + err)

    def test_owned_path_outside_registered_module_fails(self):
        text = VALID_SLICE.replace(
            "server/src/main/java/demo/sales/order/export/; "
            "web/src/features/sales/order/components/",
            "web/src/features/billing/components/",
        )
        self.write_design(text)
        code, out, err = self.run_cli("demo", "--declaration-only")
        self.assertEqual(1, code)
        self.assertIn("outside the owner/related module paths", out + err)

    def test_unsafe_owned_path_is_rejected(self):
        for bad in ("../escape/", "/abs/path/", "web/src/features/sales/order/bad*"):
            with self.subTest(bad=bad):
                text = VALID_SLICE.replace(
                    "server/src/main/java/demo/sales/order/export/; "
                    "web/src/features/sales/order/components/",
                    bad,
                )
                self.write_design(text)
                code, out, err = self.run_cli("demo", "--declaration-only")
                self.assertEqual(1, code)
                self.assertIn("ERROR", out + err)

    def test_trailing_subtree_marker_is_normalized(self):
        text = VALID_SLICE.replace(
            "server/src/main/java/demo/sales/order/export/; "
            "web/src/features/sales/order/components/",
            "server/src/main/java/demo/sales/order/export/**; "
            "web/src/features/sales/order/components/**",
        )
        self.write_design(text)
        code, out, err = self.run_cli("demo", "--declaration-only")
        self.assertEqual(0, code, err)

    def test_integration_entry_needs_reason_and_task(self):
        cases = {
            "missing task": (
                "  - web/src/router/routes.ts — register order routes",
                "task <TASK-ID>",
            ),
            "missing reason": (
                "  - web/src/router/routes.ts — ; task T-001",
                "must state a reason",
            ),
            "not in layout": (
                "  - web/src/other/registry.ts — register; task T-001",
                "does not match code-layout.json integration_paths",
            ),
        }
        original = "  - web/src/router/routes.ts — register order routes; task T-001"
        for name, (replacement, fragment) in cases.items():
            with self.subTest(name=name):
                self.write_design(VALID_SLICE.replace(original, replacement))
                code, out, err = self.run_cli("demo", "--declaration-only")
                self.assertEqual(1, code)
                self.assertIn(fragment, out + err)

    def test_code_package_outside_registered_module_fails(self):
        text = VALID_SLICE.replace(
            "- Code packages: server/src/main/java/demo/sales/order/; "
            "web/src/features/sales/order/",
            "- Code packages: web/src/features/billing/",
        )
        self.write_design(text)
        code, out, err = self.run_cli("demo", "--declaration-only")
        self.assertEqual(1, code)
        self.assertIn("outside the owner/related module paths", out + err)

    def test_integration_org_placeholder_matches_concrete_path(self):
        self.write_base()
        self.write(
            "server/src/main/java/demo/config/ApplicationConfig.java",
            "class ApplicationConfig { int beans; }\n",
        )
        code, out, err = self.run_cli("demo")
        self.assertEqual(0, code, err)
        self.assertEqual(
            ["server/src/main/java/demo/config/ApplicationConfig.java"],
            [item["path"] for item in self.read_json(DIFF_REL)["changed_paths"]],
        )

    def test_footprint_mode_requires_only_owned_and_integration(self):
        self.write_layout("footprint")
        self.write_design(
            "### Implementation Slice\n"
            "- Owner module: N/A\n"
            "- Owned paths: web/src/features/sales/order/**\n"
            "- Integration paths:\n"
            "  - web/src/router/routes.ts — register route; task T-001\n"
            "- Frozen approvals: N/A\n"
        )
        code, out, err = self.run_cli("demo", "--declaration-only")
        self.assertEqual(0, code, err)

    def test_strategy_none_skips(self):
        (self.root / "docs/architecture/code-layout.json").unlink()
        code, out, err = self.run_cli("demo", "--declaration-only")
        self.assertEqual(0, code, err)
        self.assertIn("FOOTPRINT_CHECK=SKIPPED (strategy none)", out)

        code, out, err = self.run_cli("demo")
        self.assertEqual(0, code, err)
        self.assertIn("FOOTPRINT_CHECK=SKIPPED (strategy none)", out)
        self.assertFalse((self.root / DIFF_REL).exists())

    # -- diff mode ----------------------------------------------------
    def test_diff_generation_with_added_modified_deleted(self):
        self.write(f"{ORDER_BACKEND}export/OldService.java", "class OldService {}\n")
        base = self.write_base()
        self.write(f"{ORDER_BACKEND}export/ExportService.java", "class ExportService { int x; }\n")
        self.write(f"{ORDER_BACKEND}export/ExportJob.java", "class ExportJob {}\n")
        (self.root / f"{ORDER_BACKEND}export/OldService.java").unlink()

        code, out, err = self.run_cli("demo")
        self.assertEqual(0, code, err)
        self.assertTrue((self.root / DIFF_REL).is_file())

        doc = self.read_json(DIFF_REL)
        self.assertEqual("1.0", doc["schema_version"])
        self.assertEqual("demo", doc["change_id"])
        self.assertEqual(base["fingerprint"], doc["base_fingerprint"])
        generated = datetime.fromisoformat(doc["generated_at"])
        self.assertEqual(timezone.utc.utcoffset(generated), generated.utcoffset())
        self.assertEqual(
            [
                {
                    "path": f"{ORDER_BACKEND}export/ExportJob.java",
                    "status": "added",
                    "sha256": sha256("class ExportJob {}\n"),
                },
                {
                    "path": f"{ORDER_BACKEND}export/ExportService.java",
                    "status": "modified",
                    "sha256": sha256("class ExportService { int x; }\n"),
                },
                {
                    "path": f"{ORDER_BACKEND}export/OldService.java",
                    "status": "deleted",
                    "sha256": base["files"][f"{ORDER_BACKEND}export/OldService.java"],
                },
            ],
            doc["changed_paths"],
        )
        self.assertEqual(
            self.mod.diff_hash(doc["changed_paths"]), doc["diff_sha256"]
        )

    def test_excluded_change_and_workflow_files_ignored(self):
        base = self.write_base()
        self.write("openspec/changes/demo/notes.md", "# note\n")
        self.write("openspec/changes/demo/design/evidence/other.json", "{}\n")
        self.write("openspec/changes/archive/old/design.md", "# old\n")
        self.write("workflow/evidence/run.json", "{}\n")
        self.write("workflow-state.json", "{}\n")
        self.write("docs/architecture/baseline-status.md", "# status\n")

        code, out, err = self.run_cli("demo")
        self.assertEqual(0, code, err)
        doc = self.read_json(DIFF_REL)
        self.assertEqual([], doc["changed_paths"])
        self.assertEqual(base["fingerprint"], doc["base_fingerprint"])

    def test_preexisting_dirty_file_not_counted(self):
        self.commit()
        self.write(f"{ORDER_FRONTEND}components/OrderList.vue", "<template>dirty</template>\n")
        self.write("notes-untracked.txt", "already here\n")
        self.write_base()

        code, out, err = self.run_cli("demo")
        self.assertEqual(0, code, err)
        self.assertEqual([], self.read_json(DIFF_REL)["changed_paths"])

    def test_unclassified_change_fails_and_writes_nothing(self):
        self.write_base()
        self.write("README.md", "# changed\n")
        code, out, err = self.run_cli("demo")
        self.assertEqual(1, code)
        self.assertIn("not owned", out + err)
        self.assertFalse((self.root / DIFF_REL).exists())

    def test_integration_change_must_be_declared(self):
        self.write_base()
        self.write("web/src/router/routes.ts", "export const routes = [1];\n")
        code, out, err = self.run_cli("demo")
        self.assertEqual(0, code, err)
        self.assertEqual(
            ["web/src/router/routes.ts"],
            [item["path"] for item in self.read_json(DIFF_REL)["changed_paths"]],
        )

    def test_shared_path_change_requires_owned_narrowing(self):
        self.write_base()
        self.write(f"{ORDER_SHARED}SharedHelper.java", "class SharedHelper { int y; }\n")
        code, out, err = self.run_cli("demo")
        self.assertEqual(1, code)
        self.assertIn("shared", out + err)
        self.assertFalse((self.root / DIFF_REL).exists())

    def test_shared_path_change_passes_when_narrowed(self):
        text = VALID_SLICE.replace(
            "server/src/main/java/demo/sales/order/export/;",
            f"{ORDER_SHARED};",
        )
        self.write_design(text)
        self.write_base()
        self.write(f"{ORDER_SHARED}SharedHelper.java", "class SharedHelper { int y; }\n")
        code, out, err = self.run_cli("demo")
        self.assertEqual(0, code, err)
        self.assertEqual(
            [f"{ORDER_SHARED}SharedHelper.java"],
            [item["path"] for item in self.read_json(DIFF_REL)["changed_paths"]],
        )

    def test_shared_path_sibling_owned_entry_does_not_cover_change(self):
        # An owned entry inside the shared directory covers only its own subtree;
        # a change under a sibling resource still needs its own narrowing entry.
        text = VALID_SLICE.replace(
            "server/src/main/java/demo/sales/order/export/;",
            f"{ORDER_SHARED}export/;",
        )
        self.write_design(text)
        self.write_base()
        self.write(f"{ORDER_SHARED}SharedHelper.java", "class SharedHelper { int z; }\n")
        code, out, err = self.run_cli("demo")
        self.assertEqual(1, code)
        self.assertIn("shared", out + err)
        self.assertIn("contains the changed file", out + err)
        self.assertFalse((self.root / DIFF_REL).exists())

    def test_frozen_change_requires_bcr_approval(self):
        self.write_base()
        self.write("web/src/ui/Button.vue", "<template>button v2</template>\n")
        code, out, err = self.run_cli("demo")
        self.assertEqual(1, code)
        self.assertIn("frozen", out + err)
        self.assertFalse((self.root / DIFF_REL).exists())

        self.write_design(
            VALID_SLICE.replace(
                "- Frozen approvals: N/A",
                "- Frozen approvals:\n  - BCR-001 — web/src/ui/",
            )
        )
        code, out, err = self.run_cli("demo")
        self.assertEqual(0, code, err)
        self.assertEqual(
            ["web/src/ui/Button.vue"],
            [item["path"] for item in self.read_json(DIFF_REL)["changed_paths"]],
        )

    def test_architecture_baseline_change_requires_bcr(self):
        self.write_base()
        self.write("docs/architecture/system-context.md", "# system context v2\n")
        code, out, err = self.run_cli("demo")
        self.assertEqual(1, code)
        self.assertIn("frozen", out + err)
        self.assertFalse((self.root / DIFF_REL).exists())

        self.write_design(
            VALID_SLICE.replace(
                "- Frozen approvals: N/A",
                "- Frozen approvals:\n  - BCR-001 — docs/architecture/system-context.md",
            )
        )
        code, out, err = self.run_cli("demo")
        self.assertEqual(0, code, err)
        self.assertEqual(
            ["docs/architecture/system-context.md"],
            [item["path"] for item in self.read_json(DIFF_REL)["changed_paths"]],
        )

    def test_multiroots_owned_paths_match(self):
        self.write_base()
        self.write(f"{ORDER_BACKEND}export/ExportService.java", "class ExportService { int z; }\n")
        self.write(f"{ORDER_FRONTEND}components/OrderList.vue", "<template>v2</template>\n")
        code, out, err = self.run_cli("demo")
        self.assertEqual(0, code, err)
        self.assertEqual(
            [
                {
                    "path": f"{ORDER_BACKEND}export/ExportService.java",
                    "status": "modified",
                    "sha256": sha256("class ExportService { int z; }\n"),
                },
                {
                    "path": f"{ORDER_FRONTEND}components/OrderList.vue",
                    "status": "modified",
                    "sha256": sha256("<template>v2</template>\n"),
                },
            ],
            self.read_json(DIFF_REL)["changed_paths"],
        )

    def test_missing_base_fails(self):
        code, out, err = self.run_cli("demo")
        self.assertEqual(1, code)
        self.assertIn("implementation-base.json", out + err)
        self.assertFalse((self.root / DIFF_REL).exists())

    # -- verify -------------------------------------------------------
    def test_verify_matches_after_diff(self):
        self.write_base()
        self.write(f"{ORDER_BACKEND}export/ExportService.java", "class ExportService { int q; }\n")
        self.assertEqual(0, self.run_cli("demo")[0])
        code, out, err = self.run_cli("demo", "--verify")
        self.assertEqual(0, code, err)
        self.assertIn("FOOTPRINT_CHECK=PASSED", out)

    def test_verify_mismatch_fails(self):
        self.write_base()
        self.write(f"{ORDER_BACKEND}export/ExportService.java", "class ExportService { int q; }\n")
        self.assertEqual(0, self.run_cli("demo")[0])
        # A later owned file changes the recomputed path set, so the stored diff
        # no longer matches even though both paths are in scope.
        self.write(f"{ORDER_BACKEND}export/ExportJob.java", "class ExportJob {}\n")
        code, out, err = self.run_cli("demo", "--verify")
        self.assertEqual(1, code)
        self.assertIn("does not match", out + err)

    def test_verify_detects_content_change_after_diff(self):
        self.write_base()
        self.write(f"{ORDER_BACKEND}export/ExportService.java", "class ExportService { int q; }\n")
        self.assertEqual(0, self.run_cli("demo")[0])
        # Same path and status, different content: only the pinned sha256 can
        # tell the two workspace states apart.
        self.write(f"{ORDER_BACKEND}export/ExportService.java", "class ExportService { int q2; }\n")
        code, out, err = self.run_cli("demo", "--verify")
        self.assertEqual(1, code)
        self.assertIn("does not match", out + err)

    def test_verify_without_stored_diff_fails(self):
        self.write_base()
        code, out, err = self.run_cli("demo", "--verify")
        self.assertEqual(1, code)
        self.assertIn("implementation-diff.json", out + err)

    def test_verify_reruns_classification(self):
        self.write_base()
        self.write(f"{ORDER_BACKEND}export/ExportService.java", "class ExportService { int q; }\n")
        self.assertEqual(0, self.run_cli("demo")[0])
        self.write("README.md", "# changed after 08\n")
        code, out, err = self.run_cli("demo", "--verify")
        self.assertEqual(1, code)
        self.assertIn("does not match", out + err)
        self.assertIn("not owned", out + err)


if __name__ == "__main__":
    unittest.main()
