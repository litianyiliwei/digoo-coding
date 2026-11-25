#!/usr/bin/env python3
"""Add or remove a Change from a capability's ``active_changes`` cell.

Usage: ``python scripts/update-capabilities.py --change <change-id> --action add|remove``

The capability is taken from the Change's roadmap main row or approved
amendment row (``Primary Capability``). Writes preserve the CSV header and all
other columns. Idempotent: adding a listed Change or removing an absent one is
a no-op.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
import gate_common as gm  # noqa: E402
import roadmap_deps  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
CAPABILITIES_REL = "docs/product/capabilities.csv"


def _primary_capability(change_id: str) -> str:
    roadmap = gm.parse_roadmap(root=ROOT)
    row = next((r for r in roadmap.get("rows", [])
                if roadmap_deps._row_change_id(r) == change_id), None)
    if row is None:
        row = next((r for r in roadmap.get("amendments", [])
                    if roadmap_deps._row_change_id(r) == change_id
                    and roadmap_deps._amendment_approved(r)), None)
    if row is None:
        raise ValueError(f"Change {change_id!r} is not in the roadmap main table or an approved amendment")
    wanted = "primary capability"
    for key, value in row.items():
        if " ".join((key or "").casefold().split()) == wanted:
            return (value or "").strip()
    raise ValueError("roadmap row is missing the Primary Capability column")


def _registry_path() -> Path:
    path = ROOT / CAPABILITIES_REL
    if not path.is_file():
        raise ValueError(f"{CAPABILITIES_REL} is missing")
    return path


def _header(path: Path) -> list[str]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.reader(handle)
        return [cell.strip() for cell in next(reader)]


def _read_rows(path: Path | None = None) -> list[dict]:
    path = path or _registry_path()
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [
            {(key or "").strip(): (value or "").strip() for key, value in row.items()}
            for row in csv.DictReader(handle)
        ]


def _active_tokens(value: str) -> list[str]:
    tokens = []
    for token in (value or "").replace("；", ";").split(";"):
        token = token.strip()
        if not token or token.upper().startswith("N/A") or token.upper() in {"PENDING", "NONE"}:
            continue
        if token not in tokens:
            tokens.append(token)
    return tokens


def update(change_id: str, action: str) -> int:
    if action not in ("add", "remove"):
        raise ValueError("action must be add or remove")
    capability = _primary_capability(change_id)
    path = _registry_path()
    rows = _read_rows(path)
    match = next((row for row in rows
                  if (row.get("capability_slug") or "").strip() == capability), None)
    if match is None:
        raise ValueError(f"Primary Capability {capability!r} not found in {CAPABILITIES_REL}")
    tokens = _active_tokens(match.get("active_changes") or "")
    if action == "add" and change_id not in tokens:
        tokens.append(change_id)
    if action == "remove" and change_id in tokens:
        tokens = [token for token in tokens if token != change_id]
    match["active_changes"] = ";".join(tokens) if tokens else "N/A"
    fieldnames = _header(path)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})
    os.replace(tmp, path)
    print(f"CAPABILITIES_UPDATED={capability} action={action} change={change_id} active={match['active_changes']}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--change", required=True)
    parser.add_argument("--action", required=True, choices=("add", "remove"))
    args = parser.parse_args(argv)
    try:
        return update(args.change, args.action)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
