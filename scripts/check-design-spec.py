#!/usr/bin/env python3
"""Validate design-spec.json against its schema and cross-check IDs with the authoritative inventories."""
import csv, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "templates/change-assets/design/design-spec.schema.json"
STATE_ALIASES = {
    "默认": "default", "加载": "loading", "空数据": "empty", "空态": "empty", "无数据": "empty",
    "成功": "success", "失败": "error", "错误": "error", "禁用": "disabled", "无权限": "no-permission",
    "边界": "boundary", "边界值": "boundary", "重复提交": "duplicate-submit", "幂等": "duplicate-submit",
}

args = sys.argv[1:]
STRICT = "--strict" in args
NO_UI = "--no-ui" in args
REQUIRE_TOKENS = "--require-tokens" in args
change_id = None
reason = None
if "--change" in args:
    idx = args.index("--change")
    if idx + 1 >= len(args):
        print("Usage: check-design-spec.py --change <change-id> [--no-ui --reason <reason>] [--strict] [--require-tokens]", file=sys.stderr); sys.exit(2)
    change_id = args[idx + 1]
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", change_id):
        print("Invalid change-id", file=sys.stderr); sys.exit(2)
    args = args[:idx] + args[idx + 2:]
if "--reason" in args:
    idx = args.index("--reason")
    if idx + 1 >= len(args):
        print("--reason requires a value", file=sys.stderr); sys.exit(2)
    reason = args[idx + 1]
    args = args[:idx] + args[idx + 2:]
args = [a for a in args if a not in {"--strict", "--no-ui", "--require-tokens"}]
if args:
    print("Usage: check-design-spec.py --change <change-id> [--no-ui --reason <reason>] [--strict] [--require-tokens]", file=sys.stderr); sys.exit(2)
if not change_id:
    print("check-design-spec.py requires --change <change-id>", file=sys.stderr); sys.exit(2)
if NO_UI and (not reason or not reason.strip()):
    print("--no-ui requires --reason <reason>", file=sys.stderr); sys.exit(2)
if NO_UI and not STRICT:
    print("Use --strict with --no-ui so the explicit scope exception is checked", file=sys.stderr); sys.exit(2)

base = ROOT / "openspec/changes" / change_id / "design"
SPEC_FILE = base / "design-spec.json"
TOKENS_FILE = base / "design-tokens.json"
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
        return list(reader)


def resolve_ref(root_schema, ref):
    if not ref.startswith("#/"):
        raise ValueError(f"Unsupported $ref: {ref}")
    node = root_schema
    for part in ref[2:].split("/"):
        node = node[part.replace("~1", "/").replace("~0", "~")]
    return node


