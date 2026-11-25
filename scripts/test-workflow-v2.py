#!/usr/bin/env python3
"""Regression tests for the v2 multi-lane workflow state machine."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("workflow.py")
spec = importlib.util.spec_from_file_location("workflow_v2", SCRIPT)
w = importlib.util.module_from_spec(spec)
spec.loader.exec_module(w)

PROJECT_STEPS = ["01-project-bootstrap", "02-requirements-analysis",
                 "03-project-architecture-baseline", "04-proposal-planning"]
CHANGE_STEPS = [s["id"] for s in w.STAGES if s["scope"] == "change"]


class WorkflowV2Tests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        w.ROOT = self.root
        w.STATE = self.root / "workflow-state.json"
        for rel in ("workflow", "docs", "process"):
            (self.root / rel).mkdir()
        (self.root / "check.log").write_text("PASS\n", encoding="utf-8")
        (self.root / "out.md").write_text("artifact\n", encoding="utf-8")
        self._originals = {}
        for name, value in (
            ("run_baseline_gate", lambda *args, **kwargs: None),
            ("run_baseline_impact_gate", lambda *args, **kwargs: None),
            ("verify_manifest", lambda path: (True, [])),
            ("run_slice_gate", lambda change_id: None),
            ("run_footprint_gate", lambda change_id: None),
            ("static_evidence_gate", lambda *args: None),
        ):
            self._originals[name] = getattr(w, name, None)
            setattr(w, name, value)

    def tearDown(self):
        for name, value in self._originals.items():
            if value is not None:
                setattr(w, name, value)
        self.tmp.cleanup()

    # -- fixtures -------------------------------------------------------------
    def project_lane(self, completed=None, current="PROJECT_COMPLETE"):
        return {
            "current_step": current,
            "completed_steps": list(completed or PROJECT_STEPS),
            "skipped_steps": [],
            "pending_approvals": [],
            "blocked_items": [],
        }

    def state(self, project=None, changes=None, **overrides):
        data = {
            "state_schema_version": "2.0",
            "project_name": "test",
            "project": project or self.project_lane(),
            "changes": changes or {},
            "completed_changes": [],
            "abandoned_changes": [],
            "implementation_lease": None,
            "approvals_history": [],
            "transition_history": [],
            "skip_history": [],
            "reopen_history": [],
            "reset_history": [],
            "topology_migrations": [],
            "change_history": [],
            "baseline": {},
            "approval_policy": "standard",
            "approval_policy_history": [],
            "last_transition": None,
            "last_completed_outputs": [],
        }
        data.update(overrides)
        return data

    def write_state(self, data):
        w.STATE.write_text(json.dumps(data), encoding="utf-8")

    def lane(self, current="05-feature-requirements", completed=None, status="ACTIVE",
             pending=None, blocked=None, pending_annotations=None):
        return {
            "status": status,
            "current_step": current,
            "completed_steps": list(completed or []),
            "skipped_steps": [],
            "pending_approvals": list(pending or []),
            "blocked_items": list(blocked or []),
            "started_at": "2026-11-23T00:00:00+00:00",
            "dependencies": {"required": [], "verified_at": "", "waivers": []},
        }

    def roadmap(self, rows, amendments=None, rationale=None):
        text = (
            "# Proposal Roadmap\n\n## Candidate Changes\n\n"
            "| Change ID | Dependencies |\n|---|---|\n"
            + "\n".join(rows)
            + "\n"
        )
        if amendments:
            text += (
                "\n## Roadmap Amendments\n\n"
                "| Change ID | Depends On | Reason | Requester | Approver | Date "
                "| Baseline Impact |\n|---|---|---|---|---|---|---|\n"
                + "\n".join(amendments)
                + "\n"
            )
        text += "\n## Ordering Rationale\n\n" + (rationale or "") + "\n"
        path = self.root / "docs/product/proposal-roadmap.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def accepted(self, change_id):
        return {
            "completed_changes": [{"change_id": change_id,
                                   "acceptance_evidence": "workflow/evidence/10.json"}],
            "transition_history": [{"step_id": "10-acceptance-audit",
                                    "change_id": change_id,
                                    "completed_at": "2026-11-23T00:00:00+00:00",
                                    "evidence_path": "workflow/evidence/10.json"}],
        }

    def start_args(self, change_id, **overrides):
        values = {
            "change_id": change_id,
            "retry_abandoned": False,
            "waive_dependency": [],
            "reason": "",
            "by": "",
            "evidence": "",
            "note": "",
        }
        values.update(overrides)
        return type("Args", (), values)()

    def approve_args(self, step, change_id, approver="Owner"):
        return type("Args", (), {
            "step": step, "change_id": change_id, "approver": approver,
            "approved_at": "2026-11-23", "evidence": "check.log",
        })()

    # -- upgrade --------------------------------------------------------------
    def test_upgrade_state_wraps_v1_and_is_idempotent(self):
        v1 = {
            "project_name": "test", "active_change_id": "chg-a",
            "completed_steps": PROJECT_STEPS + CHANGE_STEPS[:2],
            "current_step": "07-detailed-design",
            "pending_approvals": [{"step_id": "06-figma-design-review",
                                   "change_id": "chg-a"}],
            "blocked_items": [],
            "approvals_history": [{"step_id": "05-feature-requirements",
                                   "change_id": "chg-a", "approver": "Owner",
                                   "approved_at": "2026-11-20", "evidence": "check.log"}],
            "transition_history": [{"step_id": "05-feature-requirements",
                                    "change_id": "chg-a", "completed_at": "2026-11-20"}],
        }
        self.write_state(v1)
        args = type("Args", (), {"reason": "adopt v2 lanes", "note": ""})()
        self.assertEqual(0, w.cmd_upgrade_state(args))
        state = w.load_state()
        self.assertEqual("2.0", state["state_schema_version"])
        self.assertEqual(PROJECT_STEPS, state["project"]["completed_steps"])
        self.assertEqual("PROJECT_COMPLETE", state["project"]["current_step"])
        lane = state["changes"]["chg-a"]
        self.assertEqual("ACTIVE", lane["status"])
        self.assertEqual("07-detailed-design", lane["current_step"])
        self.assertEqual(CHANGE_STEPS[:2], lane["completed_steps"])
        self.assertEqual(1, len(lane["pending_approvals"]))
        backups = list((self.root / "workflow/evidence").glob("state-v2-backup-*.json"))
        self.assertEqual(1, len(backups))

        self.assertEqual(0, w.cmd_upgrade_state(args))
        self.assertEqual(1, len(list((self.root / "workflow/evidence").glob("state-v2-backup-*.json"))))

    # -- start-change dependency gate ----------------------------------------
    def test_start_change_accepts_delivered_dependency(self):
        state = self.state()
        state.update(self.accepted("chg-b"))
        self.write_state(state)
        self.roadmap(["| chg-a | chg-b |", "| chg-b | none |"])
        self.assertEqual(0, w.cmd_start_change(self.start_args("chg-a")))
        state = w.load_state()
        lane = state["changes"]["chg-a"]
        self.assertEqual("ACTIVE", lane["status"])
        self.assertEqual("05-feature-requirements", lane["current_step"])
        self.assertEqual(["chg-b"], lane["dependencies"]["required"])

    def test_start_change_rejects_active_and_not_started_dependencies(self):
        state = self.state(changes={"chg-b": self.lane(current="07-detailed-design",
                                                       completed=CHANGE_STEPS[:2])})
        self.write_state(state)
        self.roadmap(["| chg-a | chg-b; chg-c |", "| chg-b | none |", "| chg-c | none |"])
        with self.assertRaisesRegex(ValueError, "CHANGE_START_BLOCKED") as raised:
            w.cmd_start_change(self.start_args("chg-a"))
        message = str(raised.exception)
        self.assertIn("chg-b: ACTIVE@07-detailed-design", message)
        self.assertIn("chg-c: NOT_STARTED", message)

    def test_start_change_rejects_transitive_broken_chain(self):
        state = self.state()
        state.update(self.accepted("chg-b"))
        self.write_state(state)
        self.roadmap(["| chg-a | chg-b |", "| chg-b | chg-c |", "| chg-c | none |"])
        with self.assertRaisesRegex(ValueError, "BROKEN") as raised:
            w.cmd_start_change(self.start_args("chg-a"))
        self.assertIn("chg-a ← chg-b ← chg-c", str(raised.exception))

    def test_dependency_waiver_requires_user_fields_and_evidence(self):
        self.write_state(self.state())
        self.roadmap(["| chg-a | chg-b |", "| chg-b | none |"])
        with self.assertRaisesRegex(ValueError, "waiver requires"):
            w.cmd_start_change(self.start_args("chg-a", waive_dependency=["chg-b"],
                                               reason="", by="", evidence=""))
        with self.assertRaisesRegex(ValueError, "waiver evidence"):
            w.cmd_start_change(self.start_args("chg-a", waive_dependency=["chg-b"],
                                               reason="approved by owner", by="Owner",
                                               evidence="missing.json"))
        self.assertEqual(0, w.cmd_start_change(self.start_args(
            "chg-a", waive_dependency=["chg-b"], reason="approved by owner",
            by="Owner", evidence="check.log")))
        state = w.load_state()
        waiver = state["changes"]["chg-a"]["dependencies"]["waivers"][0]
        self.assertEqual("chg-b", waiver["dependency"])
        self.assertEqual("Owner", waiver["by"])

    def test_start_change_requires_upgraded_state(self):
        v1 = {"project_name": "test", "active_change_id": "",
              "completed_steps": PROJECT_STEPS, "current_step": "05-feature-requirements",
              "pending_approvals": [], "blocked_items": []}
        self.write_state(v1)
        with self.assertRaisesRegex(ValueError, "upgrade-state"):
            w.cmd_start_change(self.start_args("chg-a"))

    # -- lane-aware entry and approval ---------------------------------------
    def test_other_lane_pending_does_not_block_change_entry(self):
        project = self.project_lane()
        state = self.state(project=project, changes={
            "chg-a": self.lane(current="07-detailed-design", completed=CHANGE_STEPS[:2]),
            "chg-b": self.lane(current="05-feature-requirements",
                               pending=[{"step_id": "05-feature-requirements",
                                         "change_id": "chg-b"}]),
        })
        self.write_state(state)
        self.roadmap(["| chg-a | none |", "| chg-b | none |"])
        errors = w.check_entry("07-detailed-design", w.load_state(), "chg-a")
        self.assertEqual([], errors)

    def test_project_pending_blocks_every_change_lane(self):
        project = self.project_lane()
        project["pending_approvals"] = [{"step_id": "04-proposal-planning"}]
        state = self.state(project=project, changes={
            "chg-a": self.lane(current="05-feature-requirements"),
        })
        self.write_state(state)
        self.roadmap(["| chg-a | none |"])
        errors = w.check_entry("05-feature-requirements", w.load_state(), "chg-a")
        self.assertTrue(any("Pending approvals" in error for error in errors), errors)

    def test_approve_matches_change_id(self):
        state = self.state(changes={
            "chg-a": self.lane(current="07-detailed-design", completed=CHANGE_STEPS[:2],
                               pending=[{"step_id": "07-detailed-design",
                                         "change_id": "chg-a", "targets": []}]),
            "chg-b": self.lane(current="07-detailed-design", completed=CHANGE_STEPS[:2],
                               pending=[{"step_id": "07-detailed-design",
                                         "change_id": "chg-b", "targets": []}]),
        })
        self.write_state(state)
        self.assertEqual(0, w.cmd_approve(self.approve_args("07-detailed-design", "chg-a")))
        state = w.load_state()
        self.assertEqual([], state["changes"]["chg-a"]["pending_approvals"])
        self.assertEqual(1, len(state["changes"]["chg-b"]["pending_approvals"]))
        self.assertEqual("chg-a", state["approvals_history"][0]["change_id"])

    def test_reopen_only_supersedes_own_lane_approval(self):
        state = self.state(changes={
            "chg-a": self.lane(current="07-detailed-design", completed=CHANGE_STEPS[:2]),
            "chg-b": self.lane(current="07-detailed-design", completed=CHANGE_STEPS[:2]),
        })
        state["approvals_history"] = [
            {"step_id": "07-detailed-design", "change_id": "chg-a",
             "approver": "Owner", "approved_at": "2026-11-20", "evidence": "check.log", "targets": []},
            {"step_id": "07-detailed-design", "change_id": "chg-b",
             "approver": "Owner", "approved_at": "2026-11-20", "evidence": "check.log", "targets": []},
        ]
        self.write_state(state)
        args = type("Args", (), {"step": "07-detailed-design", "change_id": "chg-a",
                                 "reason": "design rework", "note": ""})()
        self.assertEqual(0, w.cmd_reopen(args))
        state = w.load_state()
        history = {item["change_id"]: item for item in state["approvals_history"]}
        self.assertTrue(history["chg-a"].get("superseded_at"))
        self.assertFalse(history["chg-b"].get("superseded_at"))
        self.assertEqual("07-detailed-design", state["changes"]["chg-a"]["current_step"])
        self.assertEqual(CHANGE_STEPS[:2], state["changes"]["chg-a"]["completed_steps"][:2])

    # -- lifecycle ------------------------------------------------------------
    def test_acceptance_marks_lane_accepted_and_releases_lease(self):
        state = self.state(changes={
            "chg-a": self.lane(current="10-acceptance-audit", completed=CHANGE_STEPS[:-1]),
        }, implementation_lease={"mode": "exclusive", "change_id": "chg-a",
                                 "acquired_at": "2026-11-23T00:00:00+00:00"})
        state["approvals_history"] = [{"step_id": "10-acceptance-audit",
                                       "change_id": "chg-a", "approver": "Owner",
                                       "approved_at": "2026-11-23", "evidence": "check.log",
                                       "targets": []}]
        self.write_state(state)
        evidence = {
            "step_id": "10-acceptance-audit", "change_id": "chg-a",
            "outputs": [{"path": "out.md", "status": "created", "required": True}],
            "methods": [{"skill": "verification-before-completion", "mode": "stage-scoped",
                         "summary": "verify", "questions": [], "alternatives": [],
                         "decisions": [], "open_questions": [], "artifact_section": "",
                         "evidence": "check.log"},
                        {"skill": "baseline-impact-classification", "mode": "stage-scoped",
                         "summary": "baseline", "questions": [], "alternatives": [],
                         "decisions": [], "open_questions": [],
                         "artifact_section": "out.md#baseline", "evidence": "out.md"}],
            "checks": [{"name": "gate", "kind": "automated", "status": "passed",
                        "command": "python check.py", "exit_code": 0, "log": "check.log"}],
            "approval": {"required": True, "status": "approved", "approver": "Owner",
                         "approved_at": "2026-11-23"},
        }
        ep = self.root / "acceptance-evidence.json"
        ep.write_text(json.dumps(evidence), encoding="utf-8")
        args = type("Args", (), {"step": "10-acceptance-audit", "change_id": "chg-a",
                                 "evidence": str(ep)})()

        # Method evidence requires an artifact section on the referenced file.
        methods = evidence["methods"]
        artifact = self.root / "out.md"
        artifact.write_text("# Baseline\n\n## baseline\n", encoding="utf-8")
        self.assertEqual(0, w.cmd_transition(args))
        state = w.load_state()
        lane = state["changes"]["chg-a"]
        self.assertEqual("ACCEPTED", lane["status"])
        self.assertEqual("CHANGE_COMPLETE", lane["current_step"])
        self.assertEqual("chg-a", state["completed_changes"][0]["change_id"])
        self.assertIsNone(state["implementation_lease"])

    def test_reset_state_clears_all_lanes(self):
        state = self.state(changes={"chg-a": self.lane()},
                           implementation_lease={"mode": "exclusive", "change_id": "chg-a"})
        self.write_state(state)
        args = type("Args", (), {"reason": "clean restart", "note": "", "clean": False})()
        self.assertEqual(0, w.cmd_reset_state(args))
        state = w.load_state()
        self.assertEqual({}, state["changes"])
        self.assertIsNone(state["implementation_lease"])

    # -- implementation lease ------------------------------------------------
    def method_entry(self, skill, artifact):
        return {"skill": skill, "mode": "stage-scoped", "summary": "test",
                "questions": [], "alternatives": [], "decisions": [],
                "open_questions": [], "artifact_section": artifact,
                "evidence": artifact.split("#")[0]}

    def design_evidence(self, change_id, name):
        design = f"openspec/changes/{change_id}/design.md"
        path = self.root / design
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Design\n\n## decisions\n\n### Implementation Slice\n\n- Owned paths: `app/**`\n- Integration paths: N/A\n",
                        encoding="utf-8")
        evidence = {
            "step_id": "07-detailed-design", "change_id": change_id,
            "outputs": [{"path": design, "status": "created", "required": True}],
            "methods": [
                self.method_entry(skill, f"{design}#decisions")
                for skill in ("brainstorming", "writing-plans",
                              "existing-code-impact-analysis")
            ],
            "checks": [{"name": "gate", "kind": "automated", "status": "passed",
                        "command": "python check.py", "exit_code": 0,
                        "log": "check.log"}],
            "approval": {"required": True, "status": "approved",
                         "approver": "Owner", "approved_at": "2026-11-23"},
        }
        path = self.root / name
        path.write_text(json.dumps(evidence), encoding="utf-8")
        return path

    def transition_args(self, step, change_id, evidence):
        return type("Args", (), {"step": step, "change_id": change_id,
                                 "evidence": str(evidence)})()

    def test_implementation_lease_excludes_other_lane_until_released(self):
        state = self.state(changes={
            "chg-a": self.lane(current="07-detailed-design", completed=CHANGE_STEPS[:2]),
            "chg-b": self.lane(current="07-detailed-design", completed=CHANGE_STEPS[:2]),
        })
        state["approvals_history"] = [
            {"step_id": "07-detailed-design", "change_id": cid, "approver": "Owner",
             "approved_at": "2026-11-23", "evidence": "check.log", "targets": []}
            for cid in ("chg-a", "chg-b")
        ]
        self.write_state(state)
        self.roadmap(["| chg-a | none |", "| chg-b | none |"])
        self.assertEqual(0, w.cmd_transition(self.transition_args(
            "07-detailed-design", "chg-a", self.design_evidence("chg-a", "a07.json"))))
        state = w.load_state()
        self.assertEqual("08-implementation-orchestrator",
                         state["changes"]["chg-a"]["current_step"])
        self.assertEqual("chg-a", state["implementation_lease"]["change_id"])
        with self.assertRaisesRegex(ValueError, "IMPLEMENTATION_LEASE_HELD"):
            w.cmd_transition(self.transition_args(
                "07-detailed-design", "chg-b", self.design_evidence("chg-b", "b07.json")))
        args = type("Args", (), {"change_id": "chg-a", "reason": "stop",
                                 "note": ""})()
        self.assertEqual(0, w.cmd_abandon_change(args))
        self.assertIsNone(w.load_state()["implementation_lease"])
        self.assertEqual(0, w.cmd_transition(self.transition_args(
            "07-detailed-design", "chg-b", self.design_evidence("chg-b", "b07b.json"))))
        self.assertEqual("chg-b", w.load_state()["implementation_lease"]["change_id"])

    def test_dependency_rechecked_at_stage_05_and_08(self):
        state = self.state(changes={
            "chg-a": self.lane(current="05-feature-requirements"),
        })
        state.update(self.accepted("chg-b"))
        self.write_state(state)
        self.roadmap(["| chg-a | chg-b |", "| chg-b | none |"])
        errors = w.check_entry("05-feature-requirements", w.load_state(), "chg-a")
        self.assertEqual([], errors)
        state = w.load_state()
        state["completed_changes"] = []
        state["transition_history"] = []
        self.write_state(state)
        errors = w.check_entry("05-feature-requirements", w.load_state(), "chg-a")
        self.assertTrue(any("Unmet proposal dependencies" in error for error in errors), errors)
        state = w.load_state()
        state["changes"]["chg-a"]["completed_steps"] = CHANGE_STEPS[:3]
        state["changes"]["chg-a"]["current_step"] = "08-implementation-orchestrator"
        self.write_state(state)
        errors = w.check_entry("08-implementation-orchestrator", w.load_state(), "chg-a")
        self.assertTrue(any("Unmet proposal dependencies" in error for error in errors), errors)

    def test_default_evidence_namespace(self):
        state = self.state(changes={"chg-a": self.lane()})
        self.assertEqual("workflow/evidence/chg-a/07-detailed-design.json",
                         w.default_evidence_path(state, "07-detailed-design", "chg-a"))
        self.assertEqual("workflow/evidence/project/04-proposal-planning.json",
                         w.default_evidence_path(state, "04-proposal-planning", None))
        self.assertEqual("workflow/evidence/chg-a/07-detailed-design-review.json",
                         w.default_review_packet_path(state, "07-detailed-design", "chg-a"))

    def test_skip_stage_advances_lane_and_writes_change_handoff(self):
        state = self.state(changes={
            "chg-a": self.lane(current="06-figma-design-review",
                               completed=["05-feature-requirements"]),
        })
        self.write_state(state)
        evidence = {
            "step_id": "06-figma-design-review", "change_id": "chg-a",
            "skip": True, "reason": "no UI",
            "checks": [{"name": "figma", "kind": "automated", "status": "passed",
                        "command": "python scripts/check-figma-audit.py --strict --no-ui",
                        "exit_code": 0, "log": "check.log"}],
        }
        ep = self.root / "skip.json"
        ep.write_text(json.dumps(evidence), encoding="utf-8")
        args = type("Args", (), {"step": "06-figma-design-review", "change_id": "chg-a",
                                 "evidence": str(ep)})()
        self.assertEqual(0, w.cmd_skip_stage(args))
        state = w.load_state()
        self.assertEqual("07-detailed-design", state["changes"]["chg-a"]["current_step"])
        self.assertIn("06-figma-design-review", state["changes"]["chg-a"]["completed_steps"])
        manifest = self.root / "workflow/handoffs/chg-a/06-figma-design-review--07-detailed-design.json"
        self.assertTrue(manifest.is_file())

    def test_migrate_change_stage_only_resets_lane(self):
        state = self.state(changes={
            "chg-a": self.lane(current="09-independent-verification",
                               completed=CHANGE_STEPS[:4]),
            "chg-b": self.lane(current="07-detailed-design", completed=CHANGE_STEPS[:2]),
        })
        self.write_state(state)
        args = type("Args", (), {"reason": "design rework", "note": "",
                                 "reset_step": ["07-detailed-design"],
                                 "change_id": "chg-a"})()
        self.assertEqual(0, w.cmd_migrate_state(args))
        state = w.load_state()
        self.assertEqual("07-detailed-design", state["changes"]["chg-a"]["current_step"])
        self.assertEqual(CHANGE_STEPS[:2], state["changes"]["chg-a"]["completed_steps"])
        self.assertEqual("07-detailed-design", state["changes"]["chg-b"]["current_step"])

    def test_next_change_starts_new_lane_after_acceptance(self):
        state = self.state(changes={
            "chg-a": self.lane(current="CHANGE_COMPLETE", completed=CHANGE_STEPS,
                               status="ACCEPTED"),
        })
        state.update(self.accepted("chg-a"))
        state["active_change_id"] = "chg-a"
        self.write_state(state)
        self.roadmap(["| chg-a | none |", "| chg-b | none |"])
        args = type("Args", (), {"change_id": "chg-b", "note": ""})()
        self.assertEqual(0, w.cmd_next_change(args))
        state = w.load_state()
        self.assertEqual("05-feature-requirements",
                         state["changes"]["chg-b"]["current_step"])
        self.assertEqual("chg-b", state["active_change_id"])
        self.assertEqual("chg-a", state["change_history"][-1]["completed_change_id"])

    def test_state_transaction_fails_closed_and_removes_lock(self):
        lock = self.root / (w.STATE.name + ".txn.lock")
        lock.write_text("held", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "lock timeout"):
            with w.state_transaction(timeout=0.3, interval=0.05):
                pass
        lock.unlink()
        with w.state_transaction(timeout=0.3, interval=0.05):
            self.assertTrue(lock.exists())
        self.assertFalse(lock.exists())

    def test_next_step_reports_each_lane(self):
        import contextlib, io
        spec_ns = importlib.util.spec_from_file_location(
            "next_step_v2", Path(__file__).with_name("next-step.py"))
        ns = importlib.util.module_from_spec(spec_ns)
        spec_ns.loader.exec_module(ns)
        original_state = ns.STATE
        ns.STATE = w.STATE
        state = self.state(changes={
            "chg-a": self.lane(current="07-detailed-design",
                               completed=CHANGE_STEPS[:2]),
            "chg-b": self.lane(current="05-feature-requirements",
                               pending=[{"step_id": "05-feature-requirements",
                                         "change_id": "chg-b"}]),
        })
        self.write_state(state)
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                result = ns.main()
        finally:
            ns.STATE = original_state
        text = out.getvalue()
        self.assertEqual(0, result)
        self.assertIn("CHANGE=chg-a", text)
        self.assertIn("NEXT_STEP=07-detailed-design", text)
        self.assertIn("CHANGE=chg-b STATUS=BLOCKED", text)
        self.assertIn("PENDING", text)

    def test_next_step_project_block_suppresses_change_lanes(self):
        import contextlib, io
        spec_ns = importlib.util.spec_from_file_location(
            "next_step_v2", Path(__file__).with_name("next-step.py"))
        ns = importlib.util.module_from_spec(spec_ns)
        spec_ns.loader.exec_module(ns)
        original_state = ns.STATE
        ns.STATE = w.STATE
        state = self.state(changes={
            "chg-a": self.lane(current="05-feature-requirements"),
        })
        state["project"]["pending_approvals"] = [
            {"step_id": "04-proposal-planning", "summary": "under review"}
        ]
        self.write_state(state)
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                result = ns.main()
        finally:
            ns.STATE = original_state
        text = out.getvalue()
        self.assertEqual(3, result)
        self.assertIn("PROJECT=BLOCKED", text)
        self.assertIn("PROJECT_LANE_BLOCKS_ALL_CHANGES=true", text)
        self.assertNotIn("NEXT_STEP", text)

    def test_footprint_disjoint_lanes_share_lease(self):
        state = self.state(changes={
            "chg-a": self.lane(current="07-detailed-design", completed=CHANGE_STEPS[:2]),
            "chg-b": self.lane(current="07-detailed-design", completed=CHANGE_STEPS[:2]),
        })
        state["approvals_history"] = [
            {"step_id": "07-detailed-design", "change_id": cid, "approver": "Owner",
             "approved_at": "2026-11-23", "evidence": "check.log", "targets": []}
            for cid in ("chg-a", "chg-b")
        ]
        self.write_state(state)
        self.roadmap(["| chg-a | none |", "| chg-b | none |"])
        originals = (w.project_strategy, w.slice_paths_for_change, w.declaration_valid)
        try:
            w.project_strategy = lambda: "module-packages"
            w.slice_paths_for_change = lambda cid: (
                {"owned": ["app/a/**"], "integration": []} if cid == "chg-a"
                else {"owned": ["app/b/**"], "integration": []}
            )
            w.declaration_valid = lambda cid: True
            self.assertEqual(0, w.cmd_transition(self.transition_args(
                "07-detailed-design", "chg-a", self.design_evidence("chg-a", "a07f.json"))))
            self.assertEqual(0, w.cmd_transition(self.transition_args(
                "07-detailed-design", "chg-b", self.design_evidence("chg-b", "b07f.json"))))
            lease = w.load_state()["implementation_lease"]
            self.assertEqual("shared", lease["mode"])
            self.assertEqual(["chg-a", "chg-b"], lease["change_ids"])
        finally:
            w.project_strategy, w.slice_paths_for_change, w.declaration_valid = originals

    def test_footprint_overlap_falls_back_to_exclusive(self):
        state = self.state(changes={
            "chg-a": self.lane(current="07-detailed-design", completed=CHANGE_STEPS[:2]),
            "chg-b": self.lane(current="07-detailed-design", completed=CHANGE_STEPS[:2]),
        })
        state["approvals_history"] = [
            {"step_id": "07-detailed-design", "change_id": cid, "approver": "Owner",
             "approved_at": "2026-11-23", "evidence": "check.log", "targets": []}
            for cid in ("chg-a", "chg-b")
        ]
        self.write_state(state)
        self.roadmap(["| chg-a | none |", "| chg-b | none |"])
        originals = (w.project_strategy, w.slice_paths_for_change, w.declaration_valid)
        try:
            w.project_strategy = lambda: "module-packages"
            w.slice_paths_for_change = lambda cid: (
                {"owned": ["app/**"], "integration": []} if cid == "chg-a"
                else {"owned": ["app/sales/**"], "integration": []}
            )
            w.declaration_valid = lambda cid: True
            self.assertEqual(0, w.cmd_transition(self.transition_args(
                "07-detailed-design", "chg-a", self.design_evidence("chg-a", "a07o.json"))))
            with self.assertRaisesRegex(ValueError, "IMPLEMENTATION_LEASE_HELD"):
                w.cmd_transition(self.transition_args(
                    "07-detailed-design", "chg-b", self.design_evidence("chg-b", "b07o.json")))
        finally:
            w.project_strategy, w.slice_paths_for_change, w.declaration_valid = originals

    def test_abandoning_accepted_change_blocks_downstream_start(self):
        state = self.state(changes={
            "chg-a": self.lane(current="CHANGE_COMPLETE", completed=CHANGE_STEPS,
                               status="ACCEPTED"),
        })
        state.update(self.accepted("chg-a"))
        state["active_change_id"] = "chg-a"
        self.write_state(state)
        args = type("Args", (), {"change_id": "chg-a", "reason": "withdraw", "note": ""})()
        self.assertEqual(0, w.cmd_abandon_change(args))
        self.roadmap(["| chg-a | none |", "| chg-b | chg-a |"])
        with self.assertRaisesRegex(ValueError, "ABANDONED") as raised:
            w.cmd_start_change(self.start_args("chg-b"))
        self.assertIn("chg-a", str(raised.exception))

    def test_unfilled_dependency_column_blocks_start_and_entry(self):
        layout = self.root / "docs/architecture/code-layout.json"
        layout.parent.mkdir(parents=True, exist_ok=True)
        layout.write_text(json.dumps({"version": 1, "strategy": "module-packages",
                                      "roots": {"backend": "server/", "frontend": "web/"}}),
                          encoding="utf-8")
        self.write_state(self.state())
        text = (
            "# Proposal Roadmap\n\n## Candidate Changes\n\n"
            "| Change ID | Primary Capability | Dependencies |\n|---|---|---|\n"
            "| chg-a | cap-a | PENDING |\n"
        )
        path = self.root / "docs/product/proposal-roadmap.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "not filled") as raised:
            w.cmd_start_change(self.start_args("chg-a"))
        self.assertIn("chg-a", str(raised.exception))
        self.write_state(self.state(changes={
            "chg-a": self.lane(current="05-feature-requirements"),
        }))
        errors = w.check_entry("05-feature-requirements", w.load_state(), "chg-a")
        self.assertTrue(any("not filled" in error for error in errors), errors)

    def test_entry_at_08_reports_another_lanes_lease(self):
        state = self.state(changes={
            "chg-a": self.lane(current="08-implementation-orchestrator",
                               completed=CHANGE_STEPS[:3]),
            "chg-b": self.lane(current="08-implementation-orchestrator",
                               completed=CHANGE_STEPS[:3]),
        }, implementation_lease={"mode": "exclusive", "change_id": "chg-a"})
        self.write_state(state)
        self.roadmap(["| chg-a | none |", "| chg-b | none |"])
        errors = w.check_entry("08-implementation-orchestrator", w.load_state(), "chg-b")
        self.assertTrue(any("IMPLEMENTATION_LEASE_HELD" in error for error in errors), errors)

    def test_abandon_change_v2_marks_lane_and_releases_lease(self):
        state = self.state(changes={
            "chg-a": self.lane(current="08-implementation-orchestrator",
                               completed=CHANGE_STEPS[:3]),
        }, implementation_lease={"mode": "exclusive", "change_id": "chg-a"})
        self.write_state(state)
        args = type("Args", (), {"change_id": "chg-a", "reason": "cancel", "note": ""})()
        self.assertEqual(0, w.cmd_abandon_change(args))
        state = w.load_state()
        self.assertEqual("ABANDONED", state["changes"]["chg-a"]["status"])
        self.assertEqual([], state["changes"]["chg-a"]["completed_steps"])
        self.assertIsNone(state["implementation_lease"])
        self.assertEqual("chg-a", state["abandoned_changes"][0]["change_id"])

    def test_migrate_project_step_with_active_lane_is_rejected(self):
        state = self.state(changes={"chg-a": self.lane()})
        self.write_state(state)
        args = type("Args", (), {"reason": "redo architecture", "note": "",
                                 "reset_step": ["03-project-architecture-baseline"],
                                 "change_id": None})()
        with self.assertRaisesRegex(ValueError, "ACTIVE"):
            w.cmd_migrate_state(args)



if __name__ == "__main__":
    unittest.main()
