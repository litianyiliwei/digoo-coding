#!/usr/bin/env python3
"""Validate traceability CSV required columns and duplicate edges."""
import csv, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
raw_args = sys.argv[1:]
strict = "--strict" in raw_args
args = [arg for arg in raw_args if arg != "--strict"]
if "--file" in args:
    i = args.index("--file")
    if i + 1 >= len(args):
        print("Usage: check-traceability.py --file <csv> [--strict]", file=sys.stderr); sys.exit(2)
    candidate = Path(args[i + 1])
    if not candidate.is_absolute():
        # Prefer current working directory, then package/project root.
        candidate = candidate if candidate.exists() else ROOT / candidate
    args = args[:i] + args[i+2:]
    path = candidate
else:
    print("Usage: check-traceability.py --file <csv> [--strict]", file=sys.stderr); sys.exit(2)
if args:
    print("Usage: check-traceability.py --file <csv> [--strict]", file=sys.stderr); sys.exit(2)
if not path.is_file():
    print(f"ERROR: missing traceability file: {path}", file=sys.stderr); sys.exit(1)
required = ["source_type", "source_id", "target_type", "target_id", "relationship", "status", "evidence", "notes"]
with path.open(newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    if not reader.fieldnames or any(c not in reader.fieldnames for c in required):
        print("ERROR: traceability.csv columns must include: " + ", ".join(required), file=sys.stderr); sys.exit(1)
    rows = list(reader)
errors, warnings, seen = [], [], set()
if not rows: warnings.append(f"{path.name} is header-only; no trace links entered yet")
for line, row in enumerate(rows, 2):
    missing = [c for c in required if not (row.get(c) or "").strip()]
    if missing: errors.append(f"line {line}: blank fields: {', '.join(missing)}")
    status = (row.get("status") or "").strip().lower()
    if status not in {"covered", "n/a", "gap", "pending"}:
        errors.append(f"line {line}: status must be covered, n/a, gap, or pending; got {status!r}")
    edge = tuple((row.get(c) or "").strip() for c in ["source_type", "source_id", "target_type", "target_id", "relationship"])
    if edge in seen: errors.append(f"line {line}: duplicate traceability edge {edge}")
    seen.add(edge)
    if status == "n/a" and not (row.get("notes") or "").strip(): errors.append(f"line {line}: N/A requires a reason in notes")
    if status == "gap": warnings.append(f"line {line}: unresolved traceability gap {edge}")
for m in warnings: print("WARN:", m)
for m in errors: print("ERROR:", m)
if errors or (strict and warnings):
    print(f"Traceability check failed: {len(errors)} error(s), {len(warnings)} warning(s).")
    sys.exit(1)
print(f"Traceability structural check passed: {len(rows)} edge(s) in {path}.")