def validate(value, schema, root_schema, path):
    if "$ref" in schema:
        schema = resolve_ref(root_schema, schema["$ref"])
    expected = schema.get("type")
    if expected:
        checks = {
            "object": lambda v: isinstance(v, dict),
            "array": lambda v: isinstance(v, list),
            "string": lambda v: isinstance(v, str),
            "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "boolean": lambda v: isinstance(v, bool),
        }
        if expected not in checks:
            ERRORS.append(f"{path}: unsupported schema type {expected}")
        elif not checks[expected](value):
            ERRORS.append(f"{path}: expected {expected}, got {type(value).__name__}")
            return
    if "const" in schema and value != schema["const"]:
        ERRORS.append(f"{path}: must equal {schema['const']!r}")
    if "enum" in schema and value not in schema["enum"]:
        ERRORS.append(f"{path}: {value!r} is not one of {schema['enum']}")
    if isinstance(value, str):
        if "pattern" in schema and not re.search(schema["pattern"], value):
            ERRORS.append(f"{path}: {value!r} does not match pattern {schema['pattern']}")
        if "minLength" in schema and len(value) < schema["minLength"]:
            ERRORS.append(f"{path}: shorter than minLength {schema['minLength']}")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            ERRORS.append(f"{path}: below minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            ERRORS.append(f"{path}: above maximum {schema['maximum']}")
    if isinstance(value, list):
        if "minItems" in schema and len(value) < schema["minItems"]:
            ERRORS.append(f"{path}: fewer than minItems {schema['minItems']}")
        if "maxItems" in schema and len(value) > schema["maxItems"]:
            ERRORS.append(f"{path}: more than maxItems {schema['maxItems']}")
        if "items" in schema:
            for i, item in enumerate(value):
                validate(item, schema["items"], root_schema, f"{path}[{i}]")
    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                ERRORS.append(f"{path}: missing required property {key!r}")
        properties = schema.get("properties", {})
        additional = schema.get("additionalProperties", True)
        for key, item in value.items():
            if key in properties:
                validate(item, properties[key], root_schema, f"{path}.{key}")
            elif additional is False:
                ERRORS.append(f"{path}: unexpected property {key!r}")
            elif isinstance(additional, dict):
                validate(item, additional, root_schema, f"{path}.{key}")


def walk_strings(node, path="$"):
    if isinstance(node, dict):
        for key, value in node.items():
            yield from walk_strings(value, f"{path}.{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            yield from walk_strings(value, f"{path}[{i}]")
    elif isinstance(node, str):
        yield path, node


def split_states(value):
    tokens = [x.strip() for x in re.split(r"[;；,，、/|]+", value or "") if x.strip()]
    return [STATE_ALIASES.get(x, x) for x in tokens]


def flatten_tokens(node, prefix=""):
    found = set()
    if isinstance(node, dict):
        if "$value" in node:
            found.add(prefix)
            return found
        for key, value in node.items():
            if key.startswith("$"):
                continue
            child = f"{prefix}.{key}" if prefix else key
            found |= flatten_tokens(value, child)
    return found


# Explicit no-UI scope: the design spec must not exist.
if NO_UI:
    if SPEC_FILE.exists():
        ERRORS.append("--no-ui was declared but design-spec.json exists; remove --no-ui or delete the spec")
    for msg in ERRORS:
        print("ERROR:", msg)
    if ERRORS:
        print(f"Design spec check failed: {len(ERRORS)} error(s).")
        sys.exit(1)
    print(f"Design spec check passed: this Change explicitly has no UI. Reason: {reason}")
    sys.exit(0)

if not SPEC_FILE.is_file():
    print(f"ERROR: Missing file: {SPEC_FILE.relative_to(ROOT)}", file=sys.stderr)
    print("Create it from templates/change-assets/design/design-spec.json before running the stage 07 gate.", file=sys.stderr)
    sys.exit(1)
if not SCHEMA_PATH.is_file():
    print(f"ERROR: Missing schema: {SCHEMA_PATH.relative_to(ROOT)}", file=sys.stderr)
    sys.exit(1)

try:
    spec = json.loads(SPEC_FILE.read_text(encoding="utf-8"))
except json.JSONDecodeError as exc:
    print(f"ERROR: design-spec.json is not valid JSON: {exc}", file=sys.stderr)
    sys.exit(1)
schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
validate(spec, schema, schema, "$")

pages = read_csv(PAGE_FILE, ["page_id", "page_name", "route", "states", "status"])
blocks = read_csv(BLOCK_FILE, ["block_id", "page_id", "block_name", "block_type", "description", "sort_order", "status"])
events = read_csv(EVENT_FILE, ["event_id", "page_id", "block_id", "element_id", "trigger", "state_change", "error_behavior", "status"])

if (spec.get("changeId") or "") != change_id:
    ERRORS.append(f"$.changeId: {spec.get('changeId')!r} does not match --change {change_id!r}")

page_rows = {r.get("page_id", "").strip(): r for r in pages if r.get("page_id")}
block_rows = {}
for row in blocks:
    bid = (row.get("block_id") or "").strip()
    if bid:
        block_rows[bid] = row
inventory_elements = {}
for row in events:
    bid = (row.get("block_id") or "").strip()
    elem = (row.get("element_id") or "").strip()
    if bid and elem:
        inventory_elements.setdefault(bid, set()).add(elem)

spec_pages = spec.get("pages") or []
spec_page_ids = [p.get("pageId") for p in spec_pages]
seen_pages = set()
for pid in spec_page_ids:
    if pid in seen_pages:
        ERRORS.append(f"design-spec.json: duplicate pageId {pid}")
    seen_pages.add(pid)
missing_pages = sorted(set(page_rows) - seen_pages)
extra_pages = sorted(seen_pages - set(page_rows))
if missing_pages:
    ERRORS.append(f"design-spec.json: pages missing from spec: {', '.join(missing_pages)}")
if extra_pages:
    ERRORS.append(f"design-spec.json: pages not in page-inventory.csv: {', '.join(extra_pages)}")

total_blocks = total_elements = total_token_refs = 0
for page in spec_pages:
    pid = page.get("pageId") or "?"
    inv_rows = [r for r in blocks if (r.get("page_id") or "").strip() == pid]
    inv_order = {}
    for row in inv_rows:
        bid = (row.get("block_id") or "").strip()
        raw_order = (row.get("sort_order") or "").strip()
        if not raw_order.isdigit():
            ERRORS.append(f"block-inventory.csv: block {bid or '?'} has non-integer sort_order {raw_order!r}")
            continue
        inv_order[bid] = int(raw_order)
    spec_blocks = page.get("blocks") or []
    spec_block_ids = [b.get("blockId") for b in spec_blocks]
    seen_blocks = set()
    for bid in spec_block_ids:
        if bid in seen_blocks:
            ERRORS.append(f"{pid}: duplicate blockId {bid}")
        seen_blocks.add(bid)
    missing_blocks = sorted(set(inv_order) - seen_blocks)
    extra_blocks = sorted(seen_blocks - set(inv_order))
    if missing_blocks:
        ERRORS.append(f"{pid}: blocks missing from design-spec: {', '.join(missing_blocks)}")
    if extra_blocks:
        ERRORS.append(f"{pid}: blocks not in block-inventory.csv: {', '.join(extra_blocks)}")
    for block in spec_blocks:
        bid = block.get("blockId") or "?"
        total_blocks += 1
        if bid in inv_order and block.get("order") != inv_order[bid]:
            ERRORS.append(f"{pid}/{bid}: order {block.get('order')!r} != block-inventory sort_order {inv_order[bid]}")
        spec_elems = [e.get("elementId") for e in (block.get("elements") or []) if e.get("elementId")]
        seen_elems = set()
        for elem in spec_elems:
            if elem in seen_elems:
                ERRORS.append(f"{pid}/{bid}: duplicate elementId {elem}")
            seen_elems.add(elem)
        total_elements += len(spec_elems)
        inv_elems = inventory_elements.get(bid, set())
        missing_elems = sorted(inv_elems - seen_elems)
        extra_elems = sorted(seen_elems - inv_elems)
        if missing_elems:
            ERRORS.append(f"{pid}/{bid}: interactive elements missing from design-spec: {', '.join(missing_elems)}")
        if extra_elems:
            ERRORS.append(f"{pid}/{bid}: element IDs not in interaction-map.csv: {', '.join(extra_elems)}")
    page_row = page_rows.get(pid)
    if page_row:
        required_states = set(split_states(page_row.get("states")))
        spec_states = set(page.get("states") or [])
        missing_states = sorted(x for x in required_states if x not in spec_states)
        if missing_states:
            ERRORS.append(f"{pid}: design-spec states do not cover page-inventory states: {', '.join(missing_states)}")

    if page.get("shell") and page["shell"].get("type") == "bottom-tab" and not page["shell"].get("items"):
        ERRORS.append(f"{pid}: bottom-tab shell requires non-empty items")

token_refs = set()
for path, text in walk_strings(spec):
    if text.startswith("token:"):
        token_refs.add(text[len("token:"):])
    if any(marker in text for marker in ("TODO", "TBD", "待确认")):
        WARNINGS.append(f"{path}: unresolved placeholder {text!r}")
total_token_refs = len(token_refs)
if TOKENS_FILE.is_file():
    try:
        tokens = json.loads(TOKENS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        ERRORS.append(f"design-tokens.json is not valid JSON: {exc}")
        tokens = {}
    available = flatten_tokens(tokens)
    unknown = sorted(x for x in token_refs if x not in available)
    if unknown:
        ERRORS.append("design-spec.json: token references not found in design-tokens.json: " + ", ".join(unknown))
elif REQUIRE_TOKENS:
    ERRORS.append(f"Missing token file: {TOKENS_FILE.relative_to(ROOT)} (--require-tokens)")
else:
    WARNINGS.append("design-tokens.json not found; token references were not verified (use --require-tokens to enforce)")

for msg in WARNINGS:
    print("WARN:", msg)
for msg in ERRORS:
    print("ERROR:", msg)
if ERRORS or (STRICT and WARNINGS):
    print(f"Design spec check failed: {len(ERRORS)} error(s), {len(WARNINGS)} warning(s).")
    sys.exit(1)
print(f"Design spec check passed: {len(spec_pages)} page(s), {total_blocks} block(s), {total_elements} element(s), {total_token_refs} token ref(s) in {base.relative_to(ROOT)}.")
