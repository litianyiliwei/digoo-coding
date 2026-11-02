#!/usr/bin/env python3
"""Ensure every OpenAPI operationId maps to concrete I/O operations and catalog entries."""
import argparse, csv, re, sys
from pathlib import Path

REQUIRED_MAPPING = ["operation_id", "sequence", "io_id", "required", "transaction_scope", "failure_handling", "test_ids", "no_io_reason", "approved_by", "notes"]
REQUIRED_CATALOG = ["io_id", "io_type", "resource_or_client", "operation", "input_contract", "output_contract", "transaction_or_consistency", "timeout_ms", "retry_policy", "idempotency", "errors_and_mapping", "observability", "test_ids", "notes"]
PLACEHOLDERS = {"TODO", "TBD", "PENDING", "待确认", "待补充", "N/A"}

def read_csv(path, required, errors):
    if not path.is_file():
        errors.append(f"Missing file: {path}")
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            errors.append(f"{path.name}: missing header")
            return []
        missing = [c for c in required if c not in reader.fieldnames]
        if missing:
            errors.append(f"{path.name}: missing columns: {', '.join(missing)}")
            return []
        return list(reader)

def parse_operation_ids(path, errors):
    if not path.is_file():
        errors.append(f"OpenAPI file not found: {path}")
        return [], None
    text = path.read_text(encoding="utf-8-sig")
    # OpenAPI YAML operationId scalar syntax; use OpenAPI lint separately for full YAML/schema validity.
    ids = re.findall(r"(?m)^\s*operationId\s*:\s*['\"]?([A-Za-z0-9_.-]+)['\"]?\s*(?:#.*)?$", text)
    scope_match = re.search(r"(?m)^x-api-scope\s*:\s*['\"]?([A-Za-z_-]+)['\"]?\s*(?:#.*)?$", text)
    api_scope = scope_match.group(1).lower() if scope_match else None
    if not ids and api_scope != "none":
        errors.append(f"No operationId found in OpenAPI: {path}. If this Change intentionally adds/modifies no API, declare x-api-scope: none.")
    if ids and api_scope == "none":
        errors.append("OpenAPI has operationId entries but x-api-scope is still 'none'; set x-api-scope: defined or remove the extension.")
    seen, dup = set(), set()
    for oid in ids:
        if oid in seen: dup.add(oid)
        seen.add(oid)
    if dup: errors.append("Duplicate OpenAPI operationId(s): " + ", ".join(sorted(dup)))
    return ids, api_scope

