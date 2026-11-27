#!/usr/bin/env python3
"""Print the next workflow stage from the authoritative DAG. Read-only.

The stage DAG is read from process/WORKFLOW-STAGES.json (the single source of
truth); this script never mutates state. In v2 state it prints one line per
project/Change lane; v1 state keeps the original single NEXT_STEP output.
After finishing a stage, run the stage checks, record evidence and call
request-review; approve and transition only after the user explicitly approves
the pending stage (any unambiguous wording counts). Do not edit
workflow-state.json.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "workflow-state.json"
STAGES = json.loads((ROOT / "process/WORKFLOW-STAGES.json").read_text(encoding="utf-8"))["stages"]
CONTRACTS = json.loads((ROOT / "process/STEP-ARTIFACT-CONTRACTS.json").read_text(encoding="utf-8"))
CONTRACT_BY_SKILL = {row["skill"]: row for row in CONTRACTS["steps"]}
SKILLS_DIR = ROOT / ".claude/skills" if (ROOT / ".claude/skills").is_dir() else ROOT / ".agents/skills"
BY_ID = {stage["id"]: stage for stage in STAGES}
PROJECT_STEPS = [stage["id"] for stage in STAGES if stage["scope"] == "project"]
CHANGE_STEPS = [stage["id"] for stage in STAGES if stage["scope"] == "change"]


def emit(stage, cid=None):
    sid = stage["id"]
    p = ROOT / stage["prompt"]
    s = SKILLS_DIR / stage["skill"] / "SKILL.md"
    if not p.is_file() or not s.is_file():
        print(f"ERROR: missing prompt or skill for {sid}: {p} / {s}", file=sys.stderr)
        return 2
    if cid:
        print(f"CHANGE={cid}")
    print(f"NEXT_STEP={sid}")
    print(f"TITLE={stage['title']}")
    print(f"PROMPT={stage['prompt']}")
    print(f"SKILL={s.relative_to(ROOT)}")
    contract = CONTRACT_BY_SKILL.get(stage["skill"])
    if contract:
        profile = (CONTRACTS.get("input_policy") or {}).get("stage_profiles", {}).get(contract["step"])
        if profile and profile.get("lean"):
            print("LEAN_INPUTS=" + " ; ".join(profile["lean"]))
        print("REQUIRED_INPUTS=" + " ; ".join(contract["inputs"]))
        print("EXPECTED_OUTPUTS=" + " ; ".join(contract["outputs"]))
        print("NEXT_STAGE_INPUTS=" + " ; ".join(contract["next_inputs"]))
        print("HANDOFF_REPORT=templates/workflow/step-handoff-report.md")
    print("NOTE=Verify actual files, approvals and OpenSpec status before executing; this script only reads state.")
    if cid:
        evidence = f"workflow/evidence/{cid}/{sid}.json"
        print(f"NOTE=After finishing the stage, run the stage checks, record evidence and run: python scripts/workflow.py request-review --step {sid} --change-id {cid} --evidence {evidence} --summary \"<review summary>\"")
    else:
        evidence = f"workflow/evidence/project/{sid}.json"
        print(f"NOTE=After finishing the stage, run the stage checks, record evidence and run: python scripts/workflow.py request-review --step {sid} --evidence {evidence} --summary \"<review summary>\"")
    print(f"NOTE=End the turn after request-review. Only after the user explicitly approves {sid} (any unambiguous wording counts) run approve and then transition.")
    return 0


def main():
    if not STATE.exists():
        print(f"ERROR: missing {STATE}", file=sys.stderr); return 2
    try:
        state = json.loads(STATE.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: invalid workflow-state.json: {exc}", file=sys.stderr); return 2
    if str(state.get("state_schema_version")) == "2.0" and isinstance(state.get("project"), dict) and isinstance(state.get("changes"), dict):
        return main_v2(state)
    approvals = state.get("pending_approvals", [])
    blockers = state.get("blocked_items", [])
    if approvals or blockers:
        print("BLOCKED: workflow cannot advance automatically.")
        if approvals:
            print("Pending approvals:")
            for item in approvals: print(f" - {item}")
        if blockers:
            print("Blockers:")
            for item in blockers: print(f" - {item}")
        return 3
    completed = set(state.get("completed_steps", []))
    for stage in STAGES:
        sid = stage["id"]
        if sid in completed: continue
        missing = [d for d in stage["dependencies"] if d not in completed]
        if missing:
            print(f"WARNING: prerequisite stages not marked complete: {', '.join(missing)}")
        return emit(stage)
    print("ALL_STEPS_MARKED_COMPLETE")
    print("Verify final acceptance and archived OpenSpec state manually; no state was changed.")
    return 0


def main_v2(state):
    project = state["project"]
    changes = state.get("changes") or {}
    project_pending = list(project.get("pending_approvals") or [])
    project_blocked = list(project.get("blocked_items") or [])
    if project_pending or project_blocked:
        print(f"PROJECT=BLOCKED CURRENT_STEP={project.get('current_step')}")
        for item in project_pending:
            print(f" - PROJECT PENDING {item}")
        for item in project_blocked:
            print(f" - PROJECT BLOCKED {item}")
        print("PROJECT_LANE_BLOCKS_ALL_CHANGES=true")
        return 3
    if project.get("current_step") in PROJECT_STEPS:
        return emit(BY_ID[project["current_step"]])

    any_lane = False
    for cid, lane in sorted(changes.items()):
        if str(lane.get("status", "")).upper() == "ABANDONED":
            continue
        any_lane = True
        current = lane.get("current_step")
        pending = list(lane.get("pending_approvals") or [])
        blocked = list(lane.get("blocked_items") or [])
        if pending or blocked:
            print(f"CHANGE={cid} STATUS=BLOCKED CURRENT_STEP={current}")
            for item in pending:
                print(f" - CHANGE={cid} PENDING {item}")
            for item in blocked:
                print(f" - CHANGE={cid} BLOCKED {item}")
            continue
        if str(lane.get("status", "")).upper() == "ACCEPTED" or current not in CHANGE_STEPS:
            print(f"CHANGE={cid} STATUS={lane.get('status')} CURRENT_STEP={current}")
            continue
        result = emit(BY_ID[current], cid)
        if result:
            return result
    lease = state.get("implementation_lease")
    if lease:
        print("IMPLEMENTATION_LEASE=" + json.dumps(lease, ensure_ascii=False))
    if not any_lane and project.get("current_step") in ("PROJECT_COMPLETE", "ALL_STEPS_COMPLETE"):
        print("NO_ACTIVE_LANES")
        print("Start a Change with: python scripts/workflow.py start-change --change-id <change-id>")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
