#!/usr/bin/env python3
"""Regression tests for the proposal roadmap checker."""
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

CHECKER = Path(__file__).with_name("check-roadmap.py")

CAPABILITY_HEADER = (
    "capability_slug,capability_name,domain_id,owner_module,related_modules,"
    "status,delivered_slices,remaining_slices,active_changes,notes"
)

MODULE_HEADER = (
    "module_slug,module_name,domain_id,frontend_paths,backend_paths,shared_paths,"
    "capabilities,status,notes"
)

MAIN_HEADER = (
    "| Change ID | Primary Capability | Owner Module | Related Modules | "
    "Slice Type | Slice Coverage | Code Target | Demo Path | Slice Budget |"
)

AMENDMENT_HEADER = (
    "| Change ID | Primary Capability | Owner Module | Related Modules | "
    "Slice Type | Slice Coverage | Code Target | Reason | Requester | Approver "
    "| Date | Baseline Impact |"
)

LEGACY_HEADER = (
    "| Change ID | Extends | Slice Type | Slice Coverage | Code Target |"
)

LEGACY_HEADING = "## 1. 路线图总表"


def load(root: Path):
    spec = importlib.util.spec_from_file_location("check_roadmap", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    return module


def table(header: str, rows) -> str:
    columns = len([cell for cell in header.strip("|").split("|")])
    separator = "|" + "---|" * columns
    return "\n".join([header, separator, *rows]) + "\n"


class RoadmapCheckerTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.cr = load(self.root)

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
                    "roots": {"backend": roots[0], "frontend": roots[1]},
                    "module_card": "MODULE.md",
                }
            ),
        )

    def modules(self, rows):
        self.write(
            "docs/product/modules.csv",
            "\n".join([MODULE_HEADER, *rows]) + "\n",
        )

    def capabilities(self, rows):
        self.write(
            "docs/product/capabilities.csv",
            "\n".join([CAPABILITY_HEADER, *rows]) + "\n",
        )

    def roadmap(self, main_rows, amendment_rows=None, main_header=MAIN_HEADER):
        text = f"# Proposal Roadmap\n\n## Candidate Changes\n\n{table(main_header, main_rows)}"
        if amendment_rows is not None:
            text += (
                "\n## Roadmap Amendments\n\n"
                + table(AMENDMENT_HEADER, amendment_rows)
            )
        self.write("docs/product/proposal-roadmap.md", text)

    def legacy_roadmap(self, rows, heading=LEGACY_HEADING, header=LEGACY_HEADER):
        self.write(
            "docs/product/proposal-roadmap.md",
            f"# Roadmap\n\n{heading}\n\n{table(header, rows)}",
        )

    def change(self, change_id: str):
        self.write(f"openspec/changes/{change_id}/proposal.md", "# Proposal\n")

    def run_check(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = self.cr.main(list(args))
        return code, out.getvalue()

    def registries(self, active_change="chg-a"):
        self.modules(
            [
                "order,Order,DOM-001,web/src/features/sales/order/,"
                "server/src/main/java/org/sales/order/,"
                "server/src/main/java/org/sales/order/shared/,"
                "order-create;order-status,PLANNED,N/A",
                "audit,Audit,DOM-001,web/src/features/audit/,"
                "server/src/main/java/org/audit/,N/A,order-create,PLANNED,N/A",
            ]
        )
        self.capabilities(
            [
                "order-create,Order Create,DOM-001,order,N/A,ACTIVE,N/A,"
                f"slice-2,{active_change},N/A",
                "order-status,Order Status,DOM-001,order,N/A,PLANNED,N/A,"
                "N/A,N/A,N/A",
            ]
        )

    def valid_setup(self):
        self.layout()
        self.registries()
        self.roadmap(
            [
                "| chg-a | order-create | order | N/A + reason | extend | partial "
                "| server/src/main/java/org/sales/order/resource/ | demo | 6 AC |",
                "| chg-b | order-status | order | audit | initial | full "
                "| web/src/features/sales/order/;server/src/main/java/org/audit/ "
                "| demo | 4 AC |",
            ],
            amendment_rows=[
                "| chg-late | order-create | order | audit | extend | full "
                "| server/src/main/java/org/sales/order/resource/ | late request "
                "| Alice | Tech Lead | 2026-11-23 | CHANGE_ONLY |"
            ],
        )
        for change_id in ("chg-a", "chg-b", "chg-late"):
            self.change(change_id)

    # -- legacy strategy ------------------------------------------------------
    def test_legacy_roadmap_passes(self):
        self.legacy_roadmap(
            [
                "| chg-a | N/A + reason | initial | full | server/sales/ |",
                "| chg-b | chg-a | extend | partial | web/sales/ |",
            ]
        )
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertEqual("Roadmap structure check passed: 2 named Change(s).\n", out)

    def test_legacy_until_next_heading_rows(self):
        self.legacy_roadmap(
            ["| chg-a | N/A + reason | N/A | N/A | N/A |"],
            heading="## 1. Roadmap Overview",
        )
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertEqual("Roadmap structure check passed: 1 named Change(s).\n", out)

    def test_legacy_placeholder_and_strict(self):
        self.legacy_roadmap(["| chg-a | TODO | N/A | N/A | N/A |"])
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertIn("WARN:", out)
        self.assertIn("placeholder", out)
        code, out = self.run_check("--strict")
        self.assertEqual(1, code)
        self.assertIn("Roadmap check failed: 0 error(s), 1 warning(s).", out)

    def test_strategy_none_ignores_new_columns(self):
        self.layout(strategy="none")
        self.legacy_roadmap(
            ["| chg-a | N/A + reason | initial | full | server/sales/ |"]
        )
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertIn("Roadmap structure check passed: 1 named Change(s).", out)

    def test_legacy_invalid_and_duplicate_ids_fail(self):
        self.legacy_roadmap(
            [
                "| Chg_A | N/A | N/A | N/A | N/A |",
                "| chg-b | N/A | N/A | N/A | N/A |",
                "| chg-b | N/A | N/A | N/A | N/A |",
            ]
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("invalid change-id 'Chg_A'", out)
        self.assertIn("duplicate change-id 'chg-b'", out)
        self.assertIn("Roadmap check failed: 2 error(s), 0 warning(s).", out)

    # -- module-packages structure -------------------------------------------
    def test_new_columns_required(self):
        self.layout()
        self.registries()
        self.roadmap(
            [
                "| chg-a | N/A | initial | full | server/sales/ | demo |",
            ],
            main_header=(
                "| Change ID | Extends | Slice Type | Slice Coverage | Code Target "
                "| Demo Path |"
            ),
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("missing required column", out)
        for column in ("Primary Capability", "Owner Module", "Related Modules", "Slice Budget"):
            self.assertIn(column, out)

    def test_valid_module_packages_roadmap_passes(self):
        self.valid_setup()
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertEqual(
            "Roadmap check passed: 2 Change(s), 1 amendment(s).\n", out
        )

    def test_placeholder_row_warns_and_strict_fails(self):
        self.layout()
        self.registries(active_change="N/A")
        self.roadmap(
            ["| PENDING | PENDING | PENDING | PENDING | PENDING | PENDING "
             "| PENDING | PENDING | PENDING |"]
        )
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertIn("WARN:", out)
        self.assertIn("placeholder", out)
        code, out = self.run_check("--strict")
        self.assertEqual(1, code)

    def test_demo_and_budget_blank_warn(self):
        self.layout()
        self.registries()
        self.roadmap(
            [
                "| chg-a | order-create | order | N/A + reason | extend | full "
                "| server/src/main/java/org/sales/order/resource/ |  |  |",
            ]
        )
        self.change("chg-a")
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertIn("WARN:", out)
        self.assertIn("placeholder remains", out)

    def test_pending_placeholder_cells_warn_and_strict_fails(self):
        self.layout()
        self.registries()
        self.roadmap(
            [
                "| chg-a | order-create | order | N/A + reason | extend | full "
                "| server/src/main/java/org/sales/order/ | PENDING | PENDING |",
            ]
        )
        self.change("chg-a")
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertIn("WARN:", out)
        self.assertIn("placeholder remains in roadmap row 'chg-a'", out)
        code, out = self.run_check("--strict")
        self.assertEqual(1, code)
        self.assertIn("Roadmap check failed: 0 error(s), 1 warning(s).", out)

    # -- capability / owner / related / code target --------------------------
    def test_unknown_primary_capability_fails(self):
        self.layout()
        self.registries()
        self.roadmap(
            [
                "| chg-a | ghost-cap | ghost | N/A + reason | initial | full "
                "| server/src/main/java/org/sales/order/ | demo | 4 AC |",
            ]
        )
        self.change("chg-a")
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("ghost-cap", out)
        self.assertIn("docs/product/capabilities.csv", out)

    def test_owner_module_must_match_capability(self):
        self.layout()
        self.registries()
        self.roadmap(
            [
                "| chg-a | order-create | audit | N/A + reason | extend | full "
                "| server/src/main/java/org/audit/ | demo | 4 AC |",
            ]
        )
        self.change("chg-a")
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("Owner Module", out)
        self.assertIn("order-create", out)
        self.assertIn("audit", out)
        self.assertIn("order", out)

    def test_related_module_unknown_fails(self):
        self.layout()
        self.registries()
        self.roadmap(
            [
                "| chg-a | order-create | order | ghost | extend | full "
                "| server/src/main/java/org/sales/order/ | demo | 4 AC |",
            ]
        )
        self.change("chg-a")
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("related module 'ghost'", out)
        self.assertIn("docs/product/modules.csv", out)

    def test_code_target_outside_modules_fails(self):
        self.layout()
        self.registries()
        self.roadmap(
            [
                "| chg-a | order-create | order | N/A + reason | extend | full "
                "| server/src/main/java/org/billing/Billing.java | demo | 4 AC |",
            ]
        )
        self.change("chg-a")
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("server/src/main/java/org/billing/Billing.java", out)
        self.assertIn("owner/related module paths", out)

    def test_code_target_resource_level_passes(self):
        self.layout()
        self.registries()
        self.roadmap(
            [
                "| chg-a | order-create | order | N/A + reason | extend | full "
                "| server/src/main/java/org/sales/order/billing/BillingResource.java "
                "| demo | 4 AC |",
            ]
        )
        self.change("chg-a")
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertNotIn("ERROR:", out)

    def test_code_target_blocks_path_traversal(self):
        self.layout()
        self.registries()
        self.roadmap(
            [
                "| chg-a | order-create | order | N/A + reason | extend | full "
                "| server/src/main/java/org/sales/order/../../billing/ | demo | 4 AC |",
            ]
        )
        self.change("chg-a")
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("'..'", out)

    # -- slice type / coverage / remaining -----------------------------------
    def test_slice_type_and_coverage_enums(self):
        self.layout()
        self.registries()
        self.roadmap(
            [
                "| chg-a | order-create | order | N/A + reason | append | some "
                "| server/src/main/java/org/sales/order/ | demo | 4 AC |",
            ]
        )
        self.change("chg-a")
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("invalid Slice Type 'append'; expected initial|extend", out)
        self.assertIn(
            "invalid Slice Coverage 'some'; expected partial|full", out
        )

    def test_partial_requires_remaining(self):
        for blank in ("", "N/A", "PENDING"):
            with self.subTest(blank=blank):
                self.layout()
                self.modules(
                    [
                        "order,Order,DOM-001,web/src/features/sales/order/,"
                        "server/src/main/java/org/sales/order/,N/A,order-create,"
                        "PLANNED,N/A",
                    ]
                )
                self.capabilities(
                    [
                        "order-create,Order Create,DOM-001,order,N/A,ACTIVE,N/A,"
                        f"{blank},chg-a,N/A",
                    ]
                )
                self.roadmap(
                    [
                        "| chg-a | order-create | order | N/A + reason | extend "
                        "| partial | server/src/main/java/org/sales/order/ | demo | 4 AC |",
                    ]
                )
                self.change("chg-a")
                code, out = self.run_check()
                self.assertEqual(1, code)
                self.assertIn("ERROR:", out)
                self.assertIn("remaining_slices", out)
                self.assertIn("partial", out)

    def test_full_coverage_allows_blank_remaining(self):
        self.layout()
        self.modules(
            [
                "order,Order,DOM-001,web/src/features/sales/order/,"
                "server/src/main/java/org/sales/order/,N/A,order-create,PLANNED,N/A",
            ]
        )
        self.capabilities(
            [
                "order-create,Order Create,DOM-001,order,N/A,ACTIVE,N/A,"
                ",chg-a,N/A",
            ]
        )
        self.roadmap(
            [
                "| chg-a | order-create | order | N/A + reason | extend | full "
                "| server/src/main/java/org/sales/order/ | demo | 4 AC |",
            ]
        )
        self.change("chg-a")
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertNotIn("ERROR:", out)

    def test_extend_requires_active_or_delivered(self):
        for status, expects_error in (("PLANNED", True), ("ACTIVE", False), ("DELIVERED", False)):
            with self.subTest(status=status):
                self.layout()
                self.modules(
                    [
                        "order,Order,DOM-001,web/src/features/sales/order/,"
                        "server/src/main/java/org/sales/order/,N/A,order-create,"
                        "PLANNED,N/A",
                    ]
                )
                self.capabilities(
                    [
                        "order-create,Order Create,DOM-001,order,N/A,"
                        f"{status},N/A,slice-2,N/A,N/A",
                    ]
                )
                self.roadmap(
                    [
                        "| chg-a | order-create | order | N/A + reason | extend | full "
                        "| server/src/main/java/org/sales/order/ | demo | 4 AC |",
                    ]
                )
                self.change("chg-a")
                code, out = self.run_check()
                if expects_error:
                    self.assertEqual(1, code)
                    self.assertIn("ERROR:", out)
                    self.assertIn("ACTIVE|DELIVERED", out)
                    self.assertIn("PLANNED", out)
                else:
                    self.assertEqual(0, code)
                    self.assertNotIn("ERROR:", out)

    def test_initial_accepts_planned_capability(self):
        self.layout()
        self.modules(
            [
                "order,Order,DOM-001,web/src/features/sales/order/,"
                "server/src/main/java/org/sales/order/,N/A,order-create,PLANNED,N/A",
            ]
        )
        self.capabilities(
            [
                "order-create,Order Create,DOM-001,order,N/A,PLANNED,N/A,N/A,"
                "N/A,N/A",
            ]
        )
        self.roadmap(
            [
                "| chg-a | order-create | order | N/A + reason | initial | full "
                "| server/src/main/java/org/sales/order/ | demo | 4 AC |",
            ]
        )
        self.change("chg-a")
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertNotIn("ERROR:", out)

    # -- amendments -----------------------------------------------------------
    def test_amendment_requires_approval_fields(self):
        for field, row in {
            "Reason": "| chg-late | order-create | order | N/A + reason | extend | full "
            "| server/src/main/java/org/sales/order/ |  | Alice | Tech Lead "
            "| 2026-11-23 | CHANGE_ONLY |",
            "Requester": "| chg-late | order-create | order | N/A + reason | extend "
            "| full | server/src/main/java/org/sales/order/ | late |  | Tech Lead "
            "| 2026-11-23 | CHANGE_ONLY |",
            "Approver": "| chg-late | order-create | order | N/A + reason | extend "
            "| full | server/src/main/java/org/sales/order/ | late | Alice |  "
            "| 2026-11-23 | CHANGE_ONLY |",
            "Date": "| chg-late | order-create | order | N/A + reason | extend | full "
            "| server/src/main/java/org/sales/order/ | late | Alice | Tech Lead "
            "|  | CHANGE_ONLY |",
            "Baseline Impact": "| chg-late | order-create | order | N/A + reason "
            "| extend | full | server/src/main/java/org/sales/order/ | late | Alice "
            "| Tech Lead | 2026-11-23 |  |",
        }.items():
            with self.subTest(field=field):
                self.layout()
                self.registries()
                self.roadmap([], amendment_rows=[row])
                code, out = self.run_check()
                self.assertEqual(1, code)
                self.assertIn("ERROR:", out)
                self.assertIn("amendment", out.lower())
                self.assertIn(field, out)

    def test_amendment_requires_approver(self):
        self.layout()
        self.registries(active_change="N/A")
        self.roadmap(
            [],
            amendment_rows=[
                "| chg-late | order-create | order | N/A + reason | extend | full "
                "| server/src/main/java/org/sales/order/ | late | Alice |  "
                "| 2026-11-23 | CHANGE_ONLY |",
            ],
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("blank Approver", out)

    def test_amendment_validates_owner_and_code_target(self):
        self.layout()
        self.registries()
        self.roadmap(
            [],
            amendment_rows=[
                "| chg-late | order-create | audit | ghost | append | always "
                "| server/src/main/java/org/billing/Billing.java | late | Alice "
                "| Tech Lead | 2026-11-23 | BASELINE_UPDATE |",
            ],
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("Owner Module", out)
        self.assertIn("ghost", out)
        self.assertIn("invalid Slice Type 'append'", out)
        self.assertIn("invalid Slice Coverage 'always'", out)
        self.assertIn("org/billing/Billing.java", out)
        self.assertIn("invalid Baseline Impact 'BASELINE_UPDATE'", out)

    def test_amendment_baseline_impact_enum(self):
        self.layout()
        self.registries(active_change="chg-late")
        self.roadmap(
            [],
            amendment_rows=[
                "| chg-late | order-create | order | N/A + reason | extend | full "
                "| server/src/main/java/org/sales/order/ | late | Alice | Tech Lead "
                "| 2026-11-23 | CHANGE_ONLY |",
            ],
        )
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertNotIn("ERROR:", out)

    def test_amendment_pending_approval_fields_block_approval(self):
        rows = {
            "Reason": "| chg-late | order-create | order | N/A + reason | extend "
            "| full | server/src/main/java/org/sales/order/ | PENDING | Alice "
            "| Tech Lead | 2026-11-23 | CHANGE_ONLY |",
            "Requester": "| chg-late | order-create | order | N/A + reason | extend "
            "| full | server/src/main/java/org/sales/order/ | late | PENDING "
            "| Tech Lead | 2026-11-23 | CHANGE_ONLY |",
            "Approver": "| chg-late | order-create | order | N/A + reason | extend "
            "| full | server/src/main/java/org/sales/order/ | late | Alice "
            "| PENDING | 2026-11-23 | CHANGE_ONLY |",
            "Date": "| chg-late | order-create | order | N/A + reason | extend "
            "| full | server/src/main/java/org/sales/order/ | late | Alice "
            "| Tech Lead | PENDING | CHANGE_ONLY |",
            "Baseline Impact": "| chg-late | order-create | order | N/A + reason "
            "| extend | full | server/src/main/java/org/sales/order/ | late | Alice "
            "| Tech Lead | 2026-11-23 | PENDING |",
        }
        for field, row in rows.items():
            with self.subTest(field=field):
                self.layout()
                self.registries(active_change="chg-late")
                self.roadmap([], amendment_rows=[row])
                code, out = self.run_check()
                self.assertEqual(1, code)
                self.assertIn("ERROR:", out)
                self.assertIn(f"placeholder {field}", out)
                self.assertIn("not registered", out)

    def test_amendment_extend_planned_capability_fails(self):
        self.layout()
        self.modules(
            [
                "order,Order,DOM-001,web/src/features/sales/order/,"
                "server/src/main/java/org/sales/order/,N/A,order-create,PLANNED,N/A",
            ]
        )
        self.capabilities(
            [
                "order-create,Order Create,DOM-001,order,N/A,PLANNED,N/A,N/A,"
                "N/A,N/A",
            ]
        )
        self.roadmap(
            [],
            amendment_rows=[
                "| chg-late | order-create | order | N/A + reason | extend | full "
                "| server/src/main/java/org/sales/order/ | late | Alice | Tech Lead "
                "| 2026-11-23 | CHANGE_ONLY |",
            ],
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("ACTIVE|DELIVERED", out)
        self.assertIn("PLANNED", out)

    def test_amendment_partial_blank_remaining_fails(self):
        self.layout()
        self.modules(
            [
                "order,Order,DOM-001,web/src/features/sales/order/,"
                "server/src/main/java/org/sales/order/,N/A,order-create,PLANNED,N/A",
            ]
        )
        self.capabilities(
            [
                "order-create,Order Create,DOM-001,order,N/A,ACTIVE,N/A,"
                ",N/A,N/A",
            ]
        )
        self.roadmap(
            [],
            amendment_rows=[
                "| chg-late | order-create | order | N/A + reason | extend | partial "
                "| server/src/main/java/org/sales/order/ | late | Alice | Tech Lead "
                "| 2026-11-23 | CHANGE_ONLY |",
            ],
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("remaining_slices", out)
        self.assertIn("partial", out)

    def test_amendment_extend_and_partial_valid_passes(self):
        self.layout()
        self.modules(
            [
                "order,Order,DOM-001,web/src/features/sales/order/,"
                "server/src/main/java/org/sales/order/,N/A,order-create,PLANNED,N/A",
            ]
        )
        self.capabilities(
            [
                "order-create,Order Create,DOM-001,order,N/A,ACTIVE,N/A,"
                "slice-2,N/A,N/A",
            ]
        )
        self.roadmap(
            [],
            amendment_rows=[
                "| chg-late | order-create | order | N/A + reason | extend | partial "
                "| server/src/main/java/org/sales/order/ | late | Alice | Tech Lead "
                "| 2026-11-23 | CHANGE_ONLY |",
            ],
        )
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertNotIn("ERROR:", out)

    def test_duplicate_main_and_amendment_fails(self):
        self.layout()
        self.registries()
        self.roadmap(
            [
                "| chg-a | order-create | order | N/A + reason | extend | full "
                "| server/src/main/java/org/sales/order/ | demo | 4 AC |",
            ],
            amendment_rows=[
                "| chg-a | order-create | order | N/A + reason | extend | full "
                "| server/src/main/java/org/sales/order/ | late | Alice | Tech Lead "
                "| 2026-11-23 | CHANGE_ONLY |",
            ],
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("appears in both", out)
        self.assertIn("chg-a", out)

    def test_duplicate_and_invalid_ids_fail(self):
        self.layout()
        self.registries()
        self.roadmap(
            [
                "| Chg_A | order-create | order | N/A + reason | extend | full "
                "| server/src/main/java/org/sales/order/ | demo | 4 AC |",
                "| chg-b | order-create | order | N/A + reason | extend | full "
                "| server/src/main/java/org/sales/order/ | demo | 4 AC |",
                "| chg-b | order-create | order | N/A + reason | extend | full "
                "| server/src/main/java/org/sales/order/ | demo | 4 AC |",
            ]
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("invalid change-id 'Chg_A'", out)
        self.assertIn("duplicate change-id 'chg-b'", out)

    # -- active Change registration ------------------------------------------
    def test_active_change_registered(self):
        self.valid_setup()
        code, out = self.run_check()
        self.assertEqual(0, code)

    def test_active_change_dir_unregistered_fails(self):
        self.layout()
        self.registries()
        self.roadmap([])
        self.change("chg-ghost")
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("openspec/changes/chg-ghost", out)
        self.assertIn("not registered", out)

    def test_active_change_dir_registered_by_amendment_passes(self):
        self.layout()
        self.registries(active_change="chg-late")
        self.roadmap(
            [],
            amendment_rows=[
                "| chg-late | order-create | order | N/A + reason | extend | full "
                "| server/src/main/java/org/sales/order/ | late | Alice | Tech Lead "
                "| 2026-11-23 | CHANGE_ONLY |",
            ],
        )
        self.change("chg-late")
        code, out = self.run_check()
        self.assertEqual(0, code)

    def test_missing_openspec_dir_is_not_an_error(self):
        self.layout()
        self.registries(active_change="N/A")
        self.roadmap([])
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertNotIn("ERROR:", out)

    def test_active_changes_absent_from_roadmap_errors(self):
        self.layout()
        self.modules(
            [
                "order,Order,DOM-001,web/src/features/sales/order/,"
                "server/src/main/java/org/sales/order/,N/A,order-create,PLANNED,N/A",
            ]
        )
        self.capabilities(
            [
                "order-create,Order Create,DOM-001,order,N/A,ACTIVE,N/A,"
                "slice-2,chg-typo,N/A",
            ]
        )
        self.roadmap(
            [
                "| chg-a | order-create | order | N/A + reason | extend | partial "
                "| server/src/main/java/org/sales/order/ | demo | 4 AC |",
            ]
        )
        self.change("chg-a")
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("chg-typo", out)
        self.assertIn("docs/product/capabilities.csv", out)
        self.assertIn("not registered", out)

    # -- footprint strategy ---------------------------------------------------
    def test_footprint_requires_code_target(self):
        self.layout(strategy="footprint")
        self.write(
            "docs/product/proposal-roadmap.md",
            "# Roadmap\n\n## Candidate Changes\n\n"
            + table("| Change ID | Code Target |", ["| chg-a | server/sales/ |"]),
        )
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertIn("Roadmap footprint check passed: 1 Change(s).", out)

        self.write(
            "docs/product/proposal-roadmap.md",
            "# Roadmap\n\n## Candidate Changes\n\n"
            + table("| Change ID | Demo Path |", ["| chg-a | demo |"]),
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("missing required column", out)
        self.assertIn("Code Target", out)

    def test_footprint_code_target_outside_root_fails(self):
        self.layout(strategy="footprint")
        self.write(
            "docs/product/proposal-roadmap.md",
            "# Roadmap\n\n## Candidate Changes\n\n"
            + table("| Change ID | Code Target |", ["| chg-a | src/sales/App.java |"]),
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("src/sales/App.java", out)
        self.assertIn("code-layout", out)

    def test_footprint_n_a_optional_cells_pass_strict(self):
        self.layout(strategy="footprint")
        self.write(
            "docs/product/proposal-roadmap.md",
            "# Roadmap\n\n## Candidate Changes\n\n"
            + table(
                "| Change ID | Code Target | Related Modules | Dependencies |",
                ["| chg-a | server/sales/ | N/A + reason | N/A |"],
            ),
        )
        code, out = self.run_check("--strict")
        self.assertEqual(0, code)
        self.assertNotIn("WARN:", out)
        self.assertIn("Roadmap footprint check passed: 1 Change(s).", out)

    def test_footprint_amendment_absolute_path_fails(self):
        self.layout(strategy="footprint")
        self.roadmap(
            [],
            amendment_rows=[
                "| chg-late | order-create | order | N/A + reason | extend | full "
                "| C:/Windows/evil | late | Alice | Tech Lead | 2026-11-23 "
                "| CHANGE_ONLY |",
            ],
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("C:/Windows/evil", out)
        self.assertIn("absolute", out)

    def test_footprint_amendment_traversal_fails(self):
        self.layout(strategy="footprint")
        self.roadmap(
            [],
            amendment_rows=[
                "| chg-late | order-create | order | N/A + reason | extend | full "
                "| ../../etc | late | Alice | Tech Lead | 2026-11-23 | CHANGE_ONLY |",
            ],
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("../../etc", out)
        self.assertIn("'..'", out)

    def test_footprint_amendment_valid_code_target_passes(self):
        self.layout(strategy="footprint")
        self.roadmap(
            [],
            amendment_rows=[
                "| chg-late | order-create | order | N/A + reason | extend | full "
                "| server/sales/ | late | Alice | Tech Lead | 2026-11-23 "
                "| CHANGE_ONLY |",
            ],
        )
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertNotIn("ERROR:", out)

    def test_footprint_amendment_outside_root_fails(self):
        self.layout(strategy="footprint")
        self.roadmap(
            [],
            amendment_rows=[
                "| chg-late | order-create | order | N/A + reason | extend | full "
                "| src/sales/App.java | late | Alice | Tech Lead | 2026-11-23 "
                "| CHANGE_ONLY |",
            ],
        )
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("src/sales/App.java", out)
        self.assertIn("code-layout", out)

    def test_footprint_does_not_require_registries(self):
        self.layout(strategy="footprint")
        self.write(
            "docs/product/proposal-roadmap.md",
            "# Roadmap\n\n## Candidate Changes\n\n"
            + table("| Change ID | Code Target |", ["| chg-a | server/sales/ |"]),
        )
        code, out = self.run_check()
        self.assertEqual(0, code)
        self.assertNotIn("docs/product/modules.csv", out)
        self.assertNotIn("docs/product/capabilities.csv", out)

    # -- missing inputs / errors ---------------------------------------------
    def test_missing_capability_registry_fails(self):
        self.layout()
        self.modules(
            [
                "order,Order,DOM-001,web/src/features/sales/order/,"
                "server/src/main/java/org/sales/order/,N/A,order-create,PLANNED,N/A",
            ]
        )
        self.roadmap(
            [
                "| chg-a | order-create | order | N/A + reason | extend | full "
                "| server/src/main/java/org/sales/order/ | demo | 4 AC |",
            ]
        )
        self.change("chg-a")
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("docs/product/capabilities.csv", out)

    def test_missing_modules_registry_fails(self):
        self.layout()
        self.capabilities(
            [
                "order-create,Order Create,DOM-001,order,N/A,ACTIVE,N/A,"
                "slice-2,N/A,N/A",
            ]
        )
        self.roadmap(
            [
                "| chg-a | order-create | order | N/A + reason | extend | full "
                "| server/src/main/java/org/sales/order/ | demo | 4 AC |",
            ]
        )
        self.change("chg-a")
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("docs/product/modules.csv", out)

    def test_missing_roadmap_fails(self):
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("MISSING:", out)

    def test_invalid_strategy_fails_closed(self):
        self.layout(strategy="packages")
        self.write("docs/product/proposal-roadmap.md", "# Roadmap\n\nNothing here.\n")
        code, out = self.run_check()
        self.assertEqual(1, code)
        self.assertIn("ERROR:", out)
        self.assertIn("invalid strategy", out)

    def test_bad_arguments_usage(self):
        code, out = self.run_check("--unknown")
        self.assertEqual(2, code)
        self.assertIn("Usage: check-roadmap.py [--strict]", out)


if __name__ == "__main__":
    unittest.main()
