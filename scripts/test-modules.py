#!/usr/bin/env python3
"""Regression tests for the module registry checker."""
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

CHECKER = Path(__file__).with_name("check-modules.py")

MODULE_HEADER = (
    "module_slug,module_name,domain_id,frontend_paths,backend_paths,shared_paths,"
    "capabilities,status,notes"
)

CAPABILITY_HEADER = (
    "capability_slug,capability_name,domain_id,owner_module,related_modules,"
    "status,delivered_slices,remaining_slices,active_changes,notes"
)

DOMAINS = """# Domain Boundaries

| DOM ID | Responsibility | Invariants | Dependency Direction |
|---|---|---|---|
| DOM-001 | Orders | none | inbound |
"""


def load(root: Path):
    spec = importlib.util.spec_from_file_location("check_modules", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    return module


class ModuleCheckerTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.cm = load(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    # -- fixtures -------------------------------------------------------------
    def write(self, rel: str, text: str):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    def layout(
        self,
        strategy="module-packages",
        roots=None,
        module_card="MODULE.md",
        omit_roots=False,
    ):
        doc = {"version": 1, "strategy": strategy, "module_card": module_card}
        if not omit_roots:
            doc["roots"] = (
                roots
                if roots is not None
                else {"backend": "server/", "frontend": "web/"}
            )
        self.write("docs/architecture/code-layout.json", json.dumps(doc))

    def domains(self, text=DOMAINS):
        self.write("docs/architecture/domain-boundaries.md", text)

    def modules(self, rows, header=MODULE_HEADER):
        self.write(
            "docs/product/modules.csv",
            "\n".join([header, *rows]) + "\n",
        )

    def capabilities(self, rows, header=CAPABILITY_HEADER):
        self.write(
            "docs/product/capabilities.csv",
            "\n".join([header, *rows]) + "\n",
        )

    def card(self, *paths):
        for rel in paths:
            self.write(rel.rstrip("/") + "/MODULE.md", "# Module\n")

    def run_check(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = self.cm.main(list(args))
        return code, out.getvalue()

    def valid_setup(self, status="DELIVERED"):
        self.layout()
        self.domains()
        self.modules(
            [
                "order,Order,DOM-001,web/src/features/sales/order/,"
                "server/src/main/java/org/sales/order/,"
                "server/src/main/java/org/sales/order/shared/,"
                f"order-create;order-status,{status},N/A"
            ]
        )
        self.capabilities(
            [
                "order-create,Order Create,DOM-001,order,N/A,ACTIVE,"
                "N/A,N/A,chg-a,N/A",
                "order-status,Order Status,DOM-001,order,N/A,PLANNED,"
                "N/A,N/A,N/A,N/A",
            ]
        )
        self.card(
            "web/src/features/sales/order/",
            "server/src/main/java/org/sales/order/",
        )
        return [
            "web/src/features/sales/order/",
            "server/src/main/java/org/sales/order/",
        ]

    # -- passing --------------------------------------------------------------
    def test_valid_modules_pass(self):
        self.valid_setup()
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertEqual("Modules check passed: 1 module(s), 2 path(s).\n", out)

    def test_multi_root_module_passes(self):
        self.layout()
        self.domains()
        self.modules(
            [
                "report,Report,DOM-001,"
                "web/src/features/reports/report/;web/src/shared/reports/,"
                "server/src/main/java/org/reports/report/,"
                "web/src/features/reports/report/shared/,"
                "N/A,PLANNED,N/A"
            ]
        )
        self.capabilities([])
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertIn("Modules check passed: 1 module(s), 3 path(s).", out)

    def test_planned_module_without_paths_passes_with_warning(self):
        self.layout()
        self.domains()
        self.modules(
            ["billing,Billing,DOM-001,N/A,N/A,N/A,N/A,PLANNED,N/A"]
        )
        self.capabilities([])
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertIn("WARN:", out)
        self.assertIn("no capabilities", out)
        self.assertIn("Modules check passed: 1 module(s), 0 path(s).", out)

    def test_placeholder_row_warns_only(self):
        self.layout()
        self.domains()
        self.modules(
            ["PENDING,PENDING,PENDING,PENDING,PENDING,PENDING,PENDING,PLANNED,N/A"]
        )
        self.capabilities([])
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertIn("WARN:", out)
        self.assertIn("placeholder", out.lower())
        self.assertIn("Modules check passed: 0 module(s), 0 path(s).", out)

    def test_non_owner_may_host_capability(self):
        self.layout()
        self.domains()
        self.modules(
            [
                "order,Order,DOM-001,N/A,N/A,N/A,report-export,PLANNED,N/A",
                "report,Report,DOM-001,N/A,N/A,N/A,report-export,PLANNED,N/A",
            ]
        )
        self.capabilities(
            ["report-export,Report Export,DOM-001,report,N/A,PLANNED,N/A,N/A,N/A,N/A"]
        )
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertIn("Modules check passed: 2 module(s), 0 path(s).", out)

    def test_shared_path_prefix_is_case_insensitive(self):
        self.layout()
        self.domains()
        self.modules(
            [
                "order,Order,DOM-001,N/A,"
                "server/src/main/java/org/sales/order/,"
                "SERVER/src/main/java/org/sales/order/shared/,N/A,DELIVERED,N/A"
            ]
        )
        self.capabilities([])
        self.card("server/src/main/java/org/sales/order/")
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertNotIn("ERROR:", out)
        self.assertIn("Modules check passed: 1 module(s), 1 path(s).", out)

    # -- structural failures -------------------------------------------------
    def test_duplicate_module_slug_fails(self):
        self.layout()
        self.domains()
        self.modules(
            [
                "order,Order A,DOM-001,N/A,N/A,N/A,N/A,PLANNED,N/A",
                "order,Order B,DOM-001,N/A,N/A,N/A,N/A,PLANNED,N/A",
            ]
        )
        self.capabilities([])
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("duplicate module_slug 'order'", out)
        self.assertIn("rows 1, 2", out)
        self.assertIn("first at row 1", out)

    def test_duplicate_paths_fails(self):
        self.layout()
        self.domains()
        self.modules(
            [
                "order-a,Order A,DOM-001,web/src/features/order/,N/A,N/A,N/A,"
                "PLANNED,N/A",
                "order-b,Order B,DOM-001,web/src/features/order/,N/A,N/A,N/A,"
                "PLANNED,N/A",
            ]
        )
        self.capabilities([])
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("duplicate path 'web/src/features/order/'", out)
        self.assertIn("row 1", out)
        self.assertIn("row 2", out)

    def test_duplicate_paths_are_case_insensitive(self):
        self.layout()
        self.domains()
        self.modules(
            [
                "order-a,Order A,DOM-001,web/src/features/Report/,N/A,N/A,N/A,"
                "ACTIVE,N/A",
                "order-b,Order B,DOM-001,web/src/features/report/,N/A,N/A,N/A,"
                "ACTIVE,N/A",
            ]
        )
        self.capabilities([])
        self.card("web/src/features/Report/", "web/src/features/report/")
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("duplicate path", out)

    def test_path_outside_root_fails(self):
        self.layout()
        self.domains()
        self.modules(
            ["order,Order,DOM-001,src/features/order/,N/A,N/A,N/A,PLANNED,N/A"]
        )
        self.capabilities([])
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("src/features/order/", out)
        self.assertIn("code-layout", out)
        self.assertIn("row 1", out)

    def test_path_equals_root_fails(self):
        self.layout()
        self.domains()
        self.modules(
            ["order,Order,DOM-001,web/,N/A,N/A,N/A,PLANNED,N/A"]
        )
        self.capabilities([])
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("web/", out)
        self.assertIn("root", out)

    def test_shared_path_outside_module_fails(self):
        self.layout()
        self.domains()
        self.modules(
            [
                "order,Order,DOM-001,N/A,"
                "server/src/main/java/org/sales/order/,"
                "server/src/main/java/org/sales/common/,N/A,DELIVERED,N/A"
            ]
        )
        self.capabilities([])
        self.card("server/src/main/java/org/sales/order/")
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("shared path", out)
        self.assertIn("server/src/main/java/org/sales/common/", out)

    def test_path_parent_segment_fails(self):
        self.layout()
        self.domains()
        self.modules(
            ["order,Order,DOM-001,web/../outside/,N/A,N/A,N/A,PLANNED,N/A"]
        )
        self.capabilities([])
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("web/../outside/", out)
        self.assertIn("'..'", out)

    def test_shared_path_parent_segment_fails(self):
        self.layout()
        self.domains()
        self.modules(
            [
                "order,Order,DOM-001,N/A,"
                "server/src/main/java/org/sales/order/,"
                "server/src/main/java/org/sales/order/../common/,N/A,DELIVERED,N/A"
            ]
        )
        self.capabilities([])
        self.card("server/src/main/java/org/sales/order/")
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("shared path", out)
        self.assertIn("server/src/main/java/org/sales/order/../common/", out)
        self.assertIn("'..'", out)

    def test_absolute_paths_fail(self):
        for absolute in ("/etc/orders/", "C:/repo/orders/"):
            with self.subTest(absolute=absolute):
                self.layout()
                self.domains()
                self.modules(
                    [
                        f"order,Order,DOM-001,{absolute},N/A,N/A,N/A,"
                        "PLANNED,N/A"
                    ]
                )
                self.capabilities([])
                code, out = self.run_check()
                self.assertEqual(1, code)
                self.assertIn("ERROR:", out)
                self.assertIn("absolute", out)
                self.assertIn(absolute, out)

    def test_wildcard_path_fails(self):
        self.layout()
        self.domains()
        self.modules(
            ["order,Order,DOM-001,web/*,N/A,N/A,N/A,PLANNED,N/A"]
        )
        self.capabilities([])
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("web/*", out)
        self.assertIn("wildcard", out)

    def test_placeholder_path_token_fails(self):
        cases = {
            "frontend": (
                "order,Order,DOM-001,web/src/features/<domain>/order/,"
                "N/A,N/A,N/A,PLANNED,N/A"
            ),
            "backend": (
                "order,Order,DOM-001,N/A,"
                "server/src/main/java/<org>/sales/order/,N/A,N/A,PLANNED,N/A"
            ),
            "shared": (
                "order,Order,DOM-001,N/A,"
                "server/src/main/java/org/sales/order/,"
                "server/src/main/java/org/sales/order/<resource>/,N/A,PLANNED,N/A"
            ),
        }
        for label, row in cases.items():
            with self.subTest(label=label):
                self.layout()
                self.domains()
                self.modules([row])
                self.capabilities([])
                code, out = self.run_check()
                self.assertEqual(1, code)
                self.assertIn("ERROR:", out)
                self.assertIn("placeholder token", out)

    def test_unknown_domain_fails(self):
        self.layout()
        self.domains()
        self.modules(
            ["order,Order,DOM-999,N/A,N/A,N/A,N/A,PLANNED,N/A"]
        )
        self.capabilities([])
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("DOM-999", out)
        self.assertIn("docs/architecture/domain-boundaries.md", out)

    def test_unknown_capability_fails(self):
        self.layout()
        self.domains()
        self.modules(
            ["order,Order,DOM-001,N/A,N/A,N/A,ghost-cap,PLANNED,N/A"]
        )
        self.capabilities(
            ["known,Known,DOM-001,other,N/A,PLANNED,N/A,N/A,N/A,N/A"]
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("ghost-cap", out)
        self.assertIn("docs/product/capabilities.csv", out)

    def test_owner_module_must_list_owned_capability(self):
        self.layout()
        self.domains()
        self.modules(
            ["order,Order,DOM-001,N/A,N/A,N/A,other-cap,PLANNED,N/A"]
        )
        self.capabilities(
            [
                "order-create,Order Create,DOM-001,order,N/A,PLANNED,"
                "N/A,N/A,N/A,N/A",
                "other-cap,Other Cap,DOM-001,other,PLANNED,N/A,N/A,N/A,N/A",
            ]
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("order-create", out)
        self.assertIn("owner", out)

    def test_two_modules_claim_owner_fails(self):
        self.layout()
        self.domains()
        self.modules(
            [
                "order-a,Order A,DOM-001,N/A,N/A,N/A,shared-cap,PLANNED,N/A",
                "order-b,Order B,DOM-001,N/A,N/A,N/A,shared-cap,PLANNED,N/A",
            ]
        )
        self.capabilities(
            [
                "shared-cap,Shared Cap,DOM-001,order-a,N/A,PLANNED,"
                "N/A,N/A,N/A,N/A",
                "shared-cap,Shared Cap,DOM-001,order-b,N/A,PLANNED,"
                "N/A,N/A,N/A,N/A",
            ]
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("shared-cap", out)
        self.assertIn("multiple owner modules", out)
        self.assertIn("order-a", out)
        self.assertIn("order-b", out)

    def test_active_module_requires_path(self):
        self.layout()
        self.domains()
        self.modules(
            ["order,Order,DOM-001,N/A,N/A,N/A,N/A,ACTIVE,N/A"]
        )
        self.capabilities([])
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("at least one frontend_paths or backend_paths", out)

    def test_active_module_requires_module_card(self):
        self.layout()
        self.domains()
        self.modules(
            [
                "order,Order,DOM-001,N/A,"
                "server/src/main/java/org/sales/order/,N/A,N/A,ACTIVE,N/A"
            ]
        )
        self.capabilities([])
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("missing module card", out)
        self.assertIn("MODULE.md", out)

    def test_invalid_status_fails(self):
        self.layout()
        self.domains()
        self.modules(
            ["order,Order,DOM-001,N/A,N/A,N/A,N/A,DRAFT,N/A"]
        )
        self.capabilities([])
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("DRAFT", out)
        self.assertIn("PLANNED|ACTIVE|DELIVERED|DEPRECATED", out)

    def test_missing_module_header_fails(self):
        self.layout()
        self.domains()
        self.modules(
            ["order,Order,DOM-001,N/A,N/A,N/A,N/A,PLANNED"],
            header=MODULE_HEADER.replace(",notes", ""),
        )
        self.capabilities([])
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("missing required header", out)
        self.assertIn("notes", out)

    def test_duplicate_module_header_fails(self):
        self.layout()
        self.domains()
        self.modules(
            ["order,Order,DOM-001,N/A,N/A,N/A,N/A,PLANNED,N/A,N/A"],
            header=MODULE_HEADER.replace("status,", "status,status,"),
        )
        self.capabilities([])
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("duplicate header", out)
        self.assertIn("status", out)

    def test_unexpected_module_header_fails(self):
        self.layout()
        self.domains()
        self.modules(
            ["order,Order,DOM-001,N/A,N/A,N/A,N/A,PLANNED,N/A,owner-marker"],
            header=MODULE_HEADER + ",owner",
        )
        self.capabilities([])
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("unexpected header", out)
        self.assertIn("owner", out)

    def test_missing_domain_file_fails_closed(self):
        self.layout()
        self.modules(
            ["order,Order,DOM-001,N/A,N/A,N/A,N/A,PLANNED,N/A"]
        )
        self.capabilities([])
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("docs/architecture/domain-boundaries.md", out)

    def test_missing_capabilities_file_fails_closed(self):
        self.layout()
        self.domains()
        self.modules(
            ["order,Order,DOM-001,N/A,N/A,N/A,order-create,PLANNED,N/A"]
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("docs/product/capabilities.csv", out)

    def test_missing_modules_file_fails(self):
        self.layout()
        self.domains()
        self.capabilities([])
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("docs/product/modules.csv", out)

    def test_layout_without_roots_fails(self):
        self.layout(omit_roots=True)
        self.domains()
        self.modules(
            ["order,Order,DOM-001,N/A,N/A,N/A,N/A,PLANNED,N/A"]
        )
        self.capabilities([])
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("roots", out)

    # -- strategy switching ---------------------------------------------------
    def test_strategy_none_skips(self):
        self.layout(strategy="none")
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertEqual("MODULES_CHECK=SKIPPED (strategy none)\n", out)

    def test_missing_layout_skips(self):
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertEqual("MODULES_CHECK=SKIPPED (strategy none)\n", out)

    def test_footprint_strategy_skips(self):
        self.layout(strategy="footprint")
        self.write("docs/product/modules.csv", "garbage\n")
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertEqual("MODULES_CHECK=SKIPPED (strategy footprint)\n", out)

    def test_invalid_strategy_fails(self):
        self.layout(strategy="packages")
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("invalid strategy", out)

    # -- --completed writeback ------------------------------------------------
    def test_completed_requires_delivered(self):
        self.valid_setup(status="PLANNED")
        code, out = self.run_check("--completed", "order")
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("DELIVERED", out)

    def test_completed_rejects_owned_active_capability(self):
        self.valid_setup()
        code, out = self.run_check("--completed", "order")
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("order-create", out)
        self.assertIn("active_changes", out)
        self.assertIn("chg-a", out)

    def test_completed_rejects_mixed_active_cell(self):
        self.valid_setup()
        self.capabilities(
            [
                "order-create,Order Create,DOM-001,order,N/A,DELIVERED,"
                "N/A,N/A,N/A;chg-a,N/A",
                "order-status,Order Status,DOM-001,order,N/A,DELIVERED,"
                "N/A,N/A,N/A,N/A",
            ]
        )
        code, out = self.run_check("--completed", "order")
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("order-create", out)
        self.assertIn("active_changes", out)
        self.assertIn("chg-a", out)

    def test_completed_passes_when_delivered_and_clear(self):
        self.valid_setup()
        self.capabilities(
            [
                "order-create,Order Create,DOM-001,order,N/A,DELIVERED,"
                "chg-a,N/A,N/A,N/A",
                "order-status,Order Status,DOM-001,order,N/A,DELIVERED,"
                "chg-b,N/A,N/A,N/A",
            ]
        )
        code, out = self.run_check("--completed", "order")
        self.assertEqual(0, code)
        self.assertNotIn("ERROR:", out)
        self.assertIn("Modules check passed: 1 module(s), 2 path(s).", out)

    def test_completed_unknown_module_fails(self):
        self.valid_setup()
        code, out = self.run_check("--completed", "ghost")
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("not found", out)
        self.assertIn("ghost", out)


if __name__ == "__main__":
    unittest.main()
