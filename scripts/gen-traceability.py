#!/usr/bin/env python3
"""Generate openspec/changes/<change-id>/traceability.csv from test-cases and API-IO mappings.

Usage:
  python scripts/gen-traceability.py --change <change-id> [--out <path>] [--root <dir>]
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = ["source_type", "source_id", "target_type", "target_id", "relationship", "status", "evidence", "notes"]
TOKEN_SPLIT = re.compile(r"[;,/\s]+")


def split_ids(raw: str) -> list[str]:
    text = (raw or "").strip()
    if not text or text.upper().startswith(("N/A", "NONE", "PENDING", "TODO")):
        return []
    return [tok.strip() for tok in TOKEN_SPLIT.split(text) if tok.strip() and tok.strip() not in {"-", "—"}]


def collect_edges(change_dir: Path, change_id: str) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []
    seen: set[tuple[str, str, str, str, str]] = set()

    def add(src_type: str, src_id: str, tgt_type: str, tgt_id: str, rel: str, evidence: str, notes: str = "generated") -> None:
        key = (src_type, src_id, tgt_type, tgt_id, rel)
        if key in seen:
            return
        seen.add(key)
        edges.append({
            "source_type": src_type,
            "source_id": src_id,
            "target_type": tgt_type,
            "target_id": tgt_id,
            "relationship": rel,
            "status": "covered",
            "evidence": evidence,
            "notes": notes,
        })

    tc_path = change_dir / "design/test-cases.csv"
    if tc_path.is_file():
        with tc_path.open(newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                tid = (row.get("test_id") or "").strip()
                if not tid:
                    continue
                ev = f"openspec/changes/{change_id}/design/test-cases.csv#{tid}"
                acs = split_ids(row.get("ac_ids") or row.get("ac_id") or "")
                pages = split_ids(row.get("page_ids") or row.get("page_id") or "")
                apis = split_ids(row.get("api_ids") or row.get("operation_id") or "")
                ios = split_ids(row.get("io_ids") or row.get("io_id") or "")
                ifaces = split_ids(row.get("interface_ids") or row.get("interface_id") or "")
                for ac in acs:
                    add("AC", ac, "TEST", tid, "verified_by", ev)
                for page in pages:
                    add("PAGE", page, "TEST", tid, "verified_by", ev)
                for api in apis:
                    add("API", api, "TEST", tid, "verified_by", ev)
                    for ac in acs:
                        add("AC", ac, "API", api, "implemented_by", ev)
                    for page in pages:
                        add("PAGE", page, "API", api, "calls", ev)
                for io_id in ios:
                    add("IO", io_id, "TEST", tid, "verified_by", ev)
                for iface in ifaces:
                    add("INTERFACE", iface, "TEST", tid, "verified_by", ev)

    ui_actions_path = change_dir / "design/ui-actions.csv"
    if ui_actions_path.is_file():
        with ui_actions_path.open(newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                op = (row.get("operation_id") or "").strip()
                page = (row.get("page_id") or "").strip()
                elem = (row.get("element_id") or "").strip()
                if not op or op.upper().startswith(("N/A", "NONE", "PENDING", "TODO")):
                    continue
                ev = f"openspec/changes/{change_id}/design/ui-actions.csv#{elem or page or op}"
                if page:
                    add("PAGE", page, "API", op, "triggers", ev)
                if elem:
                    add("ELEM", elem, "API", op, "triggers", ev)

    api_io_path = change_dir / "design/api-io-mapping.csv"
    if api_io_path.is_file():
        with api_io_path.open(newline="", encoding="utf-8-sig") as f:
            for row in csv.DictReader(f):
                op = (row.get("operation_id") or row.get("operationId") or "").strip()
                if not op:
                    continue
                ev = f"openspec/changes/{change_id}/design/api-io-mapping.csv#{op}"
                for io_id in split_ids(row.get("io_ids") or row.get("io_id") or ""):
                    add("API", op, "IO", io_id, "invokes", ev)

    return edges


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--change", required=True, help="OpenSpec change-id")
    ap.add_argument("--out", help="Output CSV path (defaults to openspec/changes/<change-id>/traceability.csv)")
    ap.add_argument("--root", default=str(ROOT), help="Project root")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    change_dir = root / "openspec/changes" / args.change
    if not change_dir.is_dir():
        print(f"ERROR: change directory not found: {change_dir}", file=sys.stderr)
        return 2

    edges = collect_edges(change_dir, args.change)
    out_path = Path(args.out).resolve() if args.out else (change_dir / "traceability.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(edges)

    print(f"GENERATED_TRACEABILITY={out_path} edges={len(edges)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
