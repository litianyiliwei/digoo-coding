#!/usr/bin/env python3
"""Validate the Figma design contract (stage 06).

The human contract is `design/figma-audit.md`. The implementation reference is
`design/figma-code/PAGE-00N.<ext>` — framework-aligned design code (Vue stack:
`.vue` + Element Plus; React stack: `.tsx`/`.jsx`). The compact machine
assertion table is `design/figma-layout.csv` (expected geometry + selector +
text/font for each asserted element). Screenshots are not part of the contract;
runtime fidelity is checked by scripts/check-figma-layout.py.

`--require-framework` enforces the 06 framework-alignment rule (target
framework, figma-design-to-code usage, and matching code extension) for new
Changes; legacy Changes can omit it.
"""
from pathlib import Path
import csv, re, sys

ROOT = Path(__file__).resolve().parents[1]
args = sys.argv[1:]
strict = "--strict" in args
require_framework = "--require-framework" in args
no_ui = "--no-ui" in args
change = None
reason = None
if "--change" in args:
    idx = args.index("--change")
    if idx + 1 >= len(args):
        print("Usage: check-figma-audit.py --change <change-id> [--no-ui --reason <reason>] [--strict] [--require-framework]", file=sys.stderr)
        sys.exit(2)
    change = args[idx + 1]
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", change):
        print("Invalid change-id", file=sys.stderr)
        sys.exit(2)
    args = args[:idx] + args[idx + 2:]
if "--reason" in args:
    idx = args.index("--reason")
    if idx + 1 >= len(args):
        print("--reason requires a value", file=sys.stderr)
        sys.exit(2)
    reason = args[idx + 1]
    args = args[:idx] + args[idx + 2:]
args = [a for a in args if a not in {"--strict", "--no-ui", "--require-framework"}]
if args or not change:
    print("Usage: check-figma-audit.py --change <change-id> [--no-ui --reason <reason>] [--strict] [--require-framework]", file=sys.stderr)
    sys.exit(2)
if no_ui and (not reason or not reason.strip()):
    print("--no-ui requires --reason <reason>", file=sys.stderr)
    sys.exit(2)

base = ROOT / "openspec/changes" / change / "design"
AUDIT = base / "figma-audit.md"
CODE_DIR = base / "figma-code"
CODE_README = CODE_DIR / "README.md"
LAYOUT = base / "figma-layout.csv"
ASSETS_DIR = base / "figma-assets"
ASSETS_README = ASSETS_DIR / "README.md"

LAYOUT_REQUIRED = [
    "page_id", "route", "element_id", "figma_node_id", "x", "y", "width", "height",
    "dom_selector", "assert_geometry", "assert_text", "tolerance_px",
    "text_content", "font_size", "font_weight", "notes",
]
PAGE_RE = re.compile(r"PAGE-\d{3}")


def section(text, title):
    start = text.find(title)
    if start < 0:
        return ""
    end = text.find("\n## ", start + len(title))
    return text[start:end if end >= 0 else len(text)]


def table_rows(section_text, skip_first=()):
    rows = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if re.match(r"^\|[\s:|-]+\|$", stripped):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if cells and cells[0] in skip_first:
            continue
        rows.append(cells)
    return rows


def resolve_asset(path_value):
    raw = path_value.strip().strip("`").strip()
    candidates = [base / raw, ROOT / raw]
    if raw.startswith("design/"):
        candidates.append(base / raw[len("design/"):])
    return next((p for p in candidates if p.is_file()), None)


def load_csv(path, required, label):
    if not path.is_file():
        return None
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])
        missing = [c for c in required if c not in fields]
        if missing:
            return [{"__error__": f"{label} missing columns: {', '.join(missing)}"}]
        return [{(k or ""): (v or "").strip() for k, v in row.items()} for row in reader]


def numeric(value):
    try:
        float(str(value).strip())
        return True
    except ValueError:
        return False


def truthy(value):
    return str(value).strip().lower() in {"1", "true", "yes", "y", "是"}


def page_ids_from_rows(rows):
    ids = []
    for cells in rows:
        if not cells:
            continue
        match = re.search(r"PAGE-\d{3}", cells[0])
        if match and match.group(0) not in ids:
            ids.append(match.group(0))
    return ids


