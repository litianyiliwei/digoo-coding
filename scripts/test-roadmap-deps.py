#!/usr/bin/env python3
"""Regression tests for the roadmap dependency graph (scripts/roadmap_deps.py)."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("roadmap_deps.py")


def load(root: Path):
    spec = importlib.util.spec_from_file_location("roadmap_deps", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    return module


def table(header: str, rows) -> str:
    columns = len([cell for cell in header.strip("|").split("|")])
    separator = "|" + "---|" * columns
    return "\n".join([header, separator, *rows]) + "\n"


MAIN_HEADER = "| Change ID | Dependencies |"
AMENDMENT_HEADER = (
    "| Change ID | Depends On | Reason | Requester | Approver | Date "
    "| Baseline Impact |"
)


class RoadmapDependencyTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.deps = load(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel: str, text: str):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")
        return path

    def roadmap(
        self,
        rows,
        amendment_rows=None,
        rationale="- chg-a ← chg-b: because b is the foundation",
        main_header=MAIN_HEADER,
        amendment_header=AMENDMENT_HEADER,
    ):
        text = (
            "# Proposal Roadmap\n\n## Candidate Changes\n\n"
            + table(main_header, rows)
        )
        if amendment_rows is not None:
            text += "\n## Roadmap Amendments\n\n" + table(
                amendment_header, amendment_rows
            )
        text += "\n## Ordering Rationale\n\n" + rationale + "\n"
        self.write("docs/product/proposal-roadmap.md", text)

    def validate(self, require_dependencies=False):
        parsed = self.deps.parse()
        return parsed, *self.deps.validate(parsed, require_dependencies=require_dependencies)

    # -- parsing ---------------------------------------------------------------
    def test_parse_main_and_approved_amendment(self):
        self.roadmap(
            [
                "| chg-a | chg-b |",
                "| chg-b | none |",
            ],
            amendment_rows=[
                "| chg-late | chg-a; chg-b | late | Alice | Tech Lead "
                "| 2026-11-23 | CHANGE_ONLY |",
            ],
        )
        parsed = self.deps.parse()
        self.assertEqual(["chg-a", "chg-b", "chg-late"], parsed["registered"])
        self.assertEqual(
            [("chg-a", "chg-b"), ("chg-late", "chg-a"), ("chg-late", "chg-b")],
            [(edge["change"], edge["depends_on"]) for edge in parsed["edges"]],
        )

    def test_unapproved_amendment_dependencies_ignored(self):
        self.roadmap(
            ["| chg-a | none |"],
            amendment_rows=[
                "| chg-late | chg-a | late | Alice |  | 2026-11-23 | CHANGE_ONLY |",
            ],
        )
        parsed = self.deps.parse()
        self.assertNotIn("chg-late", parsed["registered"])
        self.assertEqual([], parsed["edges"])

    def test_na_and_none_mean_no_dependencies(self):
        self.roadmap(
            [
                "| chg-a | N/A |",
                "| chg-b | none |",
                "| chg-c | None; N/A |",
            ]
        )
        parsed = self.deps.parse()
        self.assertEqual([], parsed["edges"])

    def test_unapproved_amendment_still_reports_fields(self):
        self.roadmap(
            ["| chg-a | none |"],
            amendment_rows=[
                "| chg-late | chg-a | late | Alice | Tech Lead |  "
                "| CHANGE_ONLY |",
            ],
        )
        parsed = self.deps.parse()
        entry = next(item for item in parsed["entries"] if item["change_id"] == "chg-late")
        self.assertFalse(entry["approved"])
        self.assertEqual(["chg-a"], entry["depends_on"])

    # -- graph validation -----------------------------------------------------
    def test_unknown_dependency_fails(self):
        self.roadmap(["| chg-a | missing-change |"])
        _, errors, _, _ = self.validate()
        self.assertTrue(any("unknown dependency" in error for error in errors), errors)

    def test_self_dependency_fails(self):
        self.roadmap(["| chg-a | chg-a |"])
        _, errors, _, _ = self.validate()
        self.assertTrue(any("depends on itself" in error for error in errors), errors)

    def test_duplicate_edge_fails(self):
        self.roadmap(["| chg-a | chg-b; chg-b |", "| chg-b | none |"])
        _, errors, _, _ = self.validate()
        self.assertTrue(any("duplicate dependency" in error for error in errors), errors)

    def test_cycle_fails(self):
        self.roadmap(["| chg-a | chg-b |", "| chg-b | chg-a |"])
        _, errors, _, _ = self.validate()
        self.assertTrue(any("cycle" in error for error in errors), errors)

    def test_dependency_after_dependent_warns(self):
        self.roadmap(["| chg-a | chg-b |", "| chg-b | none |"])
        _, _, _, advisories = self.validate()
        self.assertTrue(
            any("listed after" in warning for warning in advisories), advisories
        )

    def test_missing_rationale_warns(self):
        self.roadmap(["| chg-a | chg-b |", "| chg-b | none |"], rationale="")
        _, _, _, advisories = self.validate()
        self.assertTrue(
            any("ordering rationale" in warning.lower() for warning in advisories),
            advisories,
        )

    # -- column requirements --------------------------------------------------
    def test_missing_dependencies_column_rejected_only_when_required(self):
        self.roadmap(
            ["| chg-a |"],
            rationale="",
            main_header="| Change ID |",
        )
        _, errors, _, _ = self.validate(require_dependencies=False)
        self.assertEqual([], errors)
        _, errors, _, _ = self.validate(require_dependencies=True)
        self.assertTrue(any("missing Dependencies column" in error for error in errors))

    def test_blank_or_placeholder_dependency_rejected(self):
        self.roadmap(["| chg-a |  |", "| chg-b | PENDING |", "| chg-c | N/A |"])
        _, errors, _, _ = self.validate(require_dependencies=True)
        messages = "\n".join(errors)
        self.assertIn("chg-a", messages)
        self.assertIn("chg-b", messages)
        self.assertNotIn("chg-c", messages)

    # -- runtime dependency states -------------------------------------------
    def state(self, completed=(), transitions=(), changes=None, abandoned=()):
        return {
            "completed_changes": [{"change_id": item} for item in completed],
            "transition_history": [
                {
                    "step_id": "10-acceptance-audit",
                    "change_id": item,
                    "completed_at": "2026-11-23T00:00:00+00:00",
                }
                for item in transitions
            ],
            "changes": changes or {},
            "abandoned_changes": [{"change_id": item} for item in abandoned],
        }

    def test_states_cover_all_dependency_outcomes(self):
        self.roadmap(
            [
                "| chg-a | chg-b; chg-c; chg-d; chg-e |",
                "| chg-b | none |",
                "| chg-c | none |",
                "| chg-d | none |",
                "| chg-e | none |",
            ]
        )
        state = self.state(
            completed=["chg-b"],
            transitions=["chg-b"],
            changes={"chg-c": {"status": "ACTIVE", "current_step": "07-detailed-design"}},
            abandoned=["chg-d"],
        )
        parsed = self.deps.parse()
        states = self.deps.dependency_states(parsed, state, "chg-a")
        by_id = {item["id"]: item for item in states}
        self.assertEqual("ACCEPTED", by_id["chg-b"]["status"])
        self.assertEqual("ACTIVE", by_id["chg-c"]["status"])
        self.assertEqual("07-detailed-design", by_id["chg-c"]["stage"])
        self.assertEqual("ABANDONED", by_id["chg-d"]["status"])
        self.assertEqual("NOT_STARTED", by_id["chg-e"]["status"])

    def test_transitive_broken_chain(self):
        self.roadmap(
            [
                "| chg-a | chg-b |",
                "| chg-b | chg-c |",
                "| chg-c | none |",
            ]
        )
        state = self.state(completed=["chg-b"], transitions=["chg-b"])
        parsed = self.deps.parse()
        states = self.deps.dependency_states(parsed, state, "chg-a")
        self.assertEqual("BROKEN", states[0]["status"])
        self.assertEqual(["chg-a", "chg-b", "chg-c"], states[0]["chain"])

    def test_unknown_dependency_state(self):
        self.roadmap(["| chg-a | ghost |"])
        parsed = self.deps.parse()
        state = self.state()
        states = self.deps.dependency_states(parsed, state, "chg-a")
        self.assertEqual("UNKNOWN", states[0]["status"])

    def test_cycle_does_not_recurse_forever(self):
        self.roadmap(["| chg-a | chg-b |", "| chg-b | chg-a |"])
        parsed = self.deps.parse()
        state = self.state()
        states = self.deps.dependency_states(parsed, state, "chg-a")
        self.assertEqual("BROKEN", states[0]["status"])


if __name__ == "__main__":
    unittest.main()