def is_placeholder(value):
    text = (value or "").strip()
    return not text or text.upper() in PLACEHOLDERS or any(x in text for x in ("<TODO>", "TODO:", "TBD:", "待确认"))

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("openapi")
    ap.add_argument("mapping")
    ap.add_argument("catalog")
    ap.add_argument("--strict", action="store_true", help="reject placeholders, missing evidence fields and unused catalog rows")
    args = ap.parse_args()
    errors, warnings = [], []
    operation_ids, api_scope = parse_operation_ids(Path(args.openapi), errors)
    mappings = read_csv(Path(args.mapping), REQUIRED_MAPPING, errors)
    catalog = read_csv(Path(args.catalog), REQUIRED_CATALOG, errors)

    catalog_by_id = {}
    for line, row in enumerate(catalog, 2):
        ioid = (row.get("io_id") or "").strip()
        if not ioid:
            errors.append(f"{Path(args.catalog).name} line {line}: io_id is required")
            continue
        if ioid in catalog_by_id:
            errors.append(f"{Path(args.catalog).name} line {line}: duplicate io_id {ioid}")
        catalog_by_id[ioid] = row
        if ioid == "NO_IO_EXCEPTION":
            errors.append("NO_IO_EXCEPTION is a mapping-only marker, not a catalog I/O operation")
        if args.strict:
            for field in REQUIRED_CATALOG:
                value = (row.get(field) or "").strip()
                # notes may intentionally be blank; require explicit N/A + rationale for other fields instead.
                if field != "notes" and is_placeholder(value):
                    errors.append(f"{Path(args.catalog).name} line {line}: {field} is missing/unresolved for {ioid}")

    rows_by_api = {}
    referenced_io = set()
    seen_api_sequence = set()
    for line, row in enumerate(mappings, 2):
        oid = (row.get("operation_id") or "").strip()
        ioid = (row.get("io_id") or "").strip()
        if not oid:
            errors.append(f"{Path(args.mapping).name} line {line}: operation_id is required")
            continue
        if oid not in operation_ids:
            errors.append(f"{Path(args.mapping).name} line {line}: operation_id {oid!r} not found in OpenAPI")
        seq = (row.get("sequence") or "").strip()
        try:
            seq_int = int(seq)
            if seq_int < 1: raise ValueError
        except ValueError:
            errors.append(f"{Path(args.mapping).name} line {line}: sequence must be a positive integer")
            seq_int = -1
        key = (oid, seq_int, ioid)
        if key in seen_api_sequence:
            errors.append(f"{Path(args.mapping).name} line {line}: duplicate operation_id + sequence + io_id {key}")
        seen_api_sequence.add(key)
        rows_by_api.setdefault(oid, []).append(row)
        if ioid == "NO_IO_EXCEPTION":
            reason = (row.get("no_io_reason") or "").strip()
            approver = (row.get("approved_by") or "").strip()
            if is_placeholder(reason) or is_placeholder(approver):
                errors.append(f"{Path(args.mapping).name} line {line}: NO_IO_EXCEPTION requires no_io_reason and approved_by")
            elif args.strict and any(x in reason.upper() for x in ("TODO", "TBD", "PENDING")):
                errors.append(f"{Path(args.mapping).name} line {line}: unresolved NO_IO_EXCEPTION reason")
            continue
        if not ioid:
            errors.append(f"{Path(args.mapping).name} line {line}: every operationId must map to at least one io_id")
            continue
        if ioid not in catalog_by_id:
            errors.append(f"{Path(args.mapping).name} line {line}: io_id {ioid!r} missing from I/O catalog")
        referenced_io.add(ioid)

    for oid in operation_ids:
        rows = rows_by_api.get(oid, [])
        if not rows:
            errors.append(f"OpenAPI operationId {oid!r} has no API→IO mapping")
            continue
        io_rows = [r for r in rows if (r.get("io_id") or "").strip() not in ("", "NO_IO_EXCEPTION")]
        exceptions = [r for r in rows if (r.get("io_id") or "").strip() == "NO_IO_EXCEPTION"]
        if exceptions and io_rows:
            errors.append(f"operationId {oid!r} mixes NO_IO_EXCEPTION with real I/O rows")
        if not io_rows and not exceptions:
            errors.append(f"operationId {oid!r} must map to >=1 IO ID or an approved NO_IO_EXCEPTION")
        if args.strict and exceptions:
            for row in exceptions:
                if is_placeholder(row.get("notes")):
                    errors.append(f"operationId {oid!r}: strict NO_IO_EXCEPTION requires notes explaining why no I/O is correct")

    if not operation_ids and api_scope == "none":
        if mappings:
            errors.append("x-api-scope: none is declared, but api-io-mapping.csv contains rows")
        if catalog:
            errors.append("x-api-scope: none is declared, but io-catalog.csv contains rows")

    unused = sorted(set(catalog_by_id) - referenced_io)
    if unused:
        msg = "Catalog I/O operation(s) not referenced by any API mapping: " + ", ".join(unused)
        (errors if args.strict else warnings).append(msg)

    if args.strict:
        for line, row in enumerate(mappings, 2):
            oid = (row.get("operation_id") or "").strip()
            ioid = (row.get("io_id") or "").strip()
            for field in ("required", "transaction_scope", "failure_handling", "test_ids"):
                if is_placeholder(row.get(field)):
                    errors.append(f"{Path(args.mapping).name} line {line}: {field} is missing/unresolved for {oid}/{ioid}")
            if ioid == "NO_IO_EXCEPTION":
                for field in ("no_io_reason", "approved_by", "notes"):
                    if is_placeholder(row.get(field)):
                        errors.append(f"{Path(args.mapping).name} line {line}: {field} is required for NO_IO_EXCEPTION")

    for w in warnings: print("WARN:", w)
    for e in errors: print("ERROR:", e)
    if errors or (args.strict and warnings):
        print(f"API→IO mapping check FAILED: {len(errors)} error(s), {len(warnings)} warning(s).")
        return 1
    print(f"API→IO mapping check passed: {len(operation_ids)} operationId(s), {len(mappings)} mapping row(s), {len(catalog_by_id)} catalog I/O(s).")
    return 0

if __name__ == "__main__":
    sys.exit(main())