if no_ui:
    if AUDIT.is_file() and AUDIT.stat().st_size:
        text = AUDIT.read_text(encoding="utf-8")
        if not re.search(r"^- 设计来源状态：N/A\s*$", section(text, "## 设计来源与选择"), re.M):
            print("ERROR: --no-ui declared but design/figma-audit.md does not declare 设计来源状态：N/A; update it or drop --no-ui")
            sys.exit(1)
    print(f"Figma audit check passed: this Change explicitly has no UI. Reason: {reason}")
    sys.exit(0)

if not AUDIT.is_file() or not AUDIT.stat().st_size:
    print(f"ERROR: missing Figma design contract: {AUDIT.relative_to(ROOT)}")
    print("UI-bearing Changes must export Figma node geometry, assertion mapping, tokens and UI approval.")
    sys.exit(1)

text = AUDIT.read_text(encoding="utf-8")
source_section = section(text, "## 设计来源与选择")
if re.search(r"^- 设计来源状态：N/A\s*$", source_section, re.M):
    if not re.search(r"^- 无 UI 理由：\s*\S", source_section, re.M):
        print("ERROR: 无 UI 时必须在“设计来源与选择”写入“- 无 UI 理由：<原因>”")
        sys.exit(1)
    print("Figma audit check passed: this Change declares no UI in figma-audit.md.")
    sys.exit(0)

errors, warnings = [], []
required_sections = [
    "## 设计来源与选择", "## 设计令牌（实际值）", "## 文字样式（实际值）",
    "## PAGE 与节点", "## PAGE 关键规格", "## 状态覆盖",
    "## 设计代码", "## 断言范围", "## 资产清单",
    "## MCP 读取记录", "## 差异与待确认", "## UI 评审",
]
for title in required_sections:
    if title not in text:
        errors.append(f"missing section: {title}")

if not re.search(r"(人工\s*Figma\s*设计|Figma\s*MCP\s*AI\s*自动设计)", source_section):
    errors.append("设计来源与选择必须明确为“人工 Figma 设计”或“Figma MCP AI 自动设计”")
if not re.search(r"^- 设计来源状态：APPROVED\s*$", source_section, re.M):
    errors.append("设计来源与选择必须标记“- 设计来源状态：APPROVED”，否则 06 不得开始")

required_inputs = ["需求与 AC", "Figma MCP", "设计规范"]
input_section = section(text, "## 设计输入与风格参考")
if not input_section:
    errors.append("missing section: ## 设计输入与风格参考")
else:
    missing_inputs = [name for name in required_inputs if name not in input_section]
    if missing_inputs:
        errors.append("设计输入与风格参考表缺少: " + "、".join(missing_inputs))

figma_refs = re.findall(r"https://(?:www\.)?figma\.com/[^\s)）]*|node-id=[A-Za-z0-9:%-]+|fileKey[=:][A-Za-z0-9]+", text, re.I)
figma_refs += re.findall(r"FIGMA-[A-Za-z0-9-]+", text)
if not figma_refs:
    errors.append("Figma 文件未登记：至少登记真实 Figma 链接、node-id、fileKey 或 FIGMA-ID")

# --- Token actual values ---
token_section = section(text, "## 设计令牌（实际值）")
token_rows = table_rows(token_section, skip_first=("变量",))
if len(token_rows) < 3:
    errors.append("设计令牌至少需要 3 条实际值（颜色/间距/圆角等），变量名和数量不算规格")
color_rows = [r for r in token_rows if len(r) >= 3 and re.search(r"#[0-9a-fA-F]{3,8}", r[2])]
px_rows = [r for r in token_rows if len(r) >= 3 and re.search(r"\d+(?:\.\d+)?px", r[2])]
if len(color_rows) < 2:
    errors.append("设计令牌必须至少包含 2 条带 hex 的颜色实际值")
if not px_rows:
    errors.append("设计令牌必须至少包含 1 条带 px 的间距/圆角/尺寸实际值")
