#!/usr/bin/env python3
"""Build or verify the deterministic Figma handoff package from the authoritative inventories and design-spec."""
import csv, hashlib, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_STATES = [
    "default", "loading", "empty", "success", "error",
    "disabled", "no-permission", "boundary", "duplicate-submit",
]
NAMING = {
    "pageFrame": "PAGE-xxx",
    "blockSection": "BLOCK-xxx",
    "elementLayer": "ELEM-xxx",
    "rule": "Figma 图层名必须与清单 ID 一致，供 08 figma-audit 的 figma_node_id 映射",
}
CONSTRAINT_TEXT = [
    "必须遵循：页面集合、区块顺序与边界、元素所属区块、状态覆盖、权限与导航行为、交互结果。",
    "允许优化：间距节奏、排版层级、组件质量、图标语义化、空态/错误态/无权限态设计、可访问性、一致性与动效。",
    "不得作为输入：原型截图、原型临时占位画法与试错图标、原型的彩色值（颜色由设计 token 绑定）。",
]

args = sys.argv[1:]
change_id = None
mode = "check"
if "--change" in args:
    idx = args.index("--change")
    if idx + 1 >= len(args):
        print("Usage: build-figma-handoff.py --change <change-id> [--write | --check]", file=sys.stderr); sys.exit(2)
    change_id = args[idx + 1]
    args = args[:idx] + args[idx + 2:]
if "--write" in args:
    mode = "write"; args = [a for a in args if a != "--write"]
if "--check" in args:
    args = [a for a in args if a != "--check"]
if args:
    print("Usage: build-figma-handoff.py --change <change-id> [--write | --check]", file=sys.stderr); sys.exit(2)
if not change_id or not __import__("re").fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", change_id):
    print("build-figma-handoff.py requires a valid --change <change-id>", file=sys.stderr); sys.exit(2)

base = ROOT / "openspec/changes" / change_id / "design"
out_dir = base / "generated"
OUT_JSON = out_dir / "figma-handoff.json"
OUT_MD = out_dir / "figma-handoff.md"
INPUTS = {
    "page-inventory.csv": base / "page-inventory.csv",
    "block-inventory.csv": base / "block-inventory.csv",
    "interaction-map.csv": base / "interaction-map.csv",
    "design-spec.json": base / "design-spec.json",
}

ERRORS = []


def read_csv(path):
    if not path.is_file():
        ERRORS.append(f"Missing file: {path.relative_to(ROOT)}")
        return []
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def sort_order(row):
    raw = (row.get("sort_order") or "").strip()
    if not raw.isdigit():
        ERRORS.append(f"block-inventory.csv: block {row.get('block_id')!r} has non-integer sort_order {raw!r}")
        return 10**9
    return int(raw)


def event_dict(row):
    mapping = [
        ("eventId", "event_id"), ("trigger", "trigger"), ("input", "input"),
        ("preconditions", "preconditions"), ("steps", "steps"), ("output", "output"),
        ("stateChange", "state_change"), ("errorBehavior", "error_behavior"),
        ("operationId", "operation_id"), ("status", "status"),
    ]
    return {key: (row.get(source) or "").strip() for key, source in mapping if (row.get(source) or "").strip()}


def tiered_text(entry, number=False):
    if not isinstance(entry, dict):
        return str(entry)
    value = entry.get("value")
    tier = entry.get("tier", "?")
    if isinstance(value, list):
        shown = "[" + ",".join(str(v) for v in value) + "]"
    elif isinstance(value, dict):
        shown = f"{value.get('width')}×{value.get('height')}"
    else:
        shown = str(value)
    return f"{shown}({tier})"


def layout_text(layout):
    order = ["direction", "align", "gap", "padding", "width", "height"]
    parts = []
    for key in order:
        if key in (layout or {}):
            parts.append(f"{key}={tiered_text(layout[key])}")
    return "；".join(parts) if parts else "（未指定）"


