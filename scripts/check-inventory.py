#!/usr/bin/env python3
"""Validate design inventory CSV structure, identifiers, and references."""
import csv, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
args = sys.argv[1:]
STRICT = "--strict" in args
NO_UI = "--no-ui" in args
change_id = None
reason = None
if "--change" in args:
    idx = args.index("--change")
    if idx + 1 >= len(args):
        print("Usage: check-inventory.py [--change <change-id>] [--no-ui --reason <reason>] [--strict]", file=sys.stderr); sys.exit(2)
    change_id = args[idx + 1]
    if not __import__("re").fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", change_id):
        print("Invalid change-id", file=sys.stderr); sys.exit(2)
    args = args[:idx] + args[idx+2:]
if "--reason" in args:
    idx = args.index("--reason")
    if idx + 1 >= len(args):
        print("--reason requires a value", file=sys.stderr); sys.exit(2)
    reason = args[idx+1]
    args = args[:idx] + args[idx+2:]
args = [a for a in args if a not in {"--strict", "--no-ui"}]
if args:
    print("Usage: check-inventory.py [--change <change-id>] [--no-ui --reason <reason>] [--strict]", file=sys.stderr); sys.exit(2)
if NO_UI and (not change_id or not reason or not reason.strip()):
    print("--no-ui requires --change <change-id> and --reason <reason>", file=sys.stderr); sys.exit(2)
if NO_UI and not STRICT:
    print("Use --strict with --no-ui so the explicit scope exception is checked", file=sys.stderr); sys.exit(2)
base = ROOT / "openspec/changes" / change_id / "design" if change_id else ROOT / "docs/design"
PAGE_FILE = base / "page-inventory.csv"
BLOCK_FILE = base / "block-inventory.csv"
EVENT_FILE = base / "interaction-map.csv"
ERRORS, WARNINGS = [], []

def read_csv(path, required):
    if not path.is_file():
        ERRORS.append(f"Missing file: {path.relative_to(ROOT)}")
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        missing = [x for x in required if x not in headers]
        if missing:
            ERRORS.append(f"{path.name}: missing columns: {', '.join(missing)}")
            return []
        rows = list(reader)
    if not rows and not NO_UI:
        WARNINGS.append(f"{path.name}: header only; no inventory rows yet")
    return rows

pages = read_csv(PAGE_FILE, ["page_id", "page_name", "route", "story_ids", "requirement_ids", "status"])
blocks = read_csv(BLOCK_FILE, ["block_id", "page_id", "block_name", "block_type", "description", "sort_order", "requirement_ids", "status"])
events = read_csv(EVENT_FILE, ["event_id", "page_id", "block_id", "element_id", "trigger", "input", "steps", "output", "error_behavior", "story_ids", "acceptance_ids", "status"])

def unique(rows, field, label):
    seen = set()
    for n, row in enumerate(rows, 2):
        value = (row.get(field) or "").strip()
        if not value:
            ERRORS.append(f"{label} line {n}: empty {field}")
        elif value in seen:
            ERRORS.append(f"{label} line {n}: duplicate {field}={value}")
        seen.add(value)
    return seen

page_ids = unique(pages, "page_id", PAGE_FILE.name)
block_ids = unique(blocks, "block_id", BLOCK_FILE.name)
event_ids = unique(events, "event_id", EVENT_FILE.name)
if NO_UI and (pages or blocks or events):
    ERRORS.append("--no-ui was declared but page/block/event rows exist; remove --no-ui or clear the inventories")
if NO_UI and (not PAGE_FILE.is_file() or not BLOCK_FILE.is_file() or not EVENT_FILE.is_file()):
    ERRORS.append("--no-ui still requires all three Change-scoped inventory files to exist")
for n, row in enumerate(pages, 2):
    pid = (row.get("page_id") or "").strip()
    if pid and not pid.startswith("PAGE-"):
        ERRORS.append(f"page-inventory.csv line {n}: {pid} should use PAGE- prefix")
    for field in ("page_name", "route", "story_ids", "requirement_ids", "status"):
        if not (row.get(field) or "").strip():
            ERRORS.append(f"page-inventory.csv line {n}: {field} is required; use N/A + reason when not applicable")
    if any(x in (row.get(field) or "") for field in row for x in ("TODO", "TBD", "待确认")):
        WARNINGS.append(f"page-inventory.csv line {n}: unresolved placeholder in row {pid!r}")
