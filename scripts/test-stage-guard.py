#!/usr/bin/env python3
"""Regression tests for the PreToolUse stage-boundary hook."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / ".claude/hooks/stage-boundary-guard.py"
STAGES = ["01-project-bootstrap", "02-requirements-analysis", "03-project-architecture-baseline",
          "04-proposal-planning", "05-feature-requirements", "06-figma-design-review",
          "07-detailed-design", "08-implementation-orchestrator", "09-independent-verification",
          "10-acceptance-audit"]


def run_case(root: Path, current: str, completed: list[str], path: str, pending: list | None = None) -> str:
    state = {
        "project_name": "test",
        "active_change_id": "demo-change",
        "completed_steps": completed,
        "current_step": current,
        "pending_approvals": pending or [],
        "blocked_items": [],
        "last_completed_outputs": [],
    }
    (root / "workflow-state.json").write_text(json.dumps(state), encoding="utf-8")
    payload = {"tool_name": "Write", "tool_input": {"file_path": path}, "cwd": str(root)}
    result = subprocess.run([sys.executable, str(HOOK)], input=json.dumps(payload), capture_output=True, text=True)
    return "deny" if "permissionDecision" in result.stdout else "allow"


def make_root() -> Path:
    root = Path(tempfile.mkdtemp())
    docs = root / "docs"
    docs.mkdir()
    shutil.copy(ROOT / "docs/WORKFLOW-STAGES.json", docs / "WORKFLOW-STAGES.json")
    shutil.copy(ROOT / "docs/STEP-ARTIFACT-CONTRACTS.json", docs / "STEP-ARTIFACT-CONTRACTS.json")
    return root


def main() -> int:
    base = ["01-project-bootstrap", "02-requirements-analysis", "03-project-architecture-baseline", "04-proposal-planning"]
    cases = [
        ("05-feature-requirements", base, "openspec/changes/demo-change/design.md", None, "deny"),
        ("05-feature-requirements", base, "openspec/changes/demo-change/tasks.md", None, "allow"),
        ("05-feature-requirements", base, "openspec/changes/demo-change/design/figma-audit.md", None, "deny"),
        ("05-feature-requirements", base, "docs/product/workflows.md", None, "deny"),
        ("06-figma-design-review", base + ["05-feature-requirements"], "openspec/changes/demo-change/design.md", None, "deny"),
        ("06-figma-design-review", base + ["05-feature-requirements"], "openspec/changes/demo-change/design/figma-layout.csv", None, "allow"),
        ("07-detailed-design", base + ["05-feature-requirements", "06-figma-design-review"], "openspec/changes/demo-change/design.md", None, "allow"),
        ("07-detailed-design", base + ["05-feature-requirements", "06-figma-design-review"], "openspec/changes/demo-change/design/baseline-impact.md", None, "allow"),
        ("08-implementation-orchestrator", base + ["05-feature-requirements", "06-figma-design-review", "07-detailed-design"], "openspec/changes/demo-change/tasks.md", None, "allow"),
        ("05-feature-requirements", base, "openspec/changes/demo-change/design.md", [{"step_id": "05-feature-requirements"}], "deny"),
        ("01-project-bootstrap", [], "workflow-state.json", None, "deny"),
    ]
    failures = []
    for current, completed, path, pending, expected in cases:
        root = make_root()
        try:
            actual = run_case(root, current, completed, path, pending)
        finally:
            shutil.rmtree(root, ignore_errors=True)
        if actual != expected:
            failures.append(f"{current} {path}: expected {expected}, got {actual}")
    if failures:
        print("STAGE_GUARD_FAILED")
        for failure in failures:
            print(" - " + failure)
        return 1
    print(f"STAGE_GUARD_PASSED ({len(cases)} cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
