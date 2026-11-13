#!/usr/bin/env python3
"""Validate a stage evidence file's method block against the method policy."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from method_evidence import validate_methods

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--step", required=True)
    ap.add_argument("--evidence", required=True)
    ap.add_argument("--root", default=str(ROOT), help="Project root (defaults to this package)")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    p = Path(args.evidence)
    p = (root / p).resolve() if not p.is_absolute() else p.resolve()
    try:
        evidence = json.loads(p.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - CLI error surface
        print(f"METHOD_EVIDENCE_FAILED: cannot read evidence: {exc}")
        return 1
    if evidence.get("step_id") != args.step:
        print(f"METHOD_EVIDENCE_FAILED: evidence.step_id must be {args.step}")
        return 1
    errors = validate_methods(evidence, args.step, root)
    if errors:
        print("METHOD_EVIDENCE_FAILED")
        for error in errors:
            print(" - " + error)
        return 1
    print(f"METHOD_EVIDENCE_PASSED={args.step}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
