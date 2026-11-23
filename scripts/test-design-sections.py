#!/usr/bin/env python3
"""Regression tests for ``check-design-sections.py`` and its module slice gate.

Covers the new ``--slice-only`` mode used by the 07 -> 08 hard gate:

* ``--slice-only`` ignores the other four design sections and the UI checks;
* ``module-packages`` requires all eight slice fields;
* primary capability / owner module / related modules must exist in the
  registries and the owner must match the capability's owner;
* ``Owned paths`` and ``Code packages`` are path-safe and live under the
  owner/related module roots;
* ``Integration paths`` must match ``code-layout.json`` and carry a reason and
  a task ID;
* ``Module card`` is create/update wording or ``N/A + reason``;
* ``footprint`` requires only owned/integration and treats owner ``N/A`` as
  absent;
* ``strategy=none`` (or a missing layout) skips the slice rules but keeps the
  legacy five-section check;
* the legacy full-mode section and UI checks still fire.
"""
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

CHECKER = Path(__file__).with_name("check-design-sections.py")

CAPABILITY_HEADER = (
    "capability_slug,capability_name,domain_id,owner_module,related_modules,"
    "code_packages,status,delivered_slices,remaining_slices,active_changes,notes"
)
MODULE_HEADER = (
    "module_slug,module_name,domain_id,frontend_paths,backend_paths,shared_paths,"
    "capabilities,status,notes"
)

DECISION_SUBSECTIONS = (
    "### 范围与非目标\nN/A + reason\n\n"
    "### 关键决策与权衡\n- decision\n\n"
    "### 现有代码变更影响\nN/A + reason\n\n"
    "### 设计任务分解与接口范围\n- task\n\n"
    "### 设计缺口与准入结论\nN/A + reason\n"
)

OTHER_SECTIONS = (
    "## Interface Design\nN/A + reason\n\n"
    "## Frontend Detailed Design\nN/A + reason\n\n"
    "## Backend Detailed Design\nN/A + reason\n\n"
    "## Test Design\nN/A + reason\n"
)

VALID_SLICE = """### Implementation Slice
- Primary capability: report-export
- Owner module: report
- Related modules: audit
- Slice type/coverage: initial / full
- Code packages: server/src/main/java/demo/report/; web/src/features/report/
- Owned paths: server/src/main/java/demo/report/export/; web/src/features/report/components/
- Integration paths:
  - web/src/router/routes.ts — register route; task T-003
- Module card: update web/src/features/report/MODULE.md
"""