def element_line(element):
    bits = [f"type={element.get('type', '?')}"]
    if element.get("label"):
        bits.append(f"文案「{element['label']}」")
    if element.get("size"):
        bits.append(f"size={tiered_text(element['size'])}")
    if element.get("radius"):
        bits.append(f"radius={tiered_text(element['radius'])}")
    if element.get("fill"):
        bits.append(f"fill={element['fill']}")
    if element.get("textStyle"):
        bits.append(f"textStyle={element['textStyle']}")
    if element.get("icon"):
        bits.append(f"icon={element['icon']}")
    if element.get("component"):
        component = element["component"]
        bits.append("component=" + "/".join(str(component.get(k, "")) for k in ("key", "variant") if component.get(k)))
    if element.get("states"):
        bits.append("状态=" + "/".join(element["states"]))
    return "｜".join(bits)


pages = read_csv(INPUTS["page-inventory.csv"])
blocks = read_csv(INPUTS["block-inventory.csv"])
events = read_csv(INPUTS["interaction-map.csv"])
if not INPUTS["design-spec.json"].is_file():
    ERRORS.append(f"Missing file: {INPUTS['design-spec.json'].relative_to(ROOT)}")
    spec = {}
else:
    try:
        spec = json.loads(INPUTS["design-spec.json"].read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        ERRORS.append(f"design-spec.json is not valid JSON: {exc}")
        spec = {}
if spec and (spec.get("changeId") or "") != change_id:
    ERRORS.append(f"design-spec.json changeId {spec.get('changeId')!r} does not match --change {change_id!r}")
if ERRORS:
    for msg in ERRORS:
        print("ERROR:", msg)
    print("Figma handoff build failed: fix the inputs first.")
    sys.exit(1)

source_hashes = {}
for name, path in INPUTS.items():
    source_hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
spec_pages = {p.get("pageId"): p for p in (spec.get("pages") or [])}
spec_blocks = {}
for page in spec.get("pages") or []:
    for block in page.get("blocks") or []:
        spec_blocks[(page.get("pageId"), block.get("blockId"))] = block

events_by_block = {}
for row in events:
    key = ((row.get("page_id") or "").strip(), (row.get("block_id") or "").strip())
    events_by_block.setdefault(key, []).append(row)

handoff_pages = []
md = [
    f"# Figma 交接包 — {change_id}",
    "",
    "> 派生自 page-inventory.csv、block-inventory.csv、interaction-map.csv 与 design-spec.json；",
    "> 由 `scripts/build-figma-handoff.py` 生成，禁止手改。08 审计仍以三份 CSV 为唯一权威。",
    "> source-sha256：" + "；".join(f"{name}={digest[:12]}" for name, digest in source_hashes.items()),
    "",
    "## 命名与状态词表",
    "",
    f"- 页面 Frame：`{NAMING['pageFrame']}`；区块 section：`{NAMING['blockSection']}`；元素图层：`{NAMING['elementLayer']}`",
    "- 状态： " + " / ".join(REQUIRED_STATES),
    "",
    "## 硬约束与可优化范围",
    "",
]
md += [f"- {line}" for line in CONSTRAINT_TEXT]
md.append("")

for page_row in pages:
    pid = (page_row.get("page_id") or "").strip()
    page_name = (page_row.get("page_name") or "").strip()
    page_spec = spec_pages.get(pid, {})
    page_blocks = sorted([b for b in blocks if (b.get("page_id") or "").strip() == pid], key=sort_order)
    page_handoff = {
        "pageId": pid,
        "pageName": page_name,
        "route": (page_row.get("route") or "").strip(),
        "roles": (page_row.get("roles") or "").strip(),
        "inventoryStatus": (page_row.get("status") or "").strip(),
        "inventoryStates": (page_row.get("states") or "").strip(),
        "designStates": page_spec.get("states", []),
        "frame": page_spec.get("frame"),
        "shell": page_spec.get("shell"),
        "blocks": [],
    }
    md += [
        f"## {pid} {page_name}",
        "",
        f"- 路由：{page_handoff['route']}；角色：{page_handoff['roles']}；清单状态：{page_handoff['inventoryStates']}",
    ]
    if page_spec.get("frame"):
        md.append(f"- 画板：{page_spec['frame'].get('width')} × {page_spec['frame'].get('height')}")
    if page_spec.get("shell"):
        shell = page_spec["shell"]
        items = "、".join(shell.get("items") or [])
        md.append(f"- 外壳：{shell.get('type')} / {shell.get('variant', 'N/A')}（{items or '无标签项'}）")
    if page_handoff["designStates"]:
        md.append("- 设计状态变体：" + "、".join(page_handoff["designStates"]))
    md.append("")
    for index, block_row in enumerate(page_blocks, 1):
        bid = (block_row.get("block_id") or "").strip()
        block_spec = spec_blocks.get((pid, bid), {})
        block_events = sorted(events_by_block.get((pid, bid), []), key=lambda r: (r.get("event_id") or ""))
        by_element = {}
        for event_row in block_events:
            by_element.setdefault((event_row.get("element_id") or "").strip(), []).append(event_dict(event_row))
        elements = []
        for element in block_spec.get("elements") or []:
            merged = dict(element)
            eid = element.get("elementId")
            merged["events"] = by_element.get(eid, []) if eid else []
            elements.append(merged)
        known = {e.get("elementId") for e in elements if e.get("elementId")}
        for eid in sorted(x for x in by_element if x and x not in known):
            elements.append({"elementId": eid, "type": "other", "events": by_element[eid],
                             "notes": "element missing from design-spec.json; run check-design-spec.py"})
        block_handoff = {
            "blockId": bid,
            "blockName": (block_row.get("block_name") or "").strip(),
            "blockType": (block_row.get("block_type") or "").strip(),
            "order": sort_order(block_row),
            "description": (block_row.get("description") or "").strip(),
            "requirementIds": (block_row.get("requirement_ids") or "").strip(),
            "inventoryStatus": (block_row.get("status") or "").strip(),
            "layout": block_spec.get("layout", {}),
            "states": block_spec.get("states", []),
            "elements": elements,
        }
        page_handoff["blocks"].append(block_handoff)
        md += [f"### {index}. {bid} {block_handoff['blockName']}（{block_handoff['blockType']}；{block_handoff['description']}）", ""]
        md.append(f"- 布局：{layout_text(block_handoff['layout'])}")
        if block_handoff["states"]:
            md.append("- 区块状态：" + "、".join(block_handoff["states"]))
        md.append("- 元素：")
        if not elements:
            md.append("  - （无登记元素）")
        for element in elements:
            label = f"`{element['elementId']}` " if element.get("elementId") else "（装饰）"
            md.append(f"  - {label}{element_line(element)}")
            for event in element.get("events") or []:
                summary = event.get("trigger", "")
                if event.get("output"):
                    summary += f" → {event['output']}"
                if event.get("stateChange"):
                    summary += f"；状态变化={event['stateChange']}"
                if event.get("errorBehavior"):
                    summary += f"；错误={event['errorBehavior']}"
                md.append(f"    - `{event.get('eventId', '?')}` {summary}")
        md.append("")
    handoff_pages.append(page_handoff)

handoff = {
    "schemaVersion": "figma-handoff/1.0",
    "changeId": change_id,
    "sourceSha256": source_hashes,
    "naming": NAMING,
    "requiredStates": REQUIRED_STATES,
    "pages": handoff_pages,
}
json_text = json.dumps(handoff, ensure_ascii=False, indent=2) + "\n"
md_text = "\n".join(md).rstrip() + "\n"

if mode == "write":
    out_dir.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json_text, encoding="utf-8")
    OUT_MD.write_text(md_text, encoding="utf-8")
    print(f"Wrote {OUT_JSON.relative_to(ROOT)} and {OUT_MD.relative_to(ROOT)}.")
else:
    stale = []
    for path, expected in ((OUT_JSON, json_text), (OUT_MD, md_text)):
        if not path.is_file():
            stale.append(f"missing: {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8") != expected:
            stale.append(f"stale: {path.relative_to(ROOT)}")
    if stale:
        for msg in stale:
            print("ERROR:", msg)
        print("Figma handoff is stale; regenerate with: python scripts/build-figma-handoff.py --change "
              f"{change_id} --write", file=sys.stderr)
        sys.exit(1)
    print(f"Figma handoff is current: {len(handoff_pages)} page(s), "
          f"{sum(len(p['blocks']) for p in handoff_pages)} block(s), "
          f"{sum(len(b['elements']) for p in handoff_pages for b in p['blocks'])} element(s).")
