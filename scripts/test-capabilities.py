#!/usr/bin/env python3
"""Regression tests for the capability registry checker."""
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

CHECKER = Path(__file__).with_name("check-capabilities.py")

HEADER = (
    "capability_slug,capability_name,domain_id,owner_module,related_modules,"
    "status,delivered_slices,remaining_slices,active_changes,notes"
)

MODULE_HEADER = (
    "module_slug,module_name,domain_id,frontend_paths,backend_paths,shared_paths,"
    "capabilities,status,notes"
)

DOMAINS = """# Domain Boundaries

| DOM ID | Responsibility | Invariants | Dependency Direction |
|---|---|---|---|
| DOM-001 | Orders | none | inbound |
"""


def load(root: Path):
    spec = importlib.util.spec_from_file_location("check_capabilities", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    return module


class CapabilityCheckerTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.cc = load(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    # -- fixtures -------------------------------------------------------------
    def write(self, rel: str, text: str):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    def layout(self, strategy="module-packages", roots=("server/", "web/")):
        self.write(
            "docs/architecture/code-layout.json",
            json.dumps(
                {
                    "version": 1,
                    "strategy": strategy,
                    "roots": {"backend": roots[0], "frontend": roots[1]}
                    if len(roots) == 2
                    else {f"root{index}": root for index, root in enumerate(roots)},
                    "module_card": "MODULE.md",
                }
            ),
        )

    def domains(self, text=DOMAINS):
        self.write("docs/architecture/domain-boundaries.md", text)

    def modules(self, rows):
        self.write(
            "docs/product/modules.csv",
            "\n".join([MODULE_HEADER, *rows]) + "\n",
        )

    def registry(self, rows, header=HEADER):
        self.write(
            "docs/product/capabilities.csv",
            "\n".join([header, *rows]) + "\n",
        )

    def roadmap(self, rows):
        self.write(
            "docs/product/proposal-roadmap.md",
            "## Candidate Changes\n\n"
            "| Change ID | Primary Capability | Extends | Slice Type | Slice Coverage "
            "| Code Target |\n"
            "|---|---|---|---|---|---|\n" + "\n".join(rows) + "\n",
        )

    def run_check(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = self.cc.main(list(args))
        return code, out.getvalue()

    def valid_setup(self):
        self.layout()
        self.domains()
        self.modules(
            [
                "report,Report,DOM-001,N/A,N/A,N/A,report-export,ACTIVE,N/A",
                "billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A",
            ]
        )
        self.registry(
            [
                "report-export,Report Export,DOM-001,report,N/A,ACTIVE,"
                "chg-a,slice-2,N/A,notes",
                "billing,Billing,DOM-001,billing,N/A,DELIVERED,"
                "chg-b;chg-c,N/A,N/A,notes",
            ]
        )
        self.roadmap(
            [
                "| chg-a | report-export | N/A + reason | extend | full | N/A |",
                "| chg-b | billing | N/A + reason | initial | full | N/A |",
                "| chg-c | billing | report-export | extend | full | N/A |",
            ]
        )

    # -- passing --------------------------------------------------------------
    def test_valid_registry_passes(self):
        self.valid_setup()
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertEqual("Capabilities check passed: 2 capability(ies).\n", out)

    def test_placeholder_row_only_warns(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.registry(
            [
                "PENDING,PENDING,PENDING,PENDING,PENDING,PLANNED,"
                "PENDING,PENDING,PENDING,PENDING"
            ]
        )
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertIn("WARN:", out)
        self.assertIn("placeholder", out.lower())
        self.assertIn("Capabilities check passed: 0 capability(ies).", out)

    def test_related_modules_resolve_and_blank_is_optional(self):
        self.layout()
        self.domains()
        self.modules(
            [
                "billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A",
                "report,Report,DOM-001,N/A,N/A,N/A,report-export,ACTIVE,N/A",
            ]
        )
        self.registry(
            [
                "billing,Billing,DOM-001,billing,report,ACTIVE,N/A,slice-2,N/A,N/A",
                "report-export,Report Export,DOM-001,report,N/A,PLANNED,N/A,N/A,N/A,N/A",
            ]
        )
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertIn("Capabilities check passed: 2 capability(ies).", out)

    # -- structural failures -------------------------------------------------
    def test_duplicate_slug_fails(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.registry(
            [
                "billing,Billing,DOM-001,billing,N/A,PLANNED,N/A,N/A,N/A,N/A",
                "billing,Billing,DOM-001,billing,N/A,PLANNED,N/A,N/A,N/A,N/A",
            ]
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("docs/product/capabilities.csv", out)
        self.assertIn("duplicate capability_slug 'billing'", out)

    def test_duplicate_owner_module_fails(self):
        self.layout()
        self.domains()
        self.modules(
            [
                "billing-a,Billing A,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A",
                "billing-b,Billing B,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A",
            ]
        )
        self.registry(
            [
                "billing,Billing,DOM-001,billing-a,N/A,PLANNED,N/A,N/A,N/A,N/A",
                "billing,Billing,DOM-001,billing-b,N/A,PLANNED,N/A,N/A,N/A,N/A",
            ]
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("duplicate capability_slug 'billing'", out)
        self.assertIn("owner module", out)
        self.assertIn("billing-a", out)
        self.assertIn("billing-b", out)

    def test_unknown_domain_fails(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.registry(
            ["billing,Billing,DOM-999,billing,N/A,PLANNED,N/A,N/A,N/A,N/A"]
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("DOM-999", out)
        self.assertIn("docs/architecture/domain-boundaries.md", out)

    def test_invalid_status_fails(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.registry(
            ["billing,Billing,DOM-001,billing,N/A,DONE,N/A,N/A,N/A,N/A"]
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("DONE", out)
        self.assertIn("PLANNED|ACTIVE|DELIVERED|DEPRECATED", out)

    def test_unknown_owner_module_fails(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.registry(
            ["billing,Billing,DOM-001,ghost,N/A,PLANNED,N/A,N/A,N/A,N/A"]
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("owner_module 'ghost'", out)
        self.assertIn("docs/product/modules.csv", out)
        self.assertIn("row 1", out)

    def test_owner_module_must_list_capability(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,other-cap,ACTIVE,N/A"])
        self.registry(
            ["billing,Billing,DOM-001,billing,N/A,PLANNED,N/A,N/A,N/A,N/A"]
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("billing", out)
        self.assertIn("capabilities", out)

    def test_blank_owner_module_fails(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.registry(
            ["billing,Billing,DOM-001,N/A,N/A,PLANNED,N/A,N/A,N/A,N/A"]
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("owner_module", out)
        self.assertIn("blank", out)

    def test_unknown_related_module_fails(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.registry(
            ["billing,Billing,DOM-001,billing,ghost,PLANNED,N/A,N/A,N/A,N/A"]
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("related module 'ghost'", out)
        self.assertIn("docs/product/modules.csv", out)

    def test_missing_required_header_fails(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.registry(
            ["billing,Billing,DOM-001,billing,PLANNED"],
            header="capability_slug,capability_name,domain_id,owner_module,status",
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("docs/product/capabilities.csv", out)
        self.assertIn("missing required header", out)
        self.assertIn("notes", out)

    def test_unexpected_header_fails(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.registry(
            [
                "billing,Billing,DOM-001,billing,N/A,PLANNED,N/A,N/A,N/A,N/A,"
                "server/billing/"
            ],
            header=HEADER + ",code_packages",
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("unexpected header", out)
        self.assertIn("code_packages", out)

    def test_duplicate_header_fails(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.registry(
            ["billing,Billing,DOM-001,billing,N/A,PLANNED,N/A,N/A,N/A,N/A,N/A"],
            header=HEADER.replace("status,", "status,status,"),
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("duplicate header", out)
        self.assertIn("status", out)

    def test_missing_registry_fails(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("docs/product/capabilities.csv", out)

    def test_missing_modules_fails(self):
        self.layout()
        self.domains()
        self.registry(
            ["billing,Billing,DOM-001,billing,N/A,PLANNED,N/A,N/A,N/A,N/A"]
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("docs/product/modules.csv", out)

    def test_missing_domain_file_fails(self):
        self.layout()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.registry(
            ["billing,Billing,DOM-001,billing,N/A,PLANNED,N/A,N/A,N/A,N/A"]
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("docs/architecture/domain-boundaries.md", out)

    def test_code_paths_and_module_cards_are_not_checked(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.registry(
            ["billing,Billing,DOM-001,billing,N/A,ACTIVE,N/A,slice-2,N/A,N/A"]
        )
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertNotIn("MODULE.md", out)
        self.assertIn("Capabilities check passed: 1 capability(ies).", out)

    # -- partial remaining slices --------------------------------------------
    def test_partial_active_requires_remaining(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.roadmap(
            ["| chg-a | billing | N/A + reason | extend | partial | N/A |"]
        )
        self.registry(
            ["billing,Billing,DOM-001,billing,N/A,ACTIVE,N/A,,chg-a,N/A"]
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("billing", out)
        self.assertIn("chg-a", out)
        self.assertIn("remaining_slices", out)
        self.assertIn("partial", out)

    def test_partial_active_blank_variants_require_remaining(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.roadmap(
            ["| chg-a | billing | N/A + reason | extend | partial | N/A |"]
        )
        for blank in ("", "N/A", "PENDING"):
            with self.subTest(blank=blank):
                self.registry(
                    [
                        f"billing,Billing,DOM-001,billing,N/A,ACTIVE,N/A,{blank},"
                        "chg-a,N/A"
                    ]
                )
                code, out = self.run_check()
                self.assertEqual(1, code)
                self.assertIn("ERROR:", out)
                self.assertIn("remaining_slices", out)

    def test_partial_active_with_remaining_passes(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.roadmap(
            ["| chg-a | billing | N/A + reason | extend | partial | N/A |"]
        )
        self.registry(
            [
                "billing,Billing,DOM-001,billing,N/A,ACTIVE,N/A,"
                "slice-2;slice-3,chg-a,N/A"
            ]
        )
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertIn("Capabilities check passed: 1 capability(ies).", out)

    def test_delivered_partial_passes(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.roadmap(
            ["| chg-a | billing | N/A + reason | extend | partial | N/A |"]
        )
        self.registry(
            ["billing,Billing,DOM-001,billing,N/A,DELIVERED,chg-a,,N/A,N/A"]
        )
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertNotIn("ERROR:", out)
        self.assertIn("Capabilities check passed: 1 capability(ies).", out)

    def test_active_full_coverage_blank_remaining_warns(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.roadmap(
            ["| chg-a | billing | N/A + reason | extend | full | N/A |"]
        )
        self.registry(
            ["billing,Billing,DOM-001,billing,N/A,ACTIVE,N/A,,chg-a,N/A"]
        )
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertIn("WARN:", out)
        self.assertIn("ACTIVE", out)
        self.assertIn("Capabilities check passed: 1 capability(ies).", out)

    def test_active_without_active_changes_blank_remaining_warns(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.registry(
            ["billing,Billing,DOM-001,billing,N/A,ACTIVE,N/A,,N/A,N/A"]
        )
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertIn("WARN:", out)
        self.assertIn("ACTIVE", out)
        self.assertNotIn("ERROR:", out)

    def test_roadmap_missing_warns_not_fails(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.registry(
            ["billing,Billing,DOM-001,billing,N/A,ACTIVE,N/A,,chg-a,N/A"]
        )
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertIn("ROADMAP_UNAVAILABLE", out)
        self.assertIn("Capabilities check passed: 1 capability(ies).", out)

    def test_roadmap_without_table_rows_warns(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.write("docs/product/proposal-roadmap.md", "# Roadmap\n\nNo tables here.\n")
        self.registry(
            ["billing,Billing,DOM-001,billing,N/A,ACTIVE,N/A,,chg-a,N/A"]
        )
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertIn("ROADMAP_UNAVAILABLE", out)

    # -- strategy switching ---------------------------------------------------
    def test_strategy_none_skips(self):
        self.layout(strategy="none")
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertEqual("CAPABILITIES_CHECK=SKIPPED (strategy none)\n", out)

    def test_missing_layout_skips(self):
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertEqual("CAPABILITIES_CHECK=SKIPPED (strategy none)\n", out)

    def test_footprint_strategy_skips(self):
        self.layout(strategy="footprint")
        self.write("docs/product/capabilities.csv", "garbage\n")
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertEqual("CAPABILITIES_CHECK=SKIPPED (strategy footprint)\n", out)

    # -- --completed writeback ------------------------------------------------
    def test_completed_writeback(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.registry(
            ["billing,Billing,DOM-001,billing,N/A,ACTIVE,N/A,slice-2,chg-a,N/A"]
        )

        code, out = self.run_check("--completed", "chg-a")
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("chg-a", out)
        self.assertIn("delivered_slices", out)
        self.assertIn("active_changes", out)

        self.registry(
            ["billing,Billing,DOM-001,billing,N/A,DELIVERED,chg-a,N/A,N/A,N/A"]
        )
        code, out = self.run_check("--completed", "chg-a")
        self.assertEqual(0, code)
        self.assertIn("Capabilities check passed: 1 capability(ies).", out)

    def test_completed_absence_fails(self):
        self.layout()
        self.domains()
        self.modules(["billing,Billing,DOM-001,N/A,N/A,N/A,billing,ACTIVE,N/A"])
        self.registry(
            ["billing,Billing,DOM-001,billing,N/A,DELIVERED,chg-b,N/A,N/A,N/A"]
        )
        code, out = self.run_check("--completed", "chg-a")
        self.assertEqual(1, code)
        self.assertIn("not found in delivered_slices", out)


if __name__ == "__main__":
    unittest.main()
