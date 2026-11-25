#!/usr/bin/env python3
"""Regression tests for scripts/update-capabilities.py."""
import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("update-capabilities.py")


def load(root: Path):
    spec = importlib.util.spec_from_file_location("update_capabilities", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = root
    return module


CAP_HEADER = (
    "capability_slug,capability_name,domain_id,owner_module,related_modules,"
    "status,delivered_slices,remaining_slices,active_changes,notes"
)


class UpdateCapabilitiesTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.mod = load(self.root)

    def tearDown(self):
        self._tmp.cleanup()

    def write(self, rel: str, text: str):
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8", newline="\n")

    def roadmap(self, rows, amendments=None):
        text = (
            "# Proposal Roadmap\n\n## Candidate Changes\n\n"
            "| Change ID | Primary Capability | Dependencies |\n|---|---|---|\n"
            + "\n".join(rows) + "\n"
        )
        if amendments:
            text += (
                "\n## Roadmap Amendments\n\n"
                "| Change ID | Primary Capability | Depends On | Reason | Requester "
                "| Approver | Date | Baseline Impact |\n|---|---|---|---|---|---|---|---|\n"
                + "\n".join(amendments) + "\n"
            )
        self.write("docs/product/proposal-roadmap.md", text)

    def capabilities(self, active="N/A"):
        self.write(
            "docs/product/capabilities.csv",
            "\n".join([
                CAP_HEADER,
                f"order-create,Order Create,DOM-001,order,N/A,ACTIVE,N/A,N/A,{active},N/A",
                "order-status,Order Status,DOM-001,order,N/A,PLANNED,N/A,N/A,N/A,N/A",
            ]) + "\n",
        )

    def test_add_and_remove_active_change(self):
        self.roadmap(["| chg-a | order-create | none |"])
        self.capabilities("N/A")
        self.assertEqual(0, self.mod.update("chg-a", "add"))
        rows = self.mod._read_rows()
        self.assertEqual(["chg-a"], rows[0]["active_changes"].split(";") if rows[0]["active_changes"] != "N/A" else [])
        self.assertEqual(0, self.mod.update("chg-a", "add"))
        rows = self.mod._read_rows()
        self.assertEqual("chg-a", rows[0]["active_changes"])
        self.assertEqual(0, self.mod.update("chg-a", "remove"))
        rows = self.mod._read_rows()
        self.assertEqual("N/A", rows[0]["active_changes"])

    def test_unknown_capability_fails(self):
        self.roadmap(["| chg-a | ghost-cap | none |"])
        self.capabilities("N/A")
        with self.assertRaisesRegex(ValueError, "not found"):
            self.mod.update("chg-a", "add")

    def test_unregistered_change_fails(self):
        self.roadmap(["| chg-a | order-create | none |"])
        self.capabilities("N/A")
        with self.assertRaisesRegex(ValueError, "not in the roadmap"):
            self.mod.update("chg-b", "add")

    def test_approved_amendment_change_updates_registry(self):
        self.roadmap(
            ["| chg-a | order-create | none |"],
            amendments=[
                "| chg-late | order-status | none | late | Alice | Tech Lead "
                "| 2026-11-23 | CHANGE_ONLY |",
            ],
        )
        self.capabilities("N/A")
        self.assertEqual(0, self.mod.update("chg-late", "add"))
        rows = self.mod._read_rows()
        self.assertEqual("chg-late", rows[1]["active_changes"])


if __name__ == "__main__":
    unittest.main()
