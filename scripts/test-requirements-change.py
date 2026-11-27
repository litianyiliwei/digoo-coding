#!/usr/bin/env python3
"""Regression tests for ``check-requirements.py --change``.

Covers the module-packages capability/slice rules added on top of the legacy
US/AC structure checks: proposal capabilities, Scenario -> AC tracing, Slice
position, Acceptance Walkthrough coverage, the 12-AC budget exception and the
roadmap amendment fallback for late Changes. ``strategy=none`` must keep the
legacy behaviour.
"""
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

CHECKER = Path(__file__).with_name("check-requirements.py")

CAPABILITY_HEADER = (
    "capability_slug,capability_name,domain_id,owner_module,related_modules,"
    "status,delivered_slices,remaining_slices,active_changes,notes"
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

POSITIONS = ("entry", "behavior", "result")


def load(root: Path):
    spec = importlib.util.spec_from_file_location("check_requirements", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    return module


def table(header: str, rows) -> str:
    columns = len([cell for cell in header.strip("|").split("|")])
    separator = "|" + "---|" * columns
    return "\n".join([header, separator, *rows]) + "\n"


class RequirementsChangeTests(unittest.TestCase):
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

    def layout(self, strategy="module-packages"):
        self.write(
            "docs/architecture/code-layout.json",
            json.dumps(
                {
                    "version": 1,
                    "strategy": strategy,
                    "roots": {"backend": "server/", "frontend": "web/"},
                    "module_card": "MODULE.md",
                }
            ),
        )

    def registries(self, slugs=("report-export", "billing")):
        rows = [
            f"{slug},{slug},DOM-001,report,N/A,ACTIVE,N/A,slice-2,N/A,N/A"
            for slug in slugs
        ]
        self.write(
            "docs/product/capabilities.csv",
            "\n".join([CAPABILITY_HEADER, *rows]) + "\n",
        )

    def project_docs(self):
        self.write("docs/product/workflows.md", "## FLOW-001 Demo workflow\n")
        self.write("docs/product/business-rules.md", "| BR-001 | demo rule |\n")

    def roadmap(self, main_rows=(), amendment_rows=None, main_header=None):
        text = (
            "# Proposal Roadmap\n\n## Candidate Changes\n\n"
            + table(main_header or MAIN_HEADER, list(main_rows))
        )
        if amendment_rows is not None:
            text += "\n## Roadmap Amendments\n\n" + table(
                AMENDMENT_HEADER, list(amendment_rows)
            )
        self.write("docs/product/proposal-roadmap.md", text)

    def main_row(
        self,
        change="chg-a",
        primary="report-export",
        slice_type="initial",
    ):
        return (
            f"| {change} | {primary} | report | N/A + reason | {slice_type} | full "
            "| server/src/main/java/org/report/ | demo | 3 AC |"
        )

    def amendment_row(
        self,
        change="chg-late",
        primary="report-export",
        slice_type="initial",
        approver="Tech Lead",
    ):
        return (
            f"| {change} | {primary} | report | N/A + reason | {slice_type} | full "
            "| server/src/main/java/org/report/ | late request | Alice | "
            f"{approver} | 2026-11-23 | CHANGE_ONLY |"
        )

    def proposal(self, change="chg-a", new=("report-export",), modified=("billing",)):
        lines = ["# Proposal", "", "## Capabilities", "", "### New Capabilities"]
        lines += [f"- `{slug}`: new behavior" for slug in new]
        lines += ["", "### Modified Capabilities"]
        lines += [f"- `{slug}`: changed behavior" for slug in modified]
        lines += [
            "",
            "## Target Platforms",
            "",
            "| Platform | In scope | Notes |",
            "|---|---|---|",
            "| web | YES | Browser console |",
            "",
        ]
        self.write(f"openspec/changes/{change}/proposal.md", "\n".join(lines) + "\n")

    def specs(self, change="chg-a", scenarios=("Normal export", "Unauthorized export")):
        lines = ["## ADDED Requirements", "", "### Requirement: Export reports", ""]
        for index, title in enumerate(scenarios, 1):
            lines += [
                f"#### Scenario: {title}",
                f"- **WHEN** condition {index}",
                f"- **THEN** result {index}",
                "",
            ]
        self.write(
            f"openspec/changes/{change}/specs/report-export/spec.md",
            "\n".join(lines),
        )

    def default_acs(self):
        return [
            {"id": "AC-001", "scenario": "Normal export", "position": "entry"},
            {"id": "AC-002", "scenario": "Unauthorized export", "position": "behavior"},
            {"id": "AC-003", "scenario": "Normal export", "position": "result"},
        ]

    def stories(self, change="chg-a", acs=None, walkthrough=None,
                include_walkthrough=True, budget_lines=None):
        acs = self.default_acs() if acs is None else acs
        refs = ";".join(ac["id"] for ac in acs)
        lines = [
            "# Proposal-Level User Stories and Acceptance Criteria",
            "",
            "- Target platforms: web",
            "",
            "| US ID | User role | Story/value | Related FLOW/NODE/BR | AC IDs | "
            "Status | Source/approval |",
            "|---|---|---|---|---|---|---|",
            f"| US-001 | tester | As a user I want export | FLOW-001 | {refs} | "
            "DRAFT | proposal |",
            "",
            "## Acceptance Criteria",
            "",
        ]
        for ac in acs:
            lines += [
                f"### {ac['id']}",
                "- Given: precondition",
                "- When: action",
                "- Then: observable result",
                "- Coverage: permissions/empty values/boundaries/exceptions",
            ]
            if ac.get("scenario") is not None:
                lines.append(f"- Scenario: {ac['scenario']}")
            if ac.get("position") is not None:
                lines.append(f"- Slice position: {ac['position']}")
            lines.append("")
        if include_walkthrough:
            ids = (
                [ac["id"] for ac in acs][:3] if walkthrough is None else walkthrough
            )
            lines += ["## Acceptance Walkthrough", ""]
            for index, ac_id in enumerate(ids, 1):
                lines.append(f"{index}. {ac_id} — walkthrough step")
            lines.append("")
        lines += ["## Slice Budget", "", f"- AC count: {len(acs)}"]
        if budget_lines is not None:
            lines += budget_lines
        else:
            lines.append("- Budget exception: N/A (only when AC count exceeds 12)")
        self.write(
            f"openspec/changes/{change}/design/user-stories.md",
            "\n".join(lines) + "\n",
        )

    def valid_setup(self):
        self.layout()
        self.registries()
        self.project_docs()
        self.roadmap(main_rows=[self.main_row()])
        self.proposal()
        self.specs()
        self.stories()

    def run_check(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(out):
            code = self.cr.main(list(args))
        return code, out.getvalue()

    # -- passing --------------------------------------------------------------
    def test_valid_change_passes(self):
        self.valid_setup()
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(0, code, out)
        self.assertNotIn("ERROR:", out)
        self.assertIn(
            "Requirements artifact structure check passed (Change chg-a).", out
        )

    def test_every_scenario_referenced_passes(self):
        self.valid_setup()
        self.stories(
            acs=[
                {"id": "AC-001", "scenario": "Normal export", "position": "entry"},
                {"id": "AC-002", "scenario": "Normal export", "position": "behavior"},
                {"id": "AC-003", "scenario": "Unauthorized export",
                 "position": "result"},
            ]
        )
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(0, code, out)
        self.assertNotIn("ERROR:", out)

    def test_budget_exception_with_ascii_hyphen_passes(self):
        self.layout()
        self.registries()
        self.project_docs()
        self.roadmap(main_rows=[self.main_row()])
        self.proposal()
        self.specs(scenarios=("Normal export",))
        self.stories(
            acs=[
                {"id": f"AC-{index:03d}", "scenario": "Normal export",
                 "position": POSITIONS[index % 3]}
                for index in range(1, 14)
            ],
            walkthrough=["AC-001", "AC-002", "AC-003"],
            budget_lines=["- Budget exception: Tech Lead - scope review approved"],
        )
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(0, code, out)
        self.assertNotIn("ERROR:", out)

    def test_late_change_with_approved_amendment_passes(self):
        self.layout()
        self.registries()
        self.project_docs()
        self.roadmap([], amendment_rows=[self.amendment_row()])
        self.proposal(change="chg-late")
        self.specs(change="chg-late")
        self.stories(change="chg-late")
        code, out = self.run_check("--change", "chg-late")
        self.assertEqual(0, code, out)
        self.assertNotIn("ERROR:", out)

    def test_strategy_none_keeps_legacy(self):
        self.project_docs()
        self.stories(
            acs=[
                {"id": "AC-001", "scenario": None, "position": None},
                {"id": "AC-002", "scenario": None, "position": None},
            ],
            include_walkthrough=False,
        )
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(0, code, out)
        self.assertNotIn("ERROR:", out)
        self.assertIn(
            "Requirements artifact structure check passed (Change chg-a).", out
        )

    def test_footprint_runs_scenario_and_story_rules_only(self):
        self.layout("footprint")
        self.project_docs()
        self.proposal()
        self.specs(scenarios=("Normal export", "Unauthorized export"))
        self.stories()
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(0, code, out)
        self.assertNotIn("docs/product/capabilities.csv", out)

    def test_footprint_requires_slice_position(self):
        self.layout("footprint")
        self.project_docs()
        self.specs(scenarios=("Normal export", "Unauthorized export"))
        self.stories()
        acs = self.default_acs()
        acs[1]["position"] = None
        self.stories(acs=acs)
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(1, code, out)
        self.assertIn("ERROR:", out)
        self.assertIn("Slice position", out)
        self.assertIn("AC-002", out)

    # -- proposal capabilities -------------------------------------------------
    def test_unknown_primary_capability_fails(self):
        self.layout()
        self.registries()
        self.project_docs()
        self.roadmap(main_rows=[self.main_row(primary="ghost-cap")])
        self.proposal()
        self.specs()
        self.stories()
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(1, code, out)
        self.assertIn("ERROR:", out)
        self.assertIn("ghost-cap", out)

    def test_modified_capability_not_in_registry_fails(self):
        self.layout()
        self.registries()
        self.project_docs()
        self.roadmap(main_rows=[self.main_row(slice_type="extend")])
        self.proposal(modified=("report-export", "ghost-modified"))
        self.specs()
        self.stories()
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(1, code, out)
        self.assertIn("ERROR:", out)
        self.assertIn("ghost-modified", out)
        self.assertIn("docs/product/capabilities.csv", out)

    def test_extend_primary_must_be_modified(self):
        self.layout()
        self.registries()
        self.project_docs()
        self.roadmap(main_rows=[self.main_row(slice_type="extend")])
        self.proposal(new=("report-export", "billing"), modified=("billing",))
        self.specs()
        self.stories()
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(1, code, out)
        self.assertIn("ERROR:", out)
        self.assertIn("Modified Capabilities", out)

    # -- Scenario -> AC tracing ------------------------------------------------
    def test_unreferenced_scenario_fails(self):
        self.valid_setup()
        self.stories(
            acs=[
                {"id": "AC-001", "scenario": "Normal export", "position": "entry"},
                {"id": "AC-002", "scenario": "Normal export", "position": "behavior"},
                {"id": "AC-003", "scenario": "Normal export", "position": "result"},
            ]
        )
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(1, code, out)
        self.assertIn("ERROR:", out)
        self.assertIn("Unauthorized export", out)
        self.assertIn("not referenced", out)

    def test_missing_scenario_line_fails(self):
        self.valid_setup()
        acs = self.default_acs()
        acs[0]["scenario"] = None
        self.stories(acs=acs)
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(1, code, out)
        self.assertIn("ERROR:", out)
        self.assertIn("AC-001", out)
        self.assertIn("Scenario", out)

    # -- Slice position -------------------------------------------------------
    def test_missing_slice_position_fails(self):
        self.valid_setup()
        acs = self.default_acs()
        acs[1]["position"] = None
        self.stories(acs=acs)
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(1, code, out)
        self.assertIn("ERROR:", out)
        self.assertIn("AC-002", out)
        self.assertIn("Slice position", out)

    def test_invalid_slice_position_fails(self):
        self.valid_setup()
        acs = self.default_acs()
        acs[1]["position"] = "middle"
        self.stories(acs=acs)
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(1, code, out)
        self.assertIn("ERROR:", out)
        self.assertIn("middle", out)
        self.assertIn("entry|behavior|result", out)

    # -- Acceptance Walkthrough ------------------------------------------------
    def test_walkthrough_missing_fails(self):
        self.valid_setup()
        self.stories(include_walkthrough=False)
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(1, code, out)
        self.assertIn("ERROR:", out)
        self.assertIn("Acceptance Walkthrough", out)

    def test_walkthrough_unknown_ac_fails(self):
        self.valid_setup()
        self.stories(walkthrough=["AC-001", "AC-999", "AC-003"])
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(1, code, out)
        self.assertIn("ERROR:", out)
        self.assertIn("AC-999", out)
        self.assertIn("undefined", out)

    def test_walkthrough_missing_position_warns_and_passes(self):
        self.valid_setup()
        self.stories(walkthrough=["AC-001", "AC-002"])
        code, out = self.run_check("--change", "chg-a", "--strict")
        self.assertEqual(0, code, out)
        self.assertIn("WARN (advisory):", out)
        self.assertIn("result", out)

    # -- budget ---------------------------------------------------------------
    def test_budget_over_without_exception_fails(self):
        self.layout()
        self.registries()
        self.project_docs()
        self.roadmap(main_rows=[self.main_row()])
        self.proposal()
        self.specs(scenarios=("Normal export",))
        self.stories(
            acs=[
                {"id": f"AC-{index:03d}", "scenario": "Normal export",
                 "position": POSITIONS[index % 3]}
                for index in range(1, 14)
            ],
            walkthrough=["AC-001", "AC-002", "AC-003"],
            budget_lines=["- Budget exception: N/A"],
        )
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(1, code, out)
        self.assertIn("ERROR:", out)
        self.assertIn("Budget exception", out)
        self.assertIn("12", out)

    # -- roadmap registration / amendment -------------------------------------
    def test_late_change_without_amendment_fails(self):
        self.layout()
        self.registries()
        self.project_docs()
        self.roadmap([], amendment_rows=[])
        self.proposal(change="chg-late")
        self.specs(change="chg-late")
        self.stories(change="chg-late")
        code, out = self.run_check("--change", "chg-late")
        self.assertEqual(1, code, out)
        self.assertIn("ERROR:", out)
        self.assertIn("amendment", out)
        self.assertIn("chg-late", out)

    def test_unapproved_amendment_fails(self):
        self.layout()
        self.registries()
        self.project_docs()
        self.roadmap([], amendment_rows=[self.amendment_row(approver="  ")])
        self.proposal(change="chg-late")
        self.specs(change="chg-late")
        self.stories(change="chg-late")
        code, out = self.run_check("--change", "chg-late")
        self.assertEqual(1, code, out)
        self.assertIn("ERROR:", out)
        self.assertIn("Approver", out)

    # -- target platform declaration -------------------------------------------
    def test_missing_target_platforms_fails(self):
        self.valid_setup()
        path = self.root / "openspec/changes/chg-a/design/user-stories.md"
        text = path.read_text(encoding="utf-8").replace(
            "- Target platforms: web\n", ""
        )
        path.write_text(text, encoding="utf-8", newline="\n")
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(1, code, out)
        self.assertIn("ERROR:", out)
        self.assertIn("Target platforms", out)

    def test_proposal_target_platforms_must_match_user_stories(self):
        self.valid_setup()
        proposal = self.root / "openspec/changes/chg-a/proposal.md"
        text = proposal.read_text(encoding="utf-8").replace(
            "| web | YES | Browser console |",
            "| android | YES | Mobile app |",
        )
        proposal.write_text(text, encoding="utf-8", newline="\n")
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(1, code, out)
        self.assertIn("ERROR:", out)
        self.assertIn("disagree with user-stories.md", out)

    def test_missing_proposal_platform_section_fails(self):
        self.valid_setup()
        proposal = self.root / "openspec/changes/chg-a/proposal.md"
        text = proposal.read_text(encoding="utf-8").split("## Target Platforms")[0]
        proposal.write_text(text, encoding="utf-8", newline="\n")
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(1, code, out)
        self.assertIn("ERROR:", out)
        self.assertIn("proposal.md: missing '## Target Platforms'", out)

    def test_unsupported_platform_fails(self):
        self.valid_setup()
        path = self.root / "openspec/changes/chg-a/design/user-stories.md"
        text = path.read_text(encoding="utf-8").replace(
            "- Target platforms: web", "- Target platforms: web; blackberry"
        )
        path.write_text(text, encoding="utf-8", newline="\n")
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(1, code, out)
        self.assertIn("ERROR:", out)
        self.assertIn("unsupported target platform", out)

    def test_roadmap_target_platforms_must_match(self):
        self.valid_setup()
        # Give the roadmap row an explicit Target Platforms column.
        header = MAIN_HEADER + " Target Platforms |"
        self.roadmap(
            main_rows=[self.main_row() + " android |"],
            main_header=header,
        )
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(1, code, out)
        self.assertIn("disagree with user-stories.md", out)


        self.valid_setup()
        self.stories(
            acs=self.default_acs(),
            walkthrough=["AC-001", "AC-002", "AC-003"],
        )
        # US row now references an AC that has no section.
        path = self.root / "openspec/changes/chg-a/design/user-stories.md"
        text = path.read_text(encoding="utf-8").replace(
            "AC-001;AC-002;AC-003", "AC-001;AC-002;AC-999"
        )
        path.write_text(text, encoding="utf-8", newline="\n")
        code, out = self.run_check("--change", "chg-a")
        self.assertEqual(1, code, out)
        self.assertIn("ERROR:", out)
        self.assertIn("AC-999", out)

    def test_bad_arguments_usage(self):
        code, out = self.run_check("--change")
        self.assertEqual(2, code)
        self.assertIn("Usage:", out)

    def test_invalid_change_id(self):
        code, out = self.run_check("--change", "Chg_A")
        self.assertEqual(2, code)
        self.assertIn("Invalid change-id", out)


if __name__ == "__main__":
    unittest.main()
