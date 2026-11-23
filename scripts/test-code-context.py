#!/usr/bin/env python3
"""Regression tests for ``code-context.py`` (stage-08 implementation context manifest).

Covers:

* owned files expanded from the slice ``Owned paths`` prefixes (subtrees,
  trailing ``/**`` normalization, nested resources, multi-root);
* ``MODULE.md`` cards for owner/related modules, with missing cards recorded
  under ``missing`` without failing;
* existing change-scoped contracts (``api/openapi.yaml``, ``design/*.csv``) and
  the test matrix, plus both product registries;
* slice integration paths with their reasons;
* other registered modules' paths under ``not_needed``;
* ``strategy=none`` (missing or explicit) skipping generation without writing;
* unknown owner/related modules or missing required slice fields exiting 1 with
  path-bearing errors and no partial manifest;
* output shape against ``templates/change-assets/design/context-manifest.schema.json``.
"""
from __future__ import annotations

import contextlib
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

GENERATOR = SCRIPTS_DIR / "code-context.py"
DESIGN_REL = "openspec/changes/demo/design.md"
MANIFEST_REL = "openspec/changes/demo/design/context-manifest.json"
CHANGE_PREFIX = "openspec/changes/demo"

CAPABILITY_HEADER = (
    "capability_slug,capability_name,domain_id,owner_module,related_modules,"
    "code_packages,status,delivered_slices,remaining_slices,active_changes,notes"
)
MODULE_HEADER = (
    "module_slug,module_name,domain_id,frontend_paths,backend_paths,shared_paths,"
    "capabilities,status,notes"
)

ORDER_FE = "web/src/features/sales/order/"
ORDER_BE = "server/src/main/java/demo/sales/order/"
AUDIT_FE = "web/src/features/audit/"
AUDIT_BE = "server/src/main/java/demo/audit/"
BILLING_FE = "web/src/features/billing/"
BILLING_BE = "server/src/main/java/demo/billing/"

MAX_CATEGORIES = {
    "owned",
    "module-card",
    "contract",
    "test",
    "integration",
    "registry",
}

VALID_SLICE = """### Implementation Slice
- Primary capability: order-create
- Owner module: order
- Related modules: audit
- Slice type/coverage: initial / full
- Code packages: server/src/main/java/demo/sales/order/; web/src/features/sales/order/
- Owned paths: server/src/main/java/demo/sales/order/export/; web/src/features/sales/order/components/
- Integration paths:
  - web/src/router/routes.ts — register order routes; task T-001
- Module card: update web/src/features/sales/order/MODULE.md
- Frozen approvals: N/A
"""

DEFAULT_FILES = {
    "web/src/features/sales/order/components/OrderList.vue": "<template>list</template>\n",
    "web/src/features/sales/order/components/detail/OrderDetail.vue": "<template>detail</template>\n",
    "web/src/features/sales/order/OrderPage.vue": "<template>page</template>\n",
    "web/src/features/sales/order/MODULE.md": "# Order module\n",
    "server/src/main/java/demo/sales/order/export/ExportService.java": "class ExportService {}\n",
    "server/src/main/java/demo/sales/order/MODULE.md": "# Order backend module\n",
    "web/src/features/audit/MODULE.md": "# Audit module\n",
    "server/src/main/java/demo/audit/MODULE.md": "# Audit backend module\n",
    "web/src/features/billing/MODULE.md": "# Billing module\n",
    "server/src/main/java/demo/billing/BillingService.java": "class BillingService {}\n",
    "web/src/router/routes.ts": "export const routes = [];\n",
    f"{CHANGE_PREFIX}/api/openapi.yaml": "openapi: 3.0.0\n",
}

CONTRACT_FILES = {
    f"{CHANGE_PREFIX}/design/interface-catalog.csv": "interface_id,name\n",
    f"{CHANGE_PREFIX}/design/io-catalog.csv": "io_id,name\n",
    f"{CHANGE_PREFIX}/design/api-io-mapping.csv": "operation_id,io_ids\n",
    f"{CHANGE_PREFIX}/design/ui-actions.csv": "page_id,element_id\n",
}
TEST_FILES = {f"{CHANGE_PREFIX}/design/test-cases.csv": "test_id,ac_ids\n"}


