#!/usr/bin/env python3
"""Check advisory summary-output line budgets from output_policy.summary_budgets.

Budgets are advisory by default: an over-budget file produces a warning and the
command exits 0. Use --strict to opt into enforcement (exit 1). This is a
context-hygiene signal, not a content-quality gate. It prevents a stage from
silently turning a summary/evidence file into a copy of the upstream baseline.
Missing files are allowed because a stage may not have run yet.
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
    contract_doc = None
    for rel in ("process/STEP-ARTIFACT-CONTRACTS.json", "docs/STEP-ARTIFACT-CONTRACTS.json"):
        candidate = root / rel
        try:
            contract_doc = json.loads(candidate.read_text(encoding="utf-8"))
            break
        except (FileNotFoundError, json.JSONDecodeError):
            continue
    if contract_doc is None:
        print("OUTPUT_CONTEXT_FAILED: STEP-ARTIFACT-CONTRACTS.json not found under process/ or docs/")
        return 1
    contract = contract_doc
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
    warnings: list[str] = []
    checked: list[str] = []
    if not declared:
        print(f"Output context check: stage {args.stage} declares no file outputs; nothing to check")
        return 0
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
            warnings.append(f"{rel}: {lines} lines exceeds advisory budget {max_lines}; reference upstream instead of copying")
        if isinstance(max_chars, int) and chars > max_chars:
            warnings.append(f"{rel}: {chars} chars exceeds advisory budget {max_chars}; reference upstream instead of copying")
    if args.strict and not checked:
        print("OUTPUT_CONTEXT_WARN: no summary outputs present for this stage/change")
    for warning in warnings:
        print("WARN:", warning)
    if warnings and args.strict:
        print(f"Output context check failed (--strict): {len(warnings)} over-budget error(s).")
        return 1
    if warnings:
        print(f"Output context advisory: {len(warnings)} over-budget warning(s); budgets are not a gate.")
    else:
        print(f"Output context passed: {len(checked)} summary file(s) within advisory budget.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
