#!/usr/bin/env python3
"""Print the next workflow stage from the authoritative DAG. Read-only.

The stage DAG is read from docs/WORKFLOW-STAGES.json (the single source of
truth); this script never mutates state. After finishing a stage, record
evidence and run scripts/workflow.py transition — do not edit workflow-state.json.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "workflow-state.json"
STAGES = json.loads((ROOT / "docs/WORKFLOW-STAGES.json").read_text(encoding="utf-8"))["stages"]
CONTRACTS = json.loads((ROOT / "docs/STEP-ARTIFACT-CONTRACTS.json").read_text(encoding="utf-8"))
CONTRACT_BY_SKILL = {row["skill"]: row for row in CONTRACTS["steps"]}
SKILLS_DIR = ROOT / ".claude/skills" if (ROOT / ".claude/skills").is_dir() else ROOT / ".agents/skills"

def main():
    if not STATE.exists():
        print(f"ERROR: missing {STATE}", file=sys.stderr); return 2
    try:
        state = json.loads(STATE.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"ERROR: invalid workflow-state.json: {exc}", file=sys.stderr); return 2
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
        p = ROOT / stage["prompt"]
        s = SKILLS_DIR / stage["skill"] / "SKILL.md"
        if not p.is_file() or not s.is_file():
            print(f"ERROR: missing prompt or skill for {sid}: {p} / {s}", file=sys.stderr); return 2
        print(f"NEXT_STEP={sid}")
        print(f"TITLE={stage['title']}")
        print(f"PROMPT={stage['prompt']}")
        print(f"SKILL={s.relative_to(ROOT)}")
        contract = CONTRACT_BY_SKILL.get(stage["skill"])
        if contract:
            print("REQUIRED_INPUTS=" + " ; ".join(contract["inputs"]))
            print("EXPECTED_OUTPUTS=" + " ; ".join(contract["outputs"]))
            print("NEXT_STAGE_INPUTS=" + " ; ".join(contract["next_inputs"]))
            print("HANDOFF_REPORT=templates/workflow/step-handoff-report.md")
        print("NOTE=Verify actual files, approvals and OpenSpec status before executing; this script only reads state.")
        print(f"NOTE=After finishing the stage, record evidence and run: python scripts/workflow.py transition --step {sid} --evidence workflow/evidence/{sid}.json")
        return 0
    print("ALL_STEPS_MARKED_COMPLETE")
    print("Verify final acceptance and archived OpenSpec state manually; no state was changed.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