def load(root: Path):
    if not GENERATOR.is_file():
        raise FileNotFoundError(f"missing {GENERATOR}")
    spec = importlib.util.spec_from_file_location("code_context", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    return module


class CodeContextTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test User")
        self.write_layout()
        self.write_registries()
        for relpath, text in DEFAULT_FILES.items():
            self.write(relpath, text)
        for relpath, text in CONTRACT_FILES.items():
            self.write(relpath, text)
        for relpath, text in TEST_FILES.items():
            self.write(relpath, text)
        self.write_design(VALID_SLICE)
        self.mod = load(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    # -- helpers -------------------------------------------------------
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

    def write_layout(self, strategy: str = "module-packages") -> None:
        layout = {
            "version": 1,
            "strategy": strategy,
            "roots": {"backend": "server/", "frontend": "web/"},
            "integration_paths": ["web/src/router/routes.ts"],
            "frozen_paths": ["web/src/ui/**"],
            "module_card": "MODULE.md",
        }
        self.write("docs/architecture/code-layout.json", json.dumps(layout))

    def remove_layout(self) -> None:
        (self.root / "docs/architecture/code-layout.json").unlink()

    def write_registries(self) -> None:
        self.write(
            "docs/product/modules.csv",
            "\n".join(
                [
                    MODULE_HEADER,
                    f"order,Order,DOM-001,{ORDER_FE},{ORDER_BE},"
                    "N/A,order-create,ACTIVE,N/A",
                    f"audit,Audit,DOM-001,{AUDIT_FE},{AUDIT_BE},"
                    "N/A,N/A,ACTIVE,N/A",
                    f"billing,Billing,DOM-001,{BILLING_FE},{BILLING_BE},"
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
        self.write(DESIGN_REL, "## Design Decisions\n\n" + slice_text + "\n")

    def read_manifest(self) -> dict:
        return json.loads((self.root / MANIFEST_REL).read_text(encoding="utf-8"))

    def run_cli(self, *args: str):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = self.mod.main(list(args))
        return code, out.getvalue(), err.getvalue()

    def generate(self) -> dict:
        code, out, err = self.run_cli("demo")
        self.assertEqual(0, code, out + err)
        self.assertNotIn("ERROR", out + err)
        return self.read_manifest()

    def entries(self, doc: dict, category: str) -> list[dict]:
        return [item for item in doc["read_set"] if item["category"] == category]

    # -- owned files + module cards -----------------------------------
    def test_generates_owned_files_and_module_cards(self):
        doc = self.generate()

        self.assertEqual("demo", doc["change_id"])
        self.assertEqual("order-create", doc["capability"])
        generated = datetime.fromisoformat(doc["generated_at"])
        self.assertIsNotNone(generated.tzinfo)
        self.assertEqual(timezone.utc.utcoffset(generated), generated.utcoffset())

        owned = {item["path"] for item in self.entries(doc, "owned")}
        self.assertIn(
            "web/src/features/sales/order/components/OrderList.vue", owned
        )
        self.assertIn(
            "web/src/features/sales/order/components/detail/OrderDetail.vue", owned
        )
        self.assertIn(
            "server/src/main/java/demo/sales/order/export/ExportService.java", owned
        )
        # A file in the owner module but outside the owned prefix is not in the set.
        self.assertNotIn("web/src/features/sales/order/OrderPage.vue", owned)

        cards = {item["path"] for item in self.entries(doc, "module-card")}
        self.assertEqual(
            {
                "web/src/features/sales/order/MODULE.md",
                "server/src/main/java/demo/sales/order/MODULE.md",
                "web/src/features/audit/MODULE.md",
                "server/src/main/java/demo/audit/MODULE.md",
            },
            cards,
        )
        for entry in doc["read_set"]:
            self.assertTrue(entry["reason"].strip(), entry)

    def test_trailing_subtree_marker_normalizes_to_prefix(self):
        text = VALID_SLICE.replace(
            "server/src/main/java/demo/sales/order/export/; "
            "web/src/features/sales/order/components/",
            "server/src/main/java/demo/sales/order/export/**; "
            "web/src/features/sales/order/components/**",
        )
        self.write_design(text)
        doc = self.generate()
        owned = self.entries(doc, "owned")
        self.assertTrue(
            all("/**" not in item["path"] for item in owned),
            owned,
        )
        self.assertIn(
            "web/src/features/sales/order/components/detail/OrderDetail.vue",
            {item["path"] for item in owned},
        )
        for item in owned:
            self.assertNotIn("/**", item["reason"])

    def test_missing_module_card_reported_without_failing(self):
        (self.root / "web/src/features/audit/MODULE.md").unlink()
        doc = self.generate()

        missing = {item["path"]: item for item in doc["missing"]}
        self.assertIn("web/src/features/audit/MODULE.md", missing)
        self.assertEqual("module-card", missing["web/src/features/audit/MODULE.md"]["category"])
        self.assertTrue(missing["web/src/features/audit/MODULE.md"]["reason"].strip())
        cards = {item["path"] for item in self.entries(doc, "module-card")}
        self.assertNotIn("web/src/features/audit/MODULE.md", cards)
        self.assertIn("web/src/features/sales/order/MODULE.md", cards)

    # -- contracts / tests / integration -------------------------------
    def test_includes_contracts_and_test_assets(self):
        doc = self.generate()
        contract_paths = {item["path"] for item in self.entries(doc, "contract")}
        self.assertEqual(
            {
                f"{CHANGE_PREFIX}/api/openapi.yaml",
                f"{CHANGE_PREFIX}/design/interface-catalog.csv",
                f"{CHANGE_PREFIX}/design/io-catalog.csv",
                f"{CHANGE_PREFIX}/design/api-io-mapping.csv",
                f"{CHANGE_PREFIX}/design/ui-actions.csv",
            },
            contract_paths,
        )
        self.assertEqual(
            {f"{CHANGE_PREFIX}/design/test-cases.csv"},
            {item["path"] for item in self.entries(doc, "test")},
        )

    def test_absent_contract_assets_are_not_included(self):
        (self.root / f"{CHANGE_PREFIX}/design/ui-actions.csv").unlink()
        (self.root / f"{CHANGE_PREFIX}/design/io-catalog.csv").unlink()
        doc = self.generate()
        contract_paths = {item["path"] for item in self.entries(doc, "contract")}
        self.assertNotIn(f"{CHANGE_PREFIX}/design/ui-actions.csv", contract_paths)
        self.assertNotIn(f"{CHANGE_PREFIX}/design/io-catalog.csv", contract_paths)
        self.assertIn(f"{CHANGE_PREFIX}/design/interface-catalog.csv", contract_paths)

    def test_integration_paths_included_with_reason(self):
        doc = self.generate()
        integration = self.entries(doc, "integration")
        self.assertEqual(
            {"web/src/router/routes.ts"}, {item["path"] for item in integration}
        )
        self.assertIn("register order routes", integration[0]["reason"])

    def test_integration_paths_n_a_generates_no_integration_entries(self):
        lines = [
            line
            for line in VALID_SLICE.splitlines()
            if not line.strip().startswith("- web/src/router/routes.ts")
        ]
        text = "\n".join(lines).replace(
            "- Integration paths:",
            "- Integration paths: N/A + no thin registration changes",
        ) + "\n"
        self.write_design(text)
        doc = self.generate()
        self.assertEqual([], self.entries(doc, "integration"))

    def test_footprint_integration_paths_n_a_generates_no_entries(self):
        self.write_layout("footprint")
        self.write_design(
            "### Implementation Slice\n"
            "- Primary capability: N/A\n"
            "- Owner module: N/A\n"
            "- Owned paths: web/src/features/sales/order/components/\n"
            "- Integration paths: N/A + no thin registration changes\n"
        )
        doc = self.generate()
        self.assertEqual([], self.entries(doc, "integration"))

    def test_custom_layout_module_card_paths(self):
        layout = {
            "version": 1,
            "strategy": "module-packages",
            "roots": {"backend": "server/", "frontend": "web/"},
            "integration_paths": ["web/src/router/routes.ts"],
            "module_card": "MODULE-CARD.md",
        }
        self.write("docs/architecture/code-layout.json", json.dumps(layout))
        for prefix in (ORDER_FE, ORDER_BE, AUDIT_FE, AUDIT_BE):
            self.write(f"{prefix}MODULE-CARD.md", "# Custom card\n")
        doc = self.generate()
        cards = {item["path"] for item in self.entries(doc, "module-card")}
        self.assertEqual(
            {
                f"{ORDER_FE}MODULE-CARD.md",
                f"{ORDER_BE}MODULE-CARD.md",
                f"{AUDIT_FE}MODULE-CARD.md",
                f"{AUDIT_BE}MODULE-CARD.md",
            },
            cards,
        )
        self.assertFalse(any(path.endswith("/MODULE.md") for path in cards))

    # -- other modules -------------------------------------------------
    def test_other_modules_in_not_needed(self):
        doc = self.generate()
        not_needed = {item["path"]: item for item in doc["not_needed"]}
        self.assertEqual(
            {"web/src/features/billing", "server/src/main/java/demo/billing"},
            set(not_needed),
        )
        for item in doc["not_needed"]:
            self.assertEqual("other module", item["reason"])
        self.assertNotIn("web/src/features/sales/order", not_needed)
        self.assertNotIn("web/src/features/audit", not_needed)

    # -- strategy none -------------------------------------------------
    def test_strategy_none_skips_generation(self):
        for label, mutate in (
            ("missing layout", self.remove_layout),
            ("explicit none", lambda: self.write_layout("none")),
        ):
            with self.subTest(label=label):
                mutate()
                manifest = self.root / MANIFEST_REL
                if manifest.exists():
                    manifest.unlink()
                code, out, err = self.run_cli("demo")
                self.assertEqual(0, code, err)
                self.assertEqual("CODE_CONTEXT=SKIPPED (strategy none)", out.strip())
                self.assertFalse(manifest.exists())

    # -- failures -------------------------------------------------------
    def test_unknown_owner_module_fails_without_manifest(self):
        self.write_design(
            VALID_SLICE.replace("- Owner module: order", "- Owner module: ghost")
        )
        code, out, err = self.run_cli("demo")
        self.assertEqual(1, code)
        message = out + err
        self.assertIn(DESIGN_REL, message)
        self.assertIn("ghost", message)
        self.assertIn("modules.csv", message)
        self.assertFalse((self.root / MANIFEST_REL).exists())

    def test_unknown_related_module_fails_without_manifest(self):
        self.write_design(
            VALID_SLICE.replace("- Related modules: audit", "- Related modules: ghost")
        )
        code, out, err = self.run_cli("demo")
        self.assertEqual(1, code)
        message = out + err
        self.assertIn(DESIGN_REL, message)
        self.assertIn("ghost", message)
        self.assertFalse((self.root / MANIFEST_REL).exists())

    def test_placeholder_module_path_fails(self):
        self.write(
            "docs/product/modules.csv",
            "\n".join(
                [
                    MODULE_HEADER,
                    "order,Order,DOM-001,"
                    "web/src/features/sales/order/,"
                    "server/src/main/java/<org>/sales/order/,"
                    "N/A,order-create,ACTIVE,N/A",
                ]
            )
            + "\n",
        )
        code, out, err = self.run_cli("demo")
        self.assertEqual(1, code)
        self.assertIn("placeholder", out + err)
        self.assertIn("docs/product/modules.csv", out + err)
        self.assertFalse((self.root / MANIFEST_REL).exists())

    def test_unknown_primary_capability_fails(self):
        self.write_design(
            VALID_SLICE.replace(
                "- Primary capability: order-create", "- Primary capability: ghost"
            )
        )
        code, out, err = self.run_cli("demo")
        self.assertEqual(1, code)
        self.assertIn("ghost", out + err)
        self.assertIn("capabilities.csv", out + err)
        self.assertFalse((self.root / MANIFEST_REL).exists())

    def test_missing_required_slice_field_fails(self):
        for label, replacement in (
            ("Owned paths", "- Owned paths: server/src/main/java/demo/sales/order/export/; "
             "web/src/features/sales/order/components/\n"),
            ("Primary capability", "- Primary capability: order-create\n"),
        ):
            with self.subTest(label=label):
                altered = VALID_SLICE.replace(replacement, "")
                self.assertNotEqual(VALID_SLICE, altered)
                self.write_design(altered)
                code, out, err = self.run_cli("demo")
                self.assertEqual(1, code)
                self.assertIn(label, out + err)
                self.assertFalse((self.root / MANIFEST_REL).exists())
                self.write_design(VALID_SLICE)

    def test_missing_related_modules_field_fails(self):
        line = "- Related modules: audit\n"
        altered = VALID_SLICE.replace(line, "")
        self.assertNotEqual(VALID_SLICE, altered)
        self.write_design(altered)
        code, out, err = self.run_cli("demo")
        self.assertEqual(1, code)
        self.assertIn("Related modules", out + err)
        self.assertFalse((self.root / MANIFEST_REL).exists())

    def test_missing_integration_paths_field_fails(self):
        integration = (
            "- Integration paths:\n"
            "  - web/src/router/routes.ts — register order routes; task T-001\n"
        )
        footprint_slice = (
            "### Implementation Slice\n"
            "- Primary capability: N/A\n"
            "- Owner module: N/A\n"
            "- Owned paths: web/src/features/sales/order/components/\n"
            "- Integration paths:\n"
            "  - web/src/router/routes.ts — register order routes; task T-001\n"
        )
        for label, layout, template in (
            ("module-packages", "module-packages", VALID_SLICE),
            ("footprint", "footprint", footprint_slice),
        ):
            with self.subTest(label=label):
                self.write_layout(layout)
                altered = template.replace(integration, "")
                self.assertNotEqual(template, altered)
                self.write_design(altered)
                code, out, err = self.run_cli("demo")
                self.assertEqual(1, code)
                self.assertIn("Integration paths", out + err)
                self.assertFalse((self.root / MANIFEST_REL).exists())
        self.write_layout()
        self.write_design(VALID_SLICE)

    def test_empty_or_na_owned_paths_fails(self):
        line = (
            "- Owned paths: server/src/main/java/demo/sales/order/export/; "
            "web/src/features/sales/order/components/\n"
        )
        for value in ("", "N/A"):
            with self.subTest(value=repr(value)):
                altered = VALID_SLICE.replace(line, f"- Owned paths: {value}\n")
                self.assertNotEqual(VALID_SLICE, altered)
                self.write_design(altered)
                code, out, err = self.run_cli("demo")
                self.assertEqual(1, code)
                self.assertIn("Owned paths", out + err)
                self.assertFalse((self.root / MANIFEST_REL).exists())
                self.write_design(VALID_SLICE)

    def test_unsafe_owned_path_is_rejected(self):
        self.write_design(
            VALID_SLICE.replace(
                "server/src/main/java/demo/sales/order/export/; "
                "web/src/features/sales/order/components/",
                "../escape/",
            )
        )
        code, out, err = self.run_cli("demo")
        self.assertEqual(1, code)
        self.assertIn("'..' segment", out + err)
        self.assertFalse((self.root / MANIFEST_REL).exists())

    def test_no_partial_manifest_on_error(self):
        self.generate()
        before = (self.root / MANIFEST_REL).read_bytes()
        self.write_design(
            VALID_SLICE.replace("- Owner module: order", "- Owner module: ghost")
        )
        code, out, err = self.run_cli("demo")
        self.assertEqual(1, code)
        self.assertEqual(before, (self.root / MANIFEST_REL).read_bytes())

    def test_missing_design_fails_with_path(self):
        (self.root / DESIGN_REL).unlink()
        code, out, err = self.run_cli("demo")
        self.assertEqual(1, code)
        self.assertIn(DESIGN_REL, out + err)
        self.assertFalse((self.root / MANIFEST_REL).exists())

    # -- footprint + schema --------------------------------------------
    def test_footprint_strategy_uses_na_capability_and_no_module_cards(self):
        self.write_layout("footprint")
        self.write_design(
            "### Implementation Slice\n"
            "- Primary capability: N/A\n"
            "- Owner module: N/A\n"
            "- Owned paths: web/src/features/sales/order/components/\n"
            "- Integration paths:\n"
            "  - web/src/router/routes.ts — register order routes; task T-001\n"
        )
        doc = self.generate()
        self.assertEqual("N/A", doc["capability"])
        self.assertEqual([], self.entries(doc, "module-card"))
        owned = {item["path"] for item in self.entries(doc, "owned")}
        self.assertIn(
            "web/src/features/sales/order/components/OrderList.vue", owned
        )
        not_needed = {item["path"] for item in doc["not_needed"]}
        self.assertIn("web/src/features/billing", not_needed)
        self.assertIn("web/src/features/sales/order", not_needed)

    def test_manifest_matches_schema_shape_and_is_sorted(self):
        doc = self.generate()
        self.assertEqual(
            {"change_id", "capability", "generated_at", "read_set", "not_needed",
             "missing"},
            set(doc),
        )
        for item in doc["read_set"]:
            self.assertEqual({"path", "category", "reason"}, set(item))
            self.assertIn(item["category"], MAX_CATEGORIES)
            self.assertTrue(item["path"])
            self.assertTrue(item["reason"])
        for item in doc["not_needed"]:
            self.assertEqual({"path", "reason"}, set(item))
            self.assertTrue(item["path"])
            self.assertTrue(item["reason"])
        for item in doc["missing"]:
            self.assertEqual({"path", "category", "reason"}, set(item))
            self.assertIn(item["category"], MAX_CATEGORIES)
        for key in ("read_set", "not_needed", "missing"):
            self.assertEqual(
                sorted(item["path"] for item in doc[key]),
                [item["path"] for item in doc[key]],
                key,
            )

    def test_cli_requires_change_id(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as ctx:
                self.mod.main([])
        self.assertEqual(2, ctx.exception.code)


if __name__ == "__main__":
    unittest.main()
