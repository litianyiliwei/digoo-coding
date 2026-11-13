#!/usr/bin/env python3
"""Check summary-output line budgets from output_policy.summary_budgets.

This is an output-context gate, not a content-quality gate. It prevents a stage
from silently turning a summary/evidence file into a copy of the upstream
baseline. Missing files are allowed because a stage may not have run yet.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH_TOKEN = re.compile(r"(?:docs|templates|openspec|workflow|prompts|scripts|design)/[A-Za-z0-9_\-./<>*]+")


def norm_path(value: str) -> str:
    return str(value).replace("\\", "/").strip().rstrip("。.）)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--stage", required=True)
    ap.add_argument("--change")
    ap.add_argument("--root", default=str(ROOT), help="Project root (defaults to this package)")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    contract = json.loads((root / "docs" / "STEP-ARTIFACT-CONTRACTS.json").read_text(encoding="utf-8"))
    budgets = (contract.get("output_policy") or {}).get("summary_budgets") or {}
    if not budgets:
        print("OUTPUT_CONTEXT_FAILED: output_policy.summary_budgets is missing")
        return 1
    row = next((r for r in contract.get("steps", []) if str(r.get("step")) == args.stage.split("-")[0]), None)
    if not row:
        print(f"OUTPUT_CONTEXT_FAILED: unknown stage {args.stage}")
        return 1
    declared = []
    for output in row.get("outputs", []):
        match = PATH_TOKEN.search(str(output))
        if match:
            path = norm_path(match.group(0))
            if args.change:
                path = path.replace("<change-id>", args.change)
            declared.append(path)
    errors: list[str] = []
    checked: list[str] = []
    for pattern, limits in budgets.items():
        rel = str(pattern).replace("<change-id>", args.change or "")
        rel = norm_path(rel)
        if declared and not any(rel == item or rel.endswith("/" + item.split("/")[-1]) for item in declared):
            continue
        path = root / rel
        if not path.is_file():
            continue
        checked.append(rel)
        text = path.read_text(encoding="utf-8", errors="replace")
        lines = text.count("\n") + (1 if text and not text.endswith("\n") else 0)
        chars = len(text)
        max_lines = limits.get("max_lines")
        stage_lines = (limits.get("stage_max_lines") or {}).get(args.stage.split("-")[0])
        if isinstance(stage_lines, int):
            max_lines = stage_lines
        max_chars = limits.get("max_chars")
        stage_chars = (limits.get("stage_max_chars") or {}).get(args.stage.split("-")[0])
        if isinstance(stage_chars, int):
            max_chars = stage_chars
        if isinstance(max_lines, int) and lines > max_lines:
            errors.append(f"{rel}: {lines} lines exceeds budget {max_lines}; reference upstream instead of copying")
        if isinstance(max_chars, int) and chars > max_chars:
            errors.append(f"{rel}: {chars} chars exceeds budget {max_chars}; reference upstream instead of copying")
    if args.strict and not checked:
        print("OUTPUT_CONTEXT_WARN: no summary outputs present for this stage/change")
    for error in errors:
        print("ERROR:", error)
    if errors:
        print(f"Output context check failed: {len(errors)} error(s).")
        return 1
    print(f"Output context passed: {len(checked)} summary file(s) within budget.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