block_page = {}
for n, row in enumerate(blocks, 2):
    bid = (row.get("block_id") or "").strip()
    if bid and not bid.startswith("BLOCK-"):
        ERRORS.append(f"block-inventory.csv line {n}: {bid} should use BLOCK- prefix")
    pid = (row.get("page_id") or "").strip()
    if not pid:
        ERRORS.append(f"block-inventory.csv line {n}: page_id is required")
    elif pid not in page_ids:
        ERRORS.append(f"block-inventory.csv line {n}: page_id {pid!r} has no matching page row")
    elif bid:
        block_page[bid] = pid
    for field in ("block_id", "page_id", "block_name", "block_type", "description", "sort_order", "requirement_ids", "status"):
        if not (row.get(field) or "").strip():
            ERRORS.append(f"block-inventory.csv line {n}: {field} is required; use N/A + reason when not applicable")
    if any(x in (row.get(field) or "") for field in row for x in ("TODO", "TBD", "待确认")):
        WARNINGS.append(f"block-inventory.csv line {n}: unresolved placeholder in block {bid!r}")
blocked_pages = set(block_page.values())
for pid in page_ids:
    if pid and pid not in blocked_pages:
        ERRORS.append(f"page-inventory.csv: page {pid} has no functional block row; every page must declare its blocks in block-inventory.csv")
element_block = {}
for n, row in enumerate(events, 2):
    eid = (row.get("event_id") or "").strip()
    if eid and not eid.startswith("EVT-"):
        ERRORS.append(f"interaction-map.csv line {n}: {eid} should use EVT- prefix")
    pid = (row.get("page_id") or "").strip()
    if not pid:
        ERRORS.append(f"interaction-map.csv line {n}: page_id is required")
    elif pid not in page_ids:
        ERRORS.append(f"interaction-map.csv line {n}: page_id {pid!r} has no matching page row")
    bid = (row.get("block_id") or "").strip()
    if not bid:
        ERRORS.append(f"interaction-map.csv line {n}: block_id is required; every button/element must belong to a block")
    elif not bid.startswith("BLOCK-"):
        ERRORS.append(f"interaction-map.csv line {n}: {bid} should use BLOCK- prefix")
    elif bid not in block_ids:
        ERRORS.append(f"interaction-map.csv line {n}: block_id {bid!r} has no matching block row")
    elif pid and bid in block_page and block_page[bid] != pid:
        ERRORS.append(f"interaction-map.csv line {n}: block {bid} belongs to page {block_page[bid]}, not {pid}")
    elem = (row.get("element_id") or "").strip()
    if not elem:
        ERRORS.append(f"interaction-map.csv line {n}: element_id is required")
    elif not elem.startswith("ELEM-"):
        ERRORS.append(f"interaction-map.csv line {n}: {elem} should use ELEM- prefix")
    elif bid:
        prev = element_block.get(elem)
        if prev and prev != bid:
            ERRORS.append(f"interaction-map.csv line {n}: element {elem} appears in blocks {prev} and {bid}; an element belongs to exactly one block")
        else:
            element_block[elem] = bid
    for field in ("trigger", "steps", "output", "error_behavior", "story_ids", "acceptance_ids", "status"):
        if not (row.get(field) or "").strip():
            ERRORS.append(f"interaction-map.csv line {n}: {field} is required; use N/A + reason when not applicable")
    if any(x in (row.get(field) or "") for field in row for x in ("TODO", "TBD", "待确认")):
        WARNINGS.append(f"interaction-map.csv line {n}: unresolved placeholder in event {eid!r}")

for msg in WARNINGS: print("WARN:", msg)
for msg in ERRORS: print("ERROR:", msg)
if ERRORS or (STRICT and WARNINGS):
    print(f"Inventory check failed: {len(ERRORS)} error(s), {len(WARNINGS)} warning(s).")
    sys.exit(1)
if NO_UI:
    print(f"Inventory check passed: this Change explicitly has no UI. Reason: {reason}")
else:
    print(f"Inventory structural check passed: {len(pages)} page(s), {len(blocks)} block(s), {len(events)} event(s) in {base.relative_to(ROOT)}.")