def load(root: Path):
    spec = importlib.util.spec_from_file_location("check_design_sections", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    return module


class DesignSectionsTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.cds = load(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    # -- fixtures -------------------------------------------------------------
    def write(self, rel: str, text: str):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    def layout(self, strategy="module-packages", integration=None):
        layout = {
            "version": 1,
            "strategy": strategy,
            "roots": {"backend": "server/", "frontend": "web/"},
            "module_card": "MODULE.md",
        }
        if integration is not None:
            layout["integration_paths"] = integration
        self.write("docs/architecture/code-layout.json", json.dumps(layout))

    def registries(self):
        self.write(
            "docs/product/capabilities.csv",
            "\n".join(
                [
                    CAPABILITY_HEADER,
                    "report-export,Report Export,DOM-001,report,audit,"
                    "server/src/main/java/demo/report/,ACTIVE,N/A,N/A,N/A,N/A",
                ]
            )
            + "\n",
        )
        self.write(
            "docs/product/modules.csv",
            "\n".join(
                [
                    MODULE_HEADER,
                    "report,Report,DOM-001,web/src/features/report/,"
                    "server/src/main/java/demo/report/,N/A,report-export,ACTIVE,N/A",
                    "audit,Audit,DOM-001,N/A,server/src/main/java/demo/audit/,"
                    "N/A,N/A,ACTIVE,N/A",
                ]
            )
            + "\n",
        )

    def design(self, body: str, change="chg-a"):
        self.write(f"openspec/changes/{change}/design.md", body)

    def slice_design(self, slice_text=VALID_SLICE, change="chg-a"):
        self.design(
            "# Design\n\n## Design Decisions\n\n" + slice_text, change=change
        )

    def full_design(self, slice_text=VALID_SLICE):
        self.design(
            "# Design\n\n## Design Decisions\n\n"
            + DECISION_SUBSECTIONS
            + "\n"
            + slice_text
            + "\n"
            + OTHER_SECTIONS
        )

    def run_main(self, change="chg-a", slice_only=True, extra=()):
        args = ["--change", change]
        if slice_only:
            args.append("--slice-only")
        args.extend(extra)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                code = self.cds.main(args)
            except SystemExit as exc:  # pragma: no cover - main returns codes
                code = exc.code
        return code, out.getvalue() + err.getvalue()

    def assert_fails(self, needle=None):
        code, output = self.run_main()
        self.assertEqual(1, code, output)
        if needle is not None:
            self.assertIn(needle, output)
        return output

    # -- validity -------------------------------------------------------------
    def test_valid_module_packages_slice_passes(self):
        self.layout(integration=["web/src/router/routes.ts"])
        self.registries()
        self.slice_design()
        code, output = self.run_main()
        self.assertEqual(0, code, output)

    def test_full_valid_design_and_slice_passes(self):
        self.layout(integration=["web/src/router/routes.ts"])
        self.registries()
        self.full_design()
        code, output = self.run_main(slice_only=False)
        self.assertEqual(0, code, output)

    def test_slice_only_ignores_missing_other_sections_and_ui_checks(self):
        self.layout(integration=["web/src/router/routes.ts"])
        self.registries()
        self.slice_design()
        self.write(
            "openspec/changes/chg-a/design/figma-audit.md",
            "- Design source status: APPROVED\n",
        )
        code, output = self.run_main()
        self.assertEqual(0, code, output)

    def test_full_mode_still_requires_five_sections(self):
        self.layout(integration=["web/src/router/routes.ts"])
        self.registries()
        self.slice_design()
        code, output = self.run_main(slice_only=False)
        self.assertEqual(1, code, output)
        self.assertIn("missing section", output)

    def test_full_mode_ui_checks_still_run(self):
        self.layout(integration=["web/src/router/routes.ts"])
        self.registries()
        frontend = (
            "## Frontend Detailed Design\n"
            "### 路由与组件树\nroute tree\n"
            "### 设计令牌与实现映射\nmapping\n"
            "### PAGE→BLOCK→Figma 规格\nspecification\n"
            "### PAGE→BLOCK→组件映射\nmapping\n"
            "### 组件职责与状态\nstates\n"
            "### 事件处理\ndesign/ui-actions.csv element_id\n"
            "### 状态覆盖\nstates\n"
            "### 测试映射\ntests\n"
            "### 响应式与视口规则\n1440 baseline\n"
            "### 页面几何与保真断言\ngeometry\n"
        )
        self.design(
            "# Design\n\n## Design Decisions\n\n"
            + DECISION_SUBSECTIONS
            + "\n"
            + VALID_SLICE
            + "\n"
            + "## Interface Design\nN/A + reason\n\n"
            + frontend
            + "\n## Backend Detailed Design\nN/A + reason\n\n"
            + "## Test Design\nN/A + reason\n"
        )
        self.write(
            "openspec/changes/chg-a/design/figma-audit.md",
            "- Design source status: APPROVED\n",
        )
        code, output = self.run_main(slice_only=False)
        self.assertEqual(1, code, output)
        self.assertIn("token", output)

    # -- module-packages required fields --------------------------------------
    def test_module_packages_requires_all_fields(self):
        self.layout(integration=["web/src/router/routes.ts"])
        self.registries()
        for prefix in (
            "- Primary capability:",
            "- Owner module:",
            "- Related modules:",
            "- Slice type/coverage:",
            "- Code packages:",
            "- Owned paths:",
            "- Integration paths:",
            "- Module card:",
        ):
            with self.subTest(field=prefix):
                text = "\n".join(
                    row for row in VALID_SLICE.splitlines() if not row.startswith(prefix)
                ) + "\n"
                self.slice_design(text)
                output = self.assert_fails("missing required field")
                self.assertIn(prefix[2:].rstrip(":"), output)

    def test_required_field_n_a_is_rejected(self):
        self.layout(integration=["web/src/router/routes.ts"])
        self.registries()
        for field, value in (
            ("- Primary capability:", "N/A"),
            ("- Owner module:", "N/A"),
            ("- Slice type/coverage:", "N/A"),
            ("- Code packages:", "N/A"),
            ("- Owned paths:", "N/A"),
        ):
            with self.subTest(field=field):
                text = VALID_SLICE.replace(
                    next(
                        row
                        for row in VALID_SLICE.splitlines()
                        if row.startswith(field)
                    ),
                    f"{field} {value}",
                )
                self.slice_design(text)
                self.assert_fails("must not be empty or N/A")

    # -- registry cross-checks ------------------------------------------------
    def test_unknown_primary_capability_fails(self):
        self.layout(integration=["web/src/router/routes.ts"])
        self.registries()
        self.slice_design(VALID_SLICE.replace("report-export", "ghost-cap"))
        self.assert_fails("not in docs/product/capabilities.csv")

    def test_unknown_owner_and_related_modules_fail(self):
        self.layout(integration=["web/src/router/routes.ts"])
        self.registries()
        self.slice_design(
            VALID_SLICE.replace("- Owner module: report", "- Owner module: ghost")
        )
        self.assert_fails("not in docs/product/modules.csv")
        self.slice_design(
            VALID_SLICE.replace("- Related modules: audit", "- Related modules: ghost")
        )
        self.assert_fails("Related module 'ghost'")

    def test_module_packages_owner_must_match_capability_owner(self):
        self.layout(integration=["web/src/router/routes.ts"])
        self.registries()
        # ``audit`` exists in modules.csv but the capability is owned by ``report``.
        self.slice_design(
            VALID_SLICE.replace("- Owner module: report", "- Owner module: audit").replace(
                "- Related modules: audit", "- Related modules: N/A"
            )
        )
        self.assert_fails("must equal capability 'report-export' owner_module")

    # -- owned/package path rules ---------------------------------------------
    def test_owned_path_outside_modules_fails(self):
        self.layout(integration=["web/src/router/routes.ts"])
        self.registries()
        self.slice_design(
            VALID_SLICE.replace(
                "- Owned paths: server/src/main/java/demo/report/export/; "
                "web/src/features/report/components/",
                "- Owned paths: server/src/main/java/demo/billing/export/",
            )
        )
        self.assert_fails("outside the owner/related module paths")

    def test_owned_path_sibling_prefix_does_not_escape_root(self):
        self.layout(integration=["web/src/router/routes.ts"])
        self.registries()
        self.slice_design(
            VALID_SLICE.replace(
                "server/src/main/java/demo/report/export/",
                "server/src/main/java/demo/reporting/export/",
            ).replace("; web/src/features/report/components/", "")
        )
        self.assert_fails("outside the owner/related module paths")

    def test_unsafe_owned_and_package_paths_fail(self):
        self.layout(integration=["web/src/router/routes.ts"])
        self.registries()
        for value in (
            "/absolute/path/",
            "../escape/",
            "server/src/main/java/demo/report/*",
            "server/src/main/java/demo/report/**/export/",
            "server/src/main/java/demo/report/../billing/**",
        ):
            with self.subTest(value=value):
                text = VALID_SLICE.replace(
                    "- Owned paths: server/src/main/java/demo/report/export/; "
                    "web/src/features/report/components/",
                    f"- Owned paths: {value}",
                )
                self.slice_design(text)
                self.assert_fails()
        for value in (
            "/absolute/package/",
            "server/src/main/java/demo/report/?x",
            "server/src/main/java/demo/report/**/export/",
        ):
            with self.subTest(value=value):
                text = VALID_SLICE.replace(
                    "- Code packages: server/src/main/java/demo/report/; "
                    "web/src/features/report/",
                    f"- Code packages: {value}",
                )
                self.slice_design(text)
                self.assert_fails()

    def test_trailing_double_star_subtree_marker_passes(self):
        # Approved design §5.4 writes owned/package paths as subtrees ending in /**.
        self.layout(integration=["web/src/router/routes.ts"])
        self.registries()
        text = VALID_SLICE.replace(
            "- Code packages: server/src/main/java/demo/report/; "
            "web/src/features/report/",
            "- Code packages: server/src/main/java/demo/report/**; "
            "web/src/features/report/**",
        ).replace(
            "- Owned paths: server/src/main/java/demo/report/export/; "
            "web/src/features/report/components/",
            "- Owned paths: server/src/main/java/demo/report/export/**; "
            "web/src/features/report/**",
        )
        self.slice_design(text)
        code, output = self.run_main()
        self.assertEqual(0, code, output)

    # -- integration rules ----------------------------------------------------
    def test_integration_requires_reason_and_task(self):
        self.layout(integration=["web/src/router/routes.ts"])
        self.registries()
        self.slice_design(
            VALID_SLICE.replace(
                "  - web/src/router/routes.ts — register route; task T-003",
                "  - web/src/router/routes.ts — ; task T-003",
            )
        )
        self.assert_fails("must state a reason")
        self.slice_design(
            VALID_SLICE.replace(
                "  - web/src/router/routes.ts — register route; task T-003",
                "  - web/src/router/routes.ts — register route",
            )
        )
        self.assert_fails("must end with '; task <TASK-ID>'")

    def test_integration_not_in_layout_fails(self):
        self.layout(integration=["web/src/router/routes.ts"])
        self.registries()
        self.slice_design(
            VALID_SLICE.replace(
                "  - web/src/router/routes.ts — register route; task T-003",
                "  - server/src/main/java/demo/other/Boot.java — boot; task T-003",
            )
        )
        self.assert_fails("does not match code-layout.json integration_paths")

    def test_integration_paths_n_a_or_empty_is_valid(self):
        self.layout(integration=["web/src/router/routes.ts"])
        self.registries()
        for value in ("N/A + no thin registration changes", ""):
            with self.subTest(value=value):
                lines = [
                    line
                    for line in VALID_SLICE.splitlines()
                    if not line.strip().startswith("- web/src/router/routes.ts")
                ]
                text = "\n".join(lines).replace(
                    "- Integration paths:", f"- Integration paths: {value}".rstrip()
                ) + "\n"
                self.slice_design(text)
                code, output = self.run_main()
                self.assertEqual(0, code, output)

    def test_integration_layout_placeholder_segment_matches(self):
        self.layout(
            integration=["server/src/main/java/<org>/config/ApplicationConfig.java"]
        )
        self.registries()
        self.slice_design(
            VALID_SLICE.replace(
                "  - web/src/router/routes.ts — register route; task T-003",
                "  - server/src/main/java/demo/config/ApplicationConfig.java "
                "— register bean; task T-004",
            )
        )
        code, output = self.run_main()
        self.assertEqual(0, code, output)

    # -- module card ----------------------------------------------------------
    def test_module_card_wording(self):
        self.layout(integration=["web/src/router/routes.ts"])
        self.registries()
        self.slice_design(
            VALID_SLICE.replace(
                "- Module card: update web/src/features/report/MODULE.md",
                "- Module card: N/A",
            )
        )
        self.assert_fails("Module card")
        self.slice_design(
            VALID_SLICE.replace(
                "- Module card: update web/src/features/report/MODULE.md",
                "- Module card: N/A + templates were not changed",
            )
        )
        code, output = self.run_main()
        self.assertEqual(0, code, output)

    # -- footprint ------------------------------------------------------------
    def footprint_slice(self, owner="N/A"):
        return (
            "### Implementation Slice\n"
            f"- Owner module: {owner}\n"
            "- Primary capability: N/A\n"
            "- Owned paths: server/src/main/java/demo/report/export/\n"
            "- Integration paths:\n"
            "  - web/src/router/routes.ts — register route; task T-003\n"
        )

    def test_footprint_requires_only_owned_and_integration(self):
        self.layout(
            strategy="footprint", integration=["web/src/router/routes.ts"]
        )
        self.registries()
        self.slice_design(self.footprint_slice())
        code, output = self.run_main()
        self.assertEqual(0, code, output)

    def test_footprint_treats_owner_n_a_as_absent(self):
        self.layout(
            strategy="footprint", integration=["web/src/router/routes.ts"]
        )
        self.slice_design(self.footprint_slice(owner="N/A"))
        code, output = self.run_main()
        self.assertEqual(0, code, output)

    def test_footprint_integration_paths_n_a_is_valid(self):
        self.layout(
            strategy="footprint", integration=["web/src/router/routes.ts"]
        )
        self.slice_design(
            "### Implementation Slice\n"
            "- Owner module: N/A\n"
            "- Owned paths: server/src/main/java/demo/report/export/\n"
            "- Integration paths: N/A + no global registration changed\n"
        )
        code, output = self.run_main()
        self.assertEqual(0, code, output)

    def test_footprint_missing_owned_or_integration_fails(self):
        self.layout(
            strategy="footprint", integration=["web/src/router/routes.ts"]
        )
        self.registries()
        self.slice_design(
            self.footprint_slice().replace(
                "- Owned paths: server/src/main/java/demo/report/export/\n", ""
            )
        )
        self.assert_fails("missing required field: Owned paths")
        self.slice_design(
            "### Implementation Slice\n"
            "- Owned paths: server/src/main/java/demo/report/export/\n"
        )
        self.assert_fails("missing required field: Integration paths")

    def test_footprint_unknown_owner_fails(self):
        self.layout(
            strategy="footprint", integration=["web/src/router/routes.ts"]
        )
        self.registries()
        self.slice_design(self.footprint_slice(owner="ghost"))
        self.assert_fails("not in docs/product/modules.csv")

    # -- strategy none --------------------------------------------------------
    def test_strategy_none_skips_slice(self):
        self.design(
            "# Design\n\n## Design Decisions\n\n"
            + DECISION_SUBSECTIONS
            + "\n### Implementation Slice\n- Owned paths: anywhere/at/all/\n\n"
            + OTHER_SECTIONS
        )
        code, output = self.run_main(slice_only=False)
        self.assertEqual(0, code, output)

    def test_slice_only_strategy_none_does_not_require_slice(self):
        self.design("# Design\n\n## Design Decisions\n\nNo slice here.\n")
        code, output = self.run_main()
        self.assertEqual(0, code, output)

    # -- CLI ------------------------------------------------------------------
    def test_cli_requires_change_id(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = self.cds.main(["--slice-only"])
        self.assertEqual(2, code)
        self.assertIn("Usage:", err.getvalue())

    def test_cli_rejects_unknown_argument(self):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = self.cds.main(["--change", "chg-a", "--bogus"])
        self.assertEqual(2, code)
        self.assertIn("Usage:", err.getvalue())


if __name__ == "__main__":
    unittest.main()