for cells in token_rows:
    if len(cells) < 4 or not cells[0] or not cells[2] or not cells[3]:
        errors.append(f"设计令牌行不完整（变量/类型/实际值/CSS 映射）: {cells}")
    elif "COLOR" in cells[1].upper() and not re.search(r"#[0-9a-fA-F]{3,8}", cells[2]):
        errors.append(f"颜色令牌缺少 hex 实际值: {cells[0]}")
    elif not re.findall(r"--[A-Za-z0-9_-]+", cells[3]):
        errors.append(f"令牌缺少 CSS 变量映射: {cells[0]}")

# --- Typography actual values ---
type_section = section(text, "## 文字样式（实际值）")
type_rows = table_rows(type_section, skip_first=("样式",))
if len(type_rows) < 3:
    errors.append("文字样式至少需要 3 条实际值（字体/字重/字号/行高/字距）")
for cells in type_rows:
    if len(cells) < 6:
        errors.append(f"文字样式行不完整: {cells}")
        continue
    if "Noto Sans SC" not in cells[1] and cells[1] in ("", "PENDING"):
        errors.append(f"文字样式缺少字体族: {cells[0]}")
    if not re.search(r"\d+px", cells[3]):
        errors.append(f"文字样式缺少字号 px: {cells[0]}")
    if not re.search(r"\d{3}", cells[2]):
        errors.append(f"文字样式缺少字重: {cells[0]}")

# --- PAGE nodes (no reference images) ---
page_section = section(text, "## PAGE 与节点")
page_rows = table_rows(page_section, skip_first=("PAGE ID",))
pages = page_ids_from_rows(page_rows)
if not pages:
    errors.append("PAGE 与节点 must declare at least one PAGE-###; use 设计来源状态：N/A + 无 UI 理由 when no UI.")
for pid in pages:
    row = next((r for r in page_rows if r and pid in r[0]), None)
    if not row or len(row) < 4:
        errors.append(f"{pid}: PAGE 与节点 row incomplete (node/尺寸/状态)")
        continue
    if not re.search(r"\d+:\d+", row[1]):
        errors.append(f"{pid}: missing real Figma node id")
    if not re.search(r"\d+\s*[×x]\s*\d+", row[2]):
        errors.append(f"{pid}: missing frame size (e.g. 1440×900)")

# --- Per-PAGE specs ---
spec_section = section(text, "## PAGE 关键规格")
for pid in pages:
    heading = f"### {pid}"
    if heading not in spec_section:
        errors.append(f"PAGE 关键规格 missing heading: {heading}")
        continue
    start = spec_section.find(heading)
    end = spec_section.find("\n### ", start + len(heading))
    sub = spec_section[start:end if end >= 0 else len(spec_section)]
    if len(table_rows(sub)) < 3:
        errors.append(f"{pid}: PAGE 关键规格 needs at least 3 block rows with geometry/layout")
    if not re.search(r"w\s*=\s*\d+|width\s*[:=]\s*\d+|\d+\s*×\s*\d+", sub):
        errors.append(f"{pid}: PAGE 关键规格 missing concrete dimensions")

# --- States: default required; no reference image requirement ---
state_section = section(text, "## 状态覆盖")
state_rows = table_rows(state_section, skip_first=("PAGE ID",))
for pid in pages:
    rows = [r for r in state_rows if r and pid in r[0]]
    if not rows:
        errors.append(f"{pid}: 状态覆盖 missing")
        continue
    if not any(len(r) >= 2 and "default" in r[1].lower() for r in rows):
        errors.append(f"{pid}: 状态覆盖 must include default")
    for cells in rows:
        if len(cells) < 3:
            continue
        has_frame = "是" in cells[2] or "yes" in cells[2].lower()
        if not has_frame:
            decision = " ".join(cells[2:])
            if "决策" not in decision and "审批" not in decision:
                errors.append(f"{pid}/{cells[1]}: state without Figma frame needs explicit 07 决策/审批")

# --- Design code + compact layout assertion contract ---
if not CODE_README.is_file():
    errors.append(f"missing design-code README: {CODE_README.relative_to(ROOT)}")

code_text_by_page = {}
for pid in pages:
    matches = sorted(CODE_DIR.glob(f"{pid}.*")) if CODE_DIR.is_dir() else []
    code_file = next((p for p in matches if p.suffix.lower() in {".tsx", ".ts", ".vue", ".md"}), None)
    if not code_file:
        errors.append(f"missing design code for {pid}: {CODE_DIR.relative_to(ROOT)}/{pid}.vue (or .tsx/.jsx for React)")
    else:
        code_text_by_page[pid] = code_file.read_text(encoding="utf-8")

