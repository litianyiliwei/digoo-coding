#!/usr/bin/env python3
"""Regression tests for scripts/agent-context.py lean bundle and budget."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "agent-context.py"


def contract(max_files: int) -> dict:
    return {
        "steps": [
            {
                "step": "07",
                "skill": "detailed-design",
                "prompt": "prompts/07-detailed-design.md",
                "title": "详细设计",
                "scope": "单个功能 Change",
                "inputs": ["完整契约输入"],
                "outputs": ["openspec/changes/<change-id>/design.md"],
                "next_inputs": ["设计契约"],
                "approval": "技术负责人",
                "gate": "check-design-sections.py",
            }
        ],
        "input_policy": {
            "stage_profiles": {
                "07": {
                    "lean": [
                        "docs/product/BASELINE-BRIEF.md",
                        "openspec/changes/<change-id>/design.md",
                    ],
                    "on_demand": ["docs/architecture/system-context.md"],
                    "max_files": max_files,
                }
            }
        },
    }


def run(root: Path, stage: str = "07") -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPT), "--root", str(root), "--stage", stage]
    if stage != "02":
        command.extend(["--change", "demo"])
    return subprocess.run(
        command,
        capture_output=True, text=True,
    )


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "process").mkdir(parents=True, exist_ok=True)
        (root / "docs").mkdir(parents=True)
        (root / "process" / "STEP-ARTIFACT-CONTRACTS.json").write_text(
            json.dumps(contract(2), ensure_ascii=False), encoding="utf-8"
        )
        (root / "docs" / "product").mkdir(parents=True)
        (root / "docs" / "product" / "BASELINE-BRIEF.md").write_text("# brief\n", encoding="utf-8")
        (root / "openspec" / "changes" / "demo").mkdir(parents=True)
        (root / "openspec" / "changes" / "demo" / "design.md").write_text("# design\n", encoding="utf-8")

        ok = run(root)
        if ok.returncode != 0 or "Lean inputs" not in ok.stdout or "Budget: 2/2 lean read groups" not in ok.stdout:
            failures.append("lean bundle should pass within budget: " + ok.stdout + ok.stderr)

        (root / "process" / "STEP-ARTIFACT-CONTRACTS.json").write_text(
            json.dumps(contract(1), ensure_ascii=False), encoding="utf-8"
        )
        over = run(root)
        if over.returncode == 0 or "CONTEXT_BUDGET_EXCEEDED" not in over.stdout:
            failures.append("lean bundle should fail over budget: " + over.stdout)

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "process").mkdir(parents=True, exist_ok=True)
        (root / "docs" / "product").mkdir(parents=True)
        stage02 = {
            "steps": [{
                "step": "02", "skill": "requirements-analysis", "prompt": "prompts/02-requirements-analysis.md",
                "title": "Requirements analysis", "scope": "project-level", "inputs": ["project goals"],
                "outputs": ["docs/product/requirements-analysis.md"], "next_inputs": [], "approval": "owner", "gate": "checks"
            }],
            "input_policy": {"stage_profiles": {"02": {
                "lean": ["docs/product/BASELINE-BRIEF.md (when present)", "docs/product/open-questions.md (if present)", "User-provided project goal"],
                "on_demand": ["docs/product/reference-research.md when prior research needs reconciliation"],
                "max_files": 8
            }}}
        }
        (root / "process" / "STEP-ARTIFACT-CONTRACTS.json").write_text(
            json.dumps(stage02, ensure_ascii=False), encoding="utf-8"
        )
        optional = run(root, "02")
        if (optional.returncode != 0 or "Budget: 3/8 lean read groups" not in optional.stdout
                or "[OPTIONAL; absent]" not in optional.stdout):
            failures.append("Stage 02 should allow not-yet-created optional baseline files: " + optional.stdout + optional.stderr)

    if failures:
        for failure in failures:
            print("FAIL:", failure)
        return 1
    print("Agent context regression tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
