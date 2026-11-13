#!/usr/bin/env python3
"""Validate the Change cross-boundary interface catalog.

The catalog is the single inventory for HTTP APIs, native bridges, device
protocols, third-party APIs, asynchronous events and file/object boundaries.
It is separate from the backend IO catalog so API->IO semantics stay intact.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "interface_id", "interface_type", "source", "target", "protocol", "operation",
    "input_contract", "output_contract", "auth", "error_semantics", "timeout_ms",
    "retry_policy", "idempotency", "versioning", "test_ids", "owner", "notes",
]
ALLOWED_TYPES = {
    "HTTP_API", "NATIVE_BRIDGE", "DEVICE_PROTOCOL", "THIRD_PARTY_API",
    "ASYNC_EVENT", "FILE_OBJECT", "UI_EVENT",
}
PLACEHOLDERS = {"TODO", "TBD", "PENDING", "待确认", "待补充", "N/A", "<...>"}
ID_RE = re.compile(r"^IF-[A-Z0-9][A-Z0-9_-]*$")
TEST_RE = re.compile(r"^TEST-[A-Z0-9][A-Z0-9_-]*$")
SPLIT_RE = re.compile(r"[;,|]+")


def _split(value: str) -> list[str]:
    return [x.strip() for x in SPLIT_RE.split(value or "") if x.strip()]


def _placeholder(value: str) -> bool:
    text = (value or "").strip()
    return not text or text.upper() in PLACEHOLDERS or any(x in text for x in ("<TODO>", "TODO:", "TBD:", "待确认"))


def _read_csv(path: Path, required: list[str], errors: list[str]) -> list[dict[str, str]]:
    if not path.is_file():
        errors.append(f"missing file: {path}")
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            errors.append(f"{path}: missing header")
            return []
        missing = [c for c in required if c not in reader.fieldnames]
        if missing:
            errors.append(f"{path}: missing columns: {', '.join(missing)}")
            return []
        return list(reader)


def _openapi_ids(path: Path, errors: list[str]) -> tuple[set[str], str | None]:
    if not path.is_file():
        return set(), None
    text = path.read_text(encoding="utf-8-sig")
    ids = set(re.findall(r"(?m)^\s*operationId\s*:\s*['\"]?([A-Za-z0-9_.-]+)['\"]?\s*(?:#.*)?$", text))
    scope_match = re.search(r"(?m)^x-api-scope\s*:\s*['\"]?([A-Za-z_-]+)['\"]?\s*(?:#.*)?$", text)
    scope = scope_match.group(1).lower() if scope_match else None
    if ids and scope == "none":
        errors.append("OpenAPI has operationId entries but x-api-scope is still 'none'")
    if not ids and scope != "none":
        errors.append("OpenAPI has no operationId and does not declare x-api-scope: none")
    return ids, scope


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--change", required=True)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--require-native", action="store_true", help="Require at least one NATIVE_BRIDGE row")
    ap.add_argument("--root", default=str(ROOT), help="Project root (defaults to this package)")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", args.change):
        print("Invalid change-id", file=sys.stderr)
        return 2
    change_dir = root / "openspec" / "changes" / args.change
    catalog_path = change_dir / "design" / "interface-catalog.csv"
    design_path = change_dir / "design.md"
    openapi_path = change_dir / "api" / "openapi.yaml"
    test_path = change_dir / "design" / "test-cases.csv"
    trace_path = change_dir / "traceability.csv"

    errors: list[str] = []
    rows = _read_csv(catalog_path, REQUIRED, errors)
    if not rows:
        errors.append(f"{catalog_path}: catalog is empty; add interface rows or mark the Change as no-interface")
    openapi_ids, api_scope = _openapi_ids(openapi_path, errors)

    catalog_ids: dict[str, dict[str, str]] = {}
    for line, row in enumerate(rows, 2):
        iid = (row.get("interface_id") or "").strip()
        kind = (row.get("interface_type") or "").strip().upper()
        if not iid:
            errors.append(f"line {line}: interface_id is required")
            continue
        if not ID_RE.match(iid):
            errors.append(f"line {line}: interface_id must look like IF-<TYPE>-<NNN>, got {iid!r}")
        if iid in catalog_ids:
            errors.append(f"line {line}: duplicate interface_id {iid}")
        catalog_ids[iid] = row
        if kind not in ALLOWED_TYPES:
            errors.append(f"line {line}: interface_type {kind!r} is not one of {sorted(ALLOWED_TYPES)}")
        if args.strict:
            for field in REQUIRED:
                if field == "notes":
                    continue
                if _placeholder(row.get(field, "")):
                    errors.append(f"line {line}: {field} is missing/unresolved for {iid}")
        timeout = (row.get("timeout_ms") or "").strip()
        if timeout and (not timeout.isdigit() or int(timeout) < 0):
            errors.append(f"line {line}: timeout_ms must be a non-negative integer for {iid}")
        tests = _split(row.get("test_ids", ""))
        if not tests:
            errors.append(f"line {line}: test_ids requires at least one TEST ID for {iid}")
        for tid in tests:
            if not TEST_RE.match(tid):
                errors.append(f"line {line}: invalid TEST ID {tid!r} for {iid}")
        if kind == "HTTP_API":
            op = (row.get("operation") or "").strip()
            if not op or op not in openapi_ids:
                errors.append(f"line {line}: HTTP_API operation {op!r} not found in OpenAPI for {iid}")
            if api_scope == "none":
                errors.append(f"line {line}: HTTP_API row is not allowed when x-api-scope: none ({iid})")

    for oid in sorted(openapi_ids):
        if not any((row.get("interface_type") or "").strip().upper() == "HTTP_API"
                   and (row.get("operation") or "").strip() == oid for row in rows):
            errors.append(f"OpenAPI operationId {oid!r} has no HTTP_API row in interface-catalog.csv")

    if args.require_native and not any((row.get("interface_type") or "").strip().upper() == "NATIVE_BRIDGE" for row in rows):
        errors.append("--require-native: no NATIVE_BRIDGE row found")

    # Test-case coverage: each interface must have at least one test row pointing at it.
    test_rows = _read_csv(test_path, ["test_id", "interface_ids"], errors)
    test_ids = {(row.get("test_id") or "").strip() for row in test_rows if (row.get("test_id") or "").strip()}
    referenced_interfaces: set[str] = set()
    for line, row in enumerate(test_rows, 2):
        for iid in _split(row.get("interface_ids", "")):
            referenced_interfaces.add(iid)
            if iid not in catalog_ids:
                errors.append(f"test-cases.csv line {line}: interface_id {iid!r} not found in interface-catalog.csv")
    for iid, row in catalog_ids.items():
        for tid in _split(row.get("test_ids", "")):
            if tid not in test_ids:
                errors.append(f"{iid}: test_ids references missing test case {tid}")
        if iid not in referenced_interfaces:
            errors.append(f"{iid}: no test-cases.csv row references interface_ids={iid}")

    # Traceability: interface -> AC/TEST must be registered.
    trace_rows = _read_csv(trace_path, ["source_type", "source_id"], errors)
    traced = {(row.get("source_id") or "").strip() for row in trace_rows
              if (row.get("source_type") or "").strip().upper() == "INTERFACE"}
    for iid in catalog_ids:
        if iid not in traced:
            errors.append(f"{iid}: traceability.csv has no INTERFACE row")

    # The design section must exist and point at the catalog.
    if not design_path.is_file():
        errors.append(f"missing {design_path}")
    else:
        design_text = design_path.read_text(encoding="utf-8")
        if "### 接口边界清单" not in design_text:
            errors.append("design.md missing ### 接口边界清单")
        if "interface-catalog.csv" not in design_text:
            errors.append("design.md ### 接口边界清单 must reference interface-catalog.csv")
        boundary = design_text.split("### 接口边界清单", 1)[1].split("### ", 1)[0] if "### 接口边界清单" in design_text else ""
        if "第三方" in boundary and not boundary.strip().upper().startswith("N/A"):
            if not any((row.get("interface_type") or "").strip().upper() == "THIRD_PARTY_API" for row in rows):
                errors.append("design.md 接口边界清单 mentions 第三方 but interface-catalog.csv has no THIRD_PARTY_API row")

    for error in errors:
        print("ERROR:", error)
    if errors:
        print(f"Interface catalog check failed: {len(errors)} error(s).")
        return 1
    print(f"Interface catalog passed: {len(catalog_ids)} interface(s), "
          f"{len([r for r in catalog_ids.values() if (r.get('interface_type') or '').strip().upper() == 'NATIVE_BRIDGE'])} native bridge(s), "
          f"{len(openapi_ids)} OpenAPI operation(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