layout = load_csv(LAYOUT, LAYOUT_REQUIRED, "figma-layout.csv")
if layout is None:
    errors.append(f"missing assertion mapping: {LAYOUT.relative_to(ROOT)}")
elif layout and "__error__" in layout[0]:
    errors.append(layout[0]["__error__"])

layout_pairs = set()
if layout and not (layout and "__error__" in layout[0]):
    for row in layout:
        pid, nid = row.get("page_id", ""), row.get("figma_node_id", "")
        element_id = row.get("element_id", "")
        if not PAGE_RE.fullmatch(pid):
            errors.append(f"figma-layout.csv: invalid page_id {pid!r}")
            continue
        if not element_id:
            errors.append(f"figma-layout.csv: empty element_id for {pid}")
        if (pid, element_id) in layout_pairs:
            errors.append(f"figma-layout.csv: duplicate element {pid}/{element_id}")
        layout_pairs.add((pid, element_id))
        for field in ("x", "y", "width", "height"):
            if not numeric(row.get(field, "")):
                errors.append(f"figma-layout.csv: {pid}/{element_id} {field} is not numeric")
        if row.get("assert_geometry", "").upper() not in {"Y", "N"}:
            errors.append(f"figma-layout.csv: {pid}/{element_id} assert_geometry must be Y/N")
        if row.get("assert_text", "").upper() not in {"Y", "N"}:
            errors.append(f"figma-layout.csv: {pid}/{element_id} assert_text must be Y/N")
        if not numeric(row.get("tolerance_px", "")) or float(row["tolerance_px"]) <= 0:
            errors.append(f"figma-layout.csv: {pid}/{element_id} tolerance_px must be > 0")
        if not row.get("route"):
            errors.append(f"figma-layout.csv: {pid}/{element_id} route is empty (07 fills it)")
        if not row.get("dom_selector"):
            errors.append(f"figma-layout.csv: {pid}/{element_id} dom_selector is empty (07 fills it)")
        code_text = code_text_by_page.get(pid, "")
        if code_text and f'data-node-id="{nid}"' not in code_text:
            errors.append(
                f"figma-layout.csv: {pid}/{element_id} figma_node_id {nid!r} "
                f"not found in {pid} design code"
            )
    layout_pages = {pid for pid, _ in layout_pairs}
    for pid in pages:
        if pid not in layout_pages:
            errors.append(f"figma-layout.csv: PAGE {pid} has no assertion rows")

code_section = section(text, "## 设计代码")
if "figma-code/" not in code_section or "get_design_context" not in code_section:
    errors.append("## 设计代码 must reference figma-code/ and get_design_context")
if require_framework:
    m_framework = re.search(r"^- 目标框架：\s*\S", code_section, re.M)
    m_ext = re.search(r"^- 设计代码扩展名：\s*(\.(?:vue|tsx|jsx))\s*$", code_section, re.M)
    if not m_framework:
        errors.append("## 设计代码 must declare“- 目标框架：...” (technology-decisions.md)")
    if not m_ext:
        errors.append("## 设计代码 must declare“- 设计代码扩展名：.vue/.tsx/.jsx”")
    if "figma-design-to-code" not in code_section:
        errors.append("## 设计代码 must record the official figma-design-to-code Skill usage")
    if m_framework:
        framework = code_section[m_framework.start():].splitlines()[0]
        if "Vue" in framework or "vue" in framework:
            expected = {".vue"}
        elif "React" in framework or "react" in framework:
            expected = {".tsx", ".jsx"}
        else:
            expected = set()
            errors.append("目标框架 must name Vue or React so the code extension can be verified")
        if m_ext and expected and m_ext.group(1) not in expected:
            errors.append(
                f"设计代码扩展名 {m_ext.group(1)!r} does not match 目标框架 (expected {sorted(expected)})"
            )
        if expected:
            actual = {p.suffix.lower() for p in CODE_DIR.glob("PAGE-*.*")} if CODE_DIR.is_dir() else set()
            if not actual.issubset(expected):
                errors.append(
                    f"figma-code/ contains {sorted(actual)} but 目标框架 requires {sorted(expected)}"
                )
