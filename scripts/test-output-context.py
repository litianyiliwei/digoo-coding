#!/usr/bin/env python3
"""Regression tests for scripts/check-output-context.py."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check-output-context.py"


def run(root: Path, stage: str, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--root", str(root), "--stage", stage, *extra],
        capture_output=True, text=True,
    )


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "docs").mkdir(parents=True)
        contract = {
            "output_policy": {
                "summary_budgets": {
                    "docs/product/BASELINE-BRIEF.md": {"max_lines": 60},
                    "openspec/changes/<change-id>/design.md": {"max_lines": 400, "stage_max_lines": {"05": 60}},
                }
            },
            "steps": [
                {"step": "02", "outputs": ["docs/product/BASELINE-BRIEF.md"]},
                {"step": "05", "outputs": ["openspec/changes/<change-id>/design.md"]},
                {"step": "07", "outputs": ["openspec/changes/<change-id>/design.md"]},
            ],
        }
        (root / "docs" / "STEP-ARTIFACT-CONTRACTS.json").write_text(
            json.dumps(contract, ensure_ascii=False), encoding="utf-8"
        )
        (root / "docs" / "product").mkdir(parents=True)
        brief = root / "docs" / "product" / "BASELINE-BRIEF.md"
        brief.write_text("# brief\n" + "\n".join(f"- item {i}" for i in range(10)) + "\n", encoding="utf-8")
        ok = run(root, "02")
        if ok.returncode != 0:
            failures.append("small summary should pass: " + ok.stdout + ok.stderr)

        brief.write_text("# brief\n" + "\n".join(f"- item {i}" for i in range(70)) + "\n", encoding="utf-8")
        over = run(root, "02")
        if over.returncode == 0 or "exceeds budget" not in over.stdout:
            failures.append("oversized summary should fail: " + over.stdout)

        design = root / "openspec" / "changes" / "demo" / "design.md"
        design.parent.mkdir(parents=True)
        design.write_text("## design\n" + "\n".join(f"- line {i}" for i in range(500)) + "\n", encoding="utf-8")
        design_over = run(root, "07", "--change", "demo")
        if design_over.returncode == 0 or "exceeds budget" not in design_over.stdout:
            failures.append("oversized design.md should fail: " + design_over.stdout)

        stage_over = run(root, "05", "--change", "demo")
        if stage_over.returncode == 0 or "exceeds budget" not in stage_over.stdout:
            failures.append("stage 05 design.md stage override should fail: " + stage_over.stdout)

    if failures:
        for failure in failures:
            print("FAIL:", failure)
        return 1
    print("Output context regression tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