assertion_section = section(text, "## 断言范围")
if "figma-layout.csv" not in assertion_section:
    errors.append("## 断言范围 must reference figma-layout.csv")
if "check-figma-layout.py" not in assertion_section and "check-figma-layout" not in assertion_section:
    errors.append("## 断言范围 must name the runtime assertion gate (check-figma-layout.py)")

# --- Assets: only real image/SVG files; reference screenshots are not assets ---
asset_section = section(text, "## 资产清单")
if re.search(r"资产：无|无图片/SVG 资产|无资产", asset_section):
    asset_rows = []
else:
    asset_rows = table_rows(asset_section, skip_first=("资产",))
asset_names = []
for cells in asset_rows:
    if len(cells) < 3:
        errors.append(f"资产清单行不完整: {cells}")
        continue
    ref = cells[2]
    if not re.search(r"\.(png|jpg|jpeg|webp|svg)", ref, re.I):
        errors.append(f"资产清单缺少文件路径: {cells[0]}")
        continue
    if re.search(r"PAGE-\d{3}\.default\.(png|jpg|jpeg|webp)", ref, re.I):
        errors.append(f"资产清单不得登记参考截图；视觉比对使用 figma-code/ 与 figma-layout.csv: {ref}")
        continue
    asset_names.append(Path(ref.strip().strip("`")).name)
    if not resolve_asset(ref):
        errors.append(f"资产文件不存在: {ref}")
if asset_names:
    if not ASSETS_README.is_file():
        errors.append(f"缺少资产清单: {ASSETS_README.relative_to(ROOT)}")
    else:
        readme = ASSETS_README.read_text(encoding="utf-8")
        for name in asset_names:
            if name not in readme:
                errors.append(f"资产清单 README 未登记: {name}")

# --- MCP records: full node export + variable values are mandatory ---
mcp_text = section(text, "## MCP 读取记录")
mcp_rows = table_rows(mcp_text, skip_first=("工具/命令",))
tools = re.findall(r"(get_design_context|get_metadata|get_variable_defs|get_screenshot|use_figma|figma\s*mcp)", mcp_text, re.I)
if not tools:
    errors.append("MCP 读取记录缺少真实 Figma MCP 工具调用")
for required_tool in ("get_metadata", "get_variable_defs"):
    if not any(required_tool in " ".join(r).lower() and ("成功" in " ".join(r) or "passed" in " ".join(r).lower())
               for r in mcp_rows):
        errors.append(f"MCP 读取记录缺少成功的 {required_tool} 调用；节点几何必须来自真实读取")

# --- UI review ---
ui_section = section(text, "## UI 评审")
if not re.search(r"^- UI 评审状态：APPROVED\s*$", ui_section, re.M):
    errors.append("UI 评审必须标记“- UI 评审状态：APPROVED”，否则 06 不得通过")
if not re.search(r"^- 评审人：.+$", ui_section, re.M):
    errors.append("UI 评审缺少“- 评审人：”")
m = re.search(r"^- 评审证据：(.+)$", ui_section, re.M)
if not m:
    errors.append("UI 评审缺少“- 评审证据：”")
else:
    ev = m.group(1).strip()
    if not resolve_asset(ev) and not (base / ev).is_file() and not (ROOT / ev).is_file():
        errors.append(f"UI 评审证据文件不存在: {ev}")

for line_no, line in enumerate(text.splitlines(), 1):
    if re.search(r"PENDING|TODO|TBD|\[填充\]|<实际值>|<\.\.\.>", line, re.I):
        warnings.append(f"{AUDIT.relative_to(ROOT)}:{line_no}: unresolved placeholder remains")

if errors:
    for e in errors:
        print("ERROR:", e)
for w in warnings:
    print("WARN:", w)
if errors or (strict and warnings):
    print(f"Figma design contract check failed: {len(errors)} error(s), {len(warnings)} warning(s).")
    sys.exit(1)
print(f"Figma design contract passed: {len(pages)} PAGE(s), {len(color_rows)} color token(s), "
      f"{len(type_rows)} text style(s), {len(code_text_by_page)} design-code file(s), "
      f"{len(layout_pairs)} assertion(s).")
