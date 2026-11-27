#!/usr/bin/env python3
"""Validate the UI design contract (stage 06).

The human contract is `design/figma-audit.md`. The implementation reference is
`design/figma-code/PAGE-00N.<ext>` — framework-aligned design code (Vue stack:
`.vue` + Element Plus; React stack: `.tsx`/`.jsx`). The compact machine
assertion table is `design/figma-layout.csv` (expected geometry + selector +
text/font for each asserted element). Screenshots are not part of the contract;
runtime fidelity is checked by scripts/check-figma-layout.py.

Stage 06 accepts the HTML-first design source with an explicit provenance:

* `Design-to-HTML` + `User-provided HTML` — stakeholders supply the design HTML.
* `Design-to-HTML` + `AI-authored from requirements` — AI authors the HTML.
* `Design-to-HTML` + `Figma-to-HTML` — AI reads an approved Figma file through
  Figma MCP and converts it to HTML; the HTML remains the review deliverable.
* `Figma` — a direct Figma file read through Figma MCP (legacy Changes only).

The file names (`figma-audit.md`, `figma-code/`, `figma-layout.csv`) are
historical and are shared by both sources so downstream stages keep one
contract shape.

`--require-framework` enforces the 06 framework-alignment rule (target
framework, matching code extension) and the newer per-platform contract
(`Target platforms` in user-stories.md, a `Platform` column on every PAGE,
and `platform`/`viewport` columns in figma-layout.csv) for new Changes;
legacy Changes can omit it.
"""
from pathlib import Path
import csv, re, sys

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
import gate_common as gm  # noqa: E402

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
HTML_DIR = base / "ui-html"
HTML_README = HTML_DIR / "README.md"
HTML_INDEX = HTML_DIR / "index.html"
USER_STORIES = base / "user-stories.md"

LAYOUT_REQUIRED = [
    "page_id", "route", "element_id", "figma_node_id", "x", "y", "width", "height",
    "dom_selector", "assert_geometry", "assert_text", "tolerance_px",
    "text_content", "font_size", "font_weight", "notes",
]
LAYOUT_REQUIRED_NEW = LAYOUT_REQUIRED[:1] + ["platform", "viewport"] + LAYOUT_REQUIRED[1:]
PAGE_RE = re.compile(r"PAGE-\d{3}")

# Canonical client-platform vocabulary (shared with requirement/roadmap gates).
PLATFORMS = gm.PLATFORMS


def normalize_platform(value):
    return gm.normalize_platform(value)


def section(text, title):
    start = text.find(title)
    if start < 0:
        return ""
    end = text.find("\n## ", start + len(title))
    return text[start:end if end >= 0 else len(text)]


def section_any(text, *titles):
    for title in titles:
        found = section(text, title)
        if found:
            return found
    return ""


SOURCE_SEC = ("## 设计来源与选择", "## Design Source and Selection")
TOKEN_SEC = ("## 设计令牌（实际值）", "## Design Tokens (Actual Values)")
TYPE_SEC = ("## 文字样式（实际值）", "## Text Styles (Actual Values)")
PAGE_SEC = ("## PAGE 与节点", "## PAGEs and Nodes")
SPEC_SEC = ("## PAGE 关键规格", "## PAGE Key Specifications")
STATE_SEC = ("## 状态覆盖", "## State Coverage")
CODE_SEC = ("## 设计代码", "## Design Code")
ASSERT_SEC = ("## 断言范围", "## Assertion Scope")
ASSET_SEC = ("## 资产清单", "## Asset List")
MCP_SEC = ("## MCP 读取记录", "## MCP Read Records")
HTML_DOCS_SEC = ("## HTML 设计稿", "## HTML Design Docs")
HTML_RECORDS_SEC = ("## HTML 读取记录", "## HTML Read Records")
UI_SEC = ("## UI 评审", "## UI Review")
COVERAGE_SEC = ("## 需求覆盖", "## Requirements Coverage")
INPUT_SEC = ("## 设计输入与风格参考", "## Design Inputs and Style References")
DIFF_SEC = ("## 差异与待确认", "## Differences and Pending Confirmation")


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


def table_header(section_text):
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if re.match(r"^\|[\s:|-]+\|$", stripped):
            continue
        return [c.strip() for c in stripped.strip("|").split("|")]
    return []


def header_index(header, label):
    target = label.casefold()
    for index, cell in enumerate(header):
        if cell.casefold() == target or target in cell.casefold():
            return index
    return -1


def cell_at(row, index, default=""):
    if 0 <= index < len(row):
        return row[index]
    return default


def resolve_asset(path_value):
    raw = path_value.strip().strip("`").strip()
    candidates = [base / raw, ROOT / raw]
    if raw.startswith("design/"):
        candidates.append(base / raw[len("design/"):])
    if raw.startswith("ui-html/"):
        candidates.append(base / raw)
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


def normalize_platform(value):
    text = str(value or "").strip().strip("`").strip().casefold()
    if not text:
        return ""
    if text in PLATFORMS:
        return text
    return PLATFORM_ALIASES.get(text, "")


def declared_platforms():
    """Read the Change-level '<platforms>' declaration from user-stories.md."""
    if not USER_STORIES.is_file():
        return None
    text = USER_STORIES.read_text(encoding="utf-8")
    match = re.search(
        r"^- (?:目标平台|Target platforms)[:：]\s*(.+)$", text, re.M | re.I
    )
    if not match:
        return None
    raw = match.group(1)
    tokens = re.split(r"[;,；，、]", raw)
    result = []
    for token in tokens:
        token = token.strip()
        if not token or token.upper().startswith("N/A"):
            continue
        name = normalize_platform(token)
        if name and name not in result:
            result.append(name)
    return result


def html_page_ref(cells):
    for cell in cells:
        if re.search(r"\.html?\b", cell, re.I) or "ui-html/" in cell:
            return cell
    return ""


def count_pages_by_platform(page_platforms):
    counts = {}
    for platform in page_platforms:
        if platform:
            counts[platform] = counts.get(platform, 0) + 1
    return counts


if no_ui:
    if AUDIT.is_file() and AUDIT.stat().st_size:
        text = AUDIT.read_text(encoding="utf-8")
        if not re.search(r"^- (?:设计来源状态|Design source status)[:：]\s*N/A\s*$", section_any(text, *SOURCE_SEC), re.M):
            print("ERROR: --no-ui declared but design/figma-audit.md does not declare Design source status: N/A (设计来源状态：N/A); update it or drop --no-ui")
            sys.exit(1)
    print(f"UI design audit check passed: this Change explicitly has no UI. Reason: {reason}")
    sys.exit(0)

if not AUDIT.is_file() or not AUDIT.stat().st_size:
    print(f"ERROR: missing UI design contract: {AUDIT.relative_to(ROOT)}")
    print("UI-bearing Changes must record the design source, tokens, geometry assertion mapping and UI approval (Figma or Design-to-HTML).")
    sys.exit(1)

text = AUDIT.read_text(encoding="utf-8")
source_section = section_any(text, *SOURCE_SEC)
if re.search(r"^- (?:设计来源状态|Design source status)[:：]\s*N/A\s*$", source_section, re.M):
    if not re.search(r"^- (?:无 UI 理由|Reason for no UI)[:：]\s*\S", source_section, re.M):
        print("ERROR: a no-UI Change must write '- 无 UI 理由：<原因>' / '- Reason for no UI: <reason>' under Design Source and Selection")
        sys.exit(1)
    print("UI design audit check passed: this Change declares no UI in figma-audit.md.")
    sys.exit(0)

HTML_TERM = re.compile(r"Design-to-HTML|design\s*to\s*html|HTML\s*设计稿|设计转\s*HTML", re.I)
FIGMA_TERM = re.compile(r"Figma\s*MCP|Manual\s+Figma|人工\s*Figma|Figma\s+design", re.I)
source_line = re.search(
    r"^- (?:设计来源|Design source(?: selection)?)[:：]\s*(.+)$",
    source_section,
    re.M | re.I,
)
source_value = source_line.group(1) if source_line else ""
html_source = bool(HTML_TERM.search(source_value))
figma_source = bool(FIGMA_TERM.search(source_value))
if not source_line:
    html_source = bool(HTML_TERM.search(source_section))
    figma_source = bool(FIGMA_TERM.search(source_section))

# HTML provenance: the design source is HTML, but the HTML itself may be
# supplied by the user, authored by AI from requirements, or produced by
# converting an approved Figma file (Figma-to-HTML).
PROVENANCE_LINE = re.search(
    r"^- (?:HTML 来源|HTML provenance)[:：]\s*(.+)$",
    source_section,
    re.M | re.I,
)
PROVENANCE_FIGMA = re.compile(r"Figma-to-HTML|figma\s*to\s*html|Figma\s*转\s*HTML|Figma\s*转码", re.I)
PROVENANCE_USER = re.compile(r"User-provided|用户直接提供|用户提供|user\s*supplied", re.I)
PROVENANCE_AI = re.compile(r"AI-authored|AI\s*生成|AI\s*编写|from requirements|需求生成", re.I)
provenance_value = PROVENANCE_LINE.group(1) if PROVENANCE_LINE else ""
provenance_figma = bool(PROVENANCE_FIGMA.search(provenance_value))
provenance_user = bool(PROVENANCE_USER.search(provenance_value))
provenance_ai = bool(PROVENANCE_AI.search(provenance_value))

errors, warnings = [], []
# Advisory findings are recommendations only: printed, never failing (even under --strict).
advisories: list[str] = []
required_sections = [
    ("## 设计来源与选择", "## Design Source and Selection"),
    ("## 设计令牌（实际值）", "## Design Tokens (Actual Values)"),
    ("## 文字样式（实际值）", "## Text Styles (Actual Values)"),
    ("## PAGE 与节点", "## PAGEs and Nodes"),
    ("## PAGE 关键规格", "## PAGE Key Specifications"),
    ("## 状态覆盖", "## State Coverage"),
    ("## 设计代码", "## Design Code"),
    ("## 断言范围", "## Assertion Scope"),
    ("## 资产清单", "## Asset List"),
    ("## 差异与待确认", "## Differences and Pending Confirmation"),
    ("## UI 评审", "## UI Review"),
]
source_sections = (
    [("## HTML 设计稿", "## HTML Design Docs"), ("## HTML 读取记录", "## HTML Read Records")]
    if html_source
    else [("## MCP 读取记录", "## MCP Read Records")]
)
for zh, en in required_sections + source_sections:
    if zh not in text and en not in text:
        errors.append(f"missing section: {zh} / {en}")

if not html_source and not figma_source:
    errors.append(
        "Design Source and Selection must state Figma MCP AI automatic design, Manual Figma design, or Design-to-HTML"
    )
if html_source and figma_source:
    errors.append(
        "Design Source and Selection must select exactly one design source (Figma or Design-to-HTML), not both"
    )
if not re.search(r"^- (?:设计来源状态|Design source status)[:：]\s*APPROVED\s*$", source_section, re.M):
    errors.append("Design Source and Selection must mark '- 设计来源状态：APPROVED' / '- Design source status: APPROVED' before stage 06 starts")

if html_source and require_framework:
    if not provenance_value.strip():
        errors.append(
            "Design Source and Selection must declare '- HTML provenance: User-provided HTML | "
            "AI-authored from requirements | Figma-to-HTML (AI conversion)'"
        )
    elif sum((provenance_user, provenance_ai, provenance_figma)) != 1:
        errors.append(
            "HTML provenance must select exactly one of User-provided HTML, "
            "AI-authored from requirements, or Figma-to-HTML (AI conversion)"
        )

required_inputs = [("需求与 AC", "requirements and AC"), ("设计规范", "design conventions")]
if html_source:
    required_inputs.append(("HTML 设计稿", "HTML design"))
else:
    required_inputs.append(("Figma MCP", "Figma MCP"))
input_section = section_any(text, *INPUT_SEC)
if not input_section:
    errors.append(f"missing section: {INPUT_SEC[0]} / {INPUT_SEC[1]}")
else:
    missing_inputs = [
        zh for zh, en in required_inputs
        if zh not in input_section and en.lower() not in input_section.lower()
    ]
    if missing_inputs:
        errors.append("Design Inputs and Style References table is missing: " + ", ".join(missing_inputs))

# --- Target platform declaration (Change-level) ---
target_platforms = declared_platforms()
if require_framework:
    if target_platforms is None:
        errors.append(
            "design/user-stories.md must declare '- Target platforms: <web|app|android|ios|harmonyos|mini-program|h5|desktop|pda> ...'"
        )
    elif not target_platforms:
        errors.append("design/user-stories.md Target platforms declares no usable platform")
    else:
        unknown = [p for p in target_platforms if p not in PLATFORMS]
        if unknown:
            errors.append(
                "design/user-stories.md Target platforms contains unsupported value(s): "
                + ", ".join(unknown)
                + f" (allowed: {', '.join(sorted(PLATFORMS))})"
            )

# --- Design source identity records ---
if figma_source or provenance_figma:
    figma_refs = re.findall(r"https://(?:www\.)?figma\.com/[^\s)）]*|node-id=[A-Za-z0-9:%-]+|fileKey[=:][A-Za-z0-9]+", text, re.I)
    figma_refs += re.findall(r"FIGMA-[A-Za-z0-9-]+", text)
    if not figma_refs:
        errors.append("Figma 文件未登记：至少登记真实 Figma 链接、node-id、fileKey 或 FIGMA-ID")

# --- Token actual values ---
token_section = section_any(text, *TOKEN_SEC)
token_rows = table_rows(token_section, skip_first=("变量", "Variable", "Token", "变量名"))
if not token_rows:
    errors.append("设计令牌至少需要 1 条实际值（颜色/间距/圆角等），变量名和数量不算规格")
elif len(token_rows) < 3:
    advisories.append(f"设计令牌仅 {len(token_rows)} 条实际值；建议覆盖颜色/间距/圆角至少 3 条")
color_rows = [r for r in token_rows if len(r) >= 3 and re.search(r"#[0-9a-fA-F]{3,8}", r[2])]
px_rows = [r for r in token_rows if len(r) >= 3 and re.search(r"\d+(?:\.\d+)?px", r[2])]
if not color_rows:
    errors.append("设计令牌必须至少包含 1 条带 hex 的颜色实际值")
elif len(color_rows) < 2:
    advisories.append("设计令牌仅 1 条 hex 颜色实际值；建议至少 2 条（主色/文字色等）")
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
type_section = section_any(text, *TYPE_SEC)
type_rows = table_rows(type_section, skip_first=("样式", "Style", "Text style"))
if not type_rows:
    errors.append("文字样式至少需要 1 条实际值（字体/字重/字号/行高/字距）")
elif len(type_rows) < 3:
    advisories.append(f"文字样式仅 {len(type_rows)} 条实际值；建议覆盖标题/正文/辅助文字至少 3 条")
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

# --- PAGE rows (source-specific reference) ---
page_section = section_any(text, *PAGE_SEC)
page_rows = table_rows(page_section, skip_first=("PAGE ID",))
page_header = table_header(page_section)
platform_index = header_index(page_header, "platform") if page_header else -1
if platform_index < 0 and page_header:
    platform_index = header_index(page_header, "平台")
pages = page_ids_from_rows(page_rows)
if not pages:
    errors.append("PAGE 与节点 must declare at least one PAGE-###; use 设计来源状态：N/A + 无 UI 理由 when no UI.")

html_files = {}
page_platforms = []
if require_framework and platform_index < 0:
    errors.append("PAGEs and Nodes table must carry a Platform column (web/app/android/ios/harmonyos/mini-program/h5/desktop/pda)")

for pid in pages:
    row = next((r for r in page_rows if r and pid in r[0]), None)
    if not row or len(row) < 3:
        errors.append(f"{pid}: PAGE 与节点 row incomplete (source reference/size/state)")
        continue
    if not re.search(r"\d+\s*[×x]\s*\d+", " | ".join(row)):
        errors.append(f"{pid}: missing frame/viewport size (e.g. 1440×900 or 375×812)")
    platform = normalize_platform(cell_at(row, platform_index)) if platform_index >= 0 else ""
    if require_framework and not platform:
        errors.append(
            f"{pid}: Platform must be a canonical value ({', '.join(sorted(PLATFORMS))})"
        )
    elif platform and platform not in PLATFORMS:
        errors.append(f"{pid}: unknown platform {cell_at(row, platform_index)!r}")
    page_platforms.append(platform)

    if html_source:
        ref = html_page_ref(row)
        if not ref:
            errors.append(f"{pid}: HTML design source must reference a real .html design file")
            continue
        path = resolve_asset(ref)
        if not path:
            errors.append(f"{pid}: HTML design file does not exist: {ref}")
            continue
        html_files[pid] = path
        html_text = path.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"<!doctype\s+html|<html", html_text, re.I):
            errors.append(f"{pid}: {ref} is not an HTML document")
        if "data-node-id=" not in html_text:
            errors.append(f"{pid}: {ref} must tag key blocks with data-node-id for the assertion table")
        if (
            not re.search(r"--[A-Za-z0-9_-]+\s*:", html_text)
            and "tokens.css" not in html_text
            and not (HTML_DIR / "tokens.css").is_file()
        ):
            errors.append(
                f"{pid}: {ref} must embed design tokens as CSS custom properties or reference tokens.css"
            )
        if re.search(r"(?:src|href)\s*=\s*[\"']https?://|@import\s+url\(\s*[\"']?https?://|url\(\s*[\"']?https?://", html_text, re.I):
            errors.append(f"{pid}: {ref} must be self-contained; remove external network dependencies")
    else:
        if not re.search(r"\d+\s*:\s*\d+", " ".join(row)):
            errors.append(f"{pid}: missing real Figma node id")

if html_source:
    if not HTML_README.is_file():
        errors.append(f"missing HTML design README: {HTML_README.relative_to(ROOT)}")
    if not HTML_INDEX.is_file():
        errors.append(f"missing HTML review entry: {HTML_INDEX.relative_to(ROOT)}")

# --- Platform coverage ---
if target_platforms:
    declared = [p for p in target_platforms if p in PLATFORMS]
    present = count_pages_by_platform(page_platforms)
    if require_framework:
        for platform in declared:
            if present.get(platform, 0) < 1:
                errors.append(
                    f"target platform {platform!r} declared in design/user-stories.md has no PAGE"
                )
    extra = sorted(set(present) - set(declared)) if declared else []
    if extra:
        errors.append(
            "PAGEs use platform(s) not declared in design/user-stories.md: " + ", ".join(extra)
        )

# --- Per-PAGE specs ---
spec_section = section_any(text, *SPEC_SEC)
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
state_section = section_any(text, *STATE_SEC)
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
            if not any(k in decision.lower() for k in ("决策", "审批", "decision", "approv")):
                errors.append(f"{pid}/{cells[1]}: state without a design frame needs an explicit 07 decision/approval")

# --- Design code + compact layout assertion contract ---
if not CODE_README.is_file():
    errors.append(f"missing design-code README: {CODE_README.relative_to(ROOT)}")

code_text_by_page = {}
for pid in pages:
    matches = sorted(CODE_DIR.glob(f"{pid}.*")) if CODE_DIR.is_dir() else []
    code_file = next((p for p in matches if p.suffix.lower() in {".tsx", ".jsx", ".vue"}), None)
    if not code_file:
        errors.append(f"missing design code for {pid}: {CODE_DIR.relative_to(ROOT)}/{pid}.vue (or .tsx/.jsx for React)")
    else:
        code_text_by_page[pid] = code_file.read_text(encoding="utf-8")

layout_required = LAYOUT_REQUIRED_NEW if require_framework else LAYOUT_REQUIRED
layout = load_csv(LAYOUT, layout_required, "figma-layout.csv")
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
        if require_framework:
            platform = normalize_platform(row.get("platform", ""))
            if platform not in PLATFORMS:
                errors.append(
                    f"figma-layout.csv: {pid}/{element_id} platform must be a canonical value ({', '.join(sorted(PLATFORMS))})"
                )
            else:
                page_row = next((r for r in page_rows if r and pid in r[0]), None)
                page_platform = (
                    normalize_platform(cell_at(page_row, platform_index))
                    if page_row and platform_index >= 0 else ""
                )
                if page_platform and platform != page_platform:
                    errors.append(
                        f"figma-layout.csv: {pid}/{element_id} platform {platform!r} does not match PAGE platform {page_platform!r}"
                    )
            if not re.fullmatch(r"\d+[x×]\d+", row.get("viewport", "").strip().lower()):
                errors.append(f"figma-layout.csv: {pid}/{element_id} viewport must look like 1440x900 or 375x812")
        code_text = code_text_by_page.get(pid, "")
        if code_text and f'data-node-id="{nid}"' not in code_text:
            errors.append(
                f"figma-layout.csv: {pid}/{element_id} figma_node_id {nid!r} "
                f"not found in {pid} design code"
            )
        if html_source and pid in html_files:
            html_text = html_files[pid].read_text(encoding="utf-8", errors="replace")
            if nid and f'data-node-id="{nid}"' not in html_text:
                errors.append(
                    f"figma-layout.csv: {pid}/{element_id} figma_node_id {nid!r} "
                    f"not found in {html_files[pid].relative_to(ROOT)}"
                )
    layout_pages = {pid for pid, _ in layout_pairs}
    for pid in pages:
        if pid not in layout_pages:
            errors.append(f"figma-layout.csv: PAGE {pid} has no assertion rows")

# --- Requirements coverage: completeness + consistency ---
coverage_section = section_any(text, *COVERAGE_SEC)
coverage_header = table_header(coverage_section)
coverage_rows = table_rows(coverage_section, skip_first=("Requirement", "需求", "Requirement ID", "需求 ID"))


def cov_col(*names):
    for name in names:
        idx = header_index(coverage_header, name)
        if idx >= 0:
            return idx
    return -1


if not coverage_section:
    if require_framework:
        errors.append(
            "UI design must include '## Requirements Coverage' / '## 需求覆盖': every AC and US maps to PAGE(s) per declared platform, and every PAGE maps back to at least one requirement."
        )
else:
    req_i = cov_col("Requirement", "需求", "Requirement ID", "需求 ID")
    type_i = cov_col("Type", "类型")
    plat_i = cov_col("Platform", "平台")
    page_i = cov_col("PAGE / Block", "PAGE/Block", "PAGE", "页面/区块")
    cov_i = cov_col("Coverage", "覆盖")
    note_i = cov_col("Evidence / notes", "Evidence/notes", "Notes", "证据/说明", "证据")
    missing_cols = [
        name for name, idx in (
            ("Requirement", req_i), ("Type", type_i), ("Platform", plat_i),
            ("PAGE / Block", page_i), ("Coverage", cov_i), ("Evidence / notes", note_i),
        ) if idx < 0
    ]
    if missing_cols:
        errors.append("Requirements Coverage table is missing columns: " + ", ".join(missing_cols))
    elif not coverage_rows:
        errors.append("Requirements Coverage table must contain at least one row")
    else:
        stories_text = USER_STORIES.read_text(encoding="utf-8") if USER_STORIES.is_file() else ""
        us_ids = set(re.findall(r"US-\d{3}", stories_text))
        ac_ids = set(re.findall(r"AC-\d{3}", stories_text))
        if not us_ids or not ac_ids:
            errors.append("design/user-stories.md must declare US-### and AC-### IDs so coverage can be verified")
        declared = set(target_platforms or [])
        page_platform = {pid: (page_platforms[i] if i < len(page_platforms) else "") for i, pid in enumerate(pages)}
        covered_pages = set()
        req_rows = {}
        allowed_types = {"AC", "US", "FLOW", "NODE", "DO", "BR", "ROLE", "CAP", "OTHER"}
        source_ids = {
            "FLOW": (ROOT / "docs/product/workflows.md", r"FLOW-\d{3}"),
            "NODE": (ROOT / "docs/product/workflows.md", r"NODE-\d{3}-\d+"),
            "DO": (ROOT / "docs/product/data-objects.csv", r"DO-\d{3}"),
            "BR": (ROOT / "docs/product/business-rules.md", r"BR-\d{3}"),
        }
        for cells in coverage_rows:
            req = cell_at(cells, req_i).strip().strip("`")
            rtype = cell_at(cells, type_i).strip().upper()
            plat_raw = cell_at(cells, plat_i).strip()
            plat = "all" if plat_raw.casefold() in {"all", "全部", "通用"} else normalize_platform(plat_raw)
            page_cell = cell_at(cells, page_i)
            cov = cell_at(cells, cov_i).strip().upper()
            notes = cell_at(cells, note_i).strip()
            if not req:
                errors.append(f"Requirements Coverage row has an empty requirement: {cells}")
                continue
            if rtype not in allowed_types:
                errors.append(f"Requirements Coverage {req}: Type must be one of {sorted(allowed_types)}")
            prefix = req.split("-")[0]
            expected_type = {"AC": "AC", "US": "US", "FLOW": "FLOW", "NODE": "NODE", "DO": "DO", "BR": "BR"}.get(prefix)
            if expected_type and rtype != expected_type:
                errors.append(f"Requirements Coverage {req}: Type {rtype!r} does not match the ID prefix")
            if req.startswith("AC-") and req not in ac_ids:
                errors.append(f"Requirements Coverage: unknown AC {req} (not in design/user-stories.md)")
            elif req.startswith("US-") and req not in us_ids:
                errors.append(f"Requirements Coverage: unknown US {req} (not in design/user-stories.md)")
            elif expected_type in source_ids:
                src, pattern = source_ids[expected_type]
                if src.is_file():
                    known = set(re.findall(pattern, src.read_text(encoding="utf-8", errors="replace")))
                    if known and req not in known:
                        errors.append(f"Requirements Coverage: unknown {expected_type} {req} (not in {src.relative_to(ROOT)})")
            if cov not in {"FULL", "PARTIAL", "N/A"}:
                errors.append(f"Requirements Coverage {req}: Coverage must be FULL/PARTIAL/N/A")
            if cov == "N/A":
                if not notes or notes.casefold() in {"-", "—", "none", "n/a"}:
                    errors.append(f"Requirements Coverage {req}: N/A requires a reason in Evidence / notes")
                if PAGE_RE.search(page_cell):
                    errors.append(f"Requirements Coverage {req}: N/A rows must not reference a PAGE")
            elif not PAGE_RE.search(page_cell):
                errors.append(f"Requirements Coverage {req}: {cov} coverage requires at least one PAGE reference")
            if cov == "PARTIAL" and not re.search(r"approv|审批|批准", notes, re.I):
                errors.append(f"Requirements Coverage {req}: PARTIAL requires an approver note; complete it or mark N/A with a reason")
            if plat not in {"all"} and declared and plat not in declared:
                errors.append(f"Requirements Coverage {req}: platform {plat_raw!r} is not declared in design/user-stories.md")
            refs = PAGE_RE.findall(page_cell)
            for pid in refs:
                if pid not in pages:
                    errors.append(f"Requirements Coverage {req}: PAGE {pid} does not exist in the PAGE list")
                    continue
                covered_pages.add(pid)
                page_plat = page_platform.get(pid, "")
                if plat != "all" and page_plat and plat != page_plat:
                    errors.append(f"Requirements Coverage {req}: platform {plat!r} does not match PAGE {pid} platform {page_plat!r}")
                page_part = pid
                for eid in re.findall(r"PAGE-\d{3}-E\d+", page_cell):
                    if eid.rsplit("-", 1)[0] == page_part and (page_part, eid) not in layout_pairs:
                        errors.append(f"Requirements Coverage {req}: block {eid} has no figma-layout.csv assertion row")
            req_rows.setdefault(req, []).append((plat, cov, notes))
        for req in sorted(us_ids | ac_ids):
            rows_for = req_rows.get(req, [])
            if not rows_for:
                errors.append(f"Requirements Coverage: {req} has no coverage row")
                continue
            if declared:
                for platform in sorted(declared):
                    candidates = [r for r in rows_for if r[0] in {platform, "all"}]
                    if not any(r[1] in {"FULL", "N/A"} for r in candidates):
                        errors.append(f"Requirements Coverage: {req} has no FULL or N/A row for platform {platform}")
        for pid in pages:
            if pid not in covered_pages:
                errors.append(f"Requirements Coverage: PAGE {pid} maps back to no requirement")

# --- HTML design records (HTML source only) ---
if html_source:
    html_docs = section_any(text, *HTML_DOCS_SEC)
    if "ui-html/" not in html_docs or ".html" not in html_docs.lower():
        errors.append("## HTML Design Docs must name the design directory and its HTML review entry")
    records_section = section_any(text, *HTML_RECORDS_SEC)
    records = table_rows(records_section, skip_first=("步骤/命令", "Step/Command", "Step", "Command"))
    successful = []
    for cells in records:
        joined = " ".join(cells)
        if re.search(r"成功|success|passed|pass", joined, re.I) and re.search(
            r"render|measure|browser|playwright|dom", joined, re.I
        ):
            successful.append(cells)
    if not successful:
        errors.append(
            "HTML Read Records need at least one successful render/measure record for the HTML design files"
        )
    if provenance_figma:
        conversion = [
            cells for cells in records
            if re.search(r"figma", " ".join(cells), re.I)
            and re.search(r"convert|transcod|转换|转码|html", " ".join(cells), re.I)
            and re.search(r"成功|success|passed|pass", " ".join(cells), re.I)
        ]
        if not conversion:
            errors.append(
                "Figma-to-HTML provenance requires a successful Figma read/conversion record "
                "under HTML Read Records"
            )

code_section = section_any(text, *CODE_SEC)
if "figma-code/" not in code_section:
    errors.append("## 设计代码 / ## Design Code must reference figma-code/")
if html_source:
    if "ui-html/" not in code_section and "HTML" not in code_section:
        errors.append("## Design Code must record that target-framework design code was transcribed from the HTML design documents")
else:
    if "get_design_context" not in code_section:
        errors.append("## Design Code must reference get_design_context")
if require_framework:
    m_framework = re.search(r"^- (?:目标框架|Target framework)[:：]\s*\S", code_section, re.M)
    m_ext = re.search(r"^- (?:设计代码扩展名|Design code extension)[:：]\s*(\.(?:vue|tsx|jsx))\s*$", code_section, re.M)
    if not m_framework:
        errors.append("## 设计代码 / ## Design Code must declare '- 目标框架：...' / '- Target framework: ...' (technology-decisions.md)")
    if not m_ext:
        errors.append("## 设计代码 / ## Design Code must declare '- 设计代码扩展名：.vue/.tsx/.jsx' / '- Design code extension: .vue/.tsx/.jsx'")
    if not html_source and "figma-design-to-code" not in code_section:
        errors.append("## 设计代码 must record the official figma-design-to-code Skill usage")
    if m_framework:
        framework = code_section[m_framework.start():].splitlines()[0]
        if "Vue" in framework or "vue" in framework:
            expected = {".vue"}
        elif "React" in framework or "react" in framework:
            expected = {".tsx", ".jsx"}
        else:
            expected = set()
            errors.append("Target framework must name Vue or React so the code extension can be verified")
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
assertion_section = section_any(text, *ASSERT_SEC)
if "figma-layout.csv" not in assertion_section:
    errors.append("## 断言范围 / ## Assertion Scope must reference figma-layout.csv")

# --- Assets: only real image/SVG files; reference screenshots are not assets ---
asset_section = section_any(text, *ASSET_SEC)
if re.search(r"资产：无|无图片/SVG 资产|无资产|Assets: none|no images/SVG assets|no assets", asset_section, re.I):
    asset_rows = []
else:
    asset_rows = table_rows(asset_section, skip_first=("资产", "Asset"))
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

# --- Source read records ---
if not html_source:
    mcp_text = section_any(text, *MCP_SEC)
    mcp_rows = table_rows(mcp_text, skip_first=("工具/命令", "Tool/Command", "Tool"))
    tools = re.findall(r"(get_design_context|get_metadata|get_variable_defs|get_screenshot|use_figma|figma\s*mcp)", mcp_text, re.I)
    if not tools:
        errors.append("MCP 读取记录缺少真实 Figma MCP 工具调用")
    for required_tool in ("get_metadata", "get_variable_defs"):
        if not any(
            required_tool in " ".join(r).lower()
            and any(k in " ".join(r).lower() for k in ("成功", "success", "passed", "pass"))
            for r in mcp_rows
        ):
            errors.append(f"MCP Read Records lack a successful {required_tool} call; node geometry must come from a real read")

# --- UI review ---
ui_section = section_any(text, *UI_SEC)
if not re.search(r"^- (?:UI 评审状态|UI review status)[:：]\s*APPROVED\s*$", ui_section, re.M):
    errors.append("UI Review must mark '- UI 评审状态：APPROVED' / '- UI review status: APPROVED'")
if not re.search(r"^- (?:评审人|Reviewer)[:：]\s*.+$", ui_section, re.M):
    errors.append("UI Review is missing '- 评审人：' / '- Reviewer: '")
m = re.search(r"^- (?:评审证据|Review evidence)[:：]\s*(.+)$", ui_section, re.M)
if not m:
    errors.append("UI Review is missing '- 评审证据：' / '- Review evidence: '")
else:
    ev = m.group(1).strip()
    if not resolve_asset(ev) and not (base / ev).is_file() and not (ROOT / ev).is_file():
        errors.append(f"UI review evidence file does not exist: {ev}")
if coverage_section and not re.search(r"^- (?:覆盖评审状态|Coverage review status)[:：]\s*APPROVED\s*$", ui_section, re.M):
    errors.append("UI Review must mark '- 覆盖评审状态：APPROVED' / '- Coverage review status: APPROVED' after the owner confirms requirement coverage is complete and consistent")
if coverage_section and not re.search(r"^- (?:覆盖评审人|Coverage reviewed by)[:：]\s*.+$", ui_section, re.M):
    errors.append("UI Review is missing '- 覆盖评审人：' / '- Coverage reviewed by: '")

for line_no, line in enumerate(text.splitlines(), 1):
    if line.lstrip().startswith("#"):
        continue
    if re.search(r"PENDING|TODO|TBD|\[填充\]|<实际值>|<\.\.\.>", line, re.I):
        warnings.append(f"{AUDIT.relative_to(ROOT)}:{line_no}: unresolved placeholder remains")

if errors:
    for e in errors:
        print("ERROR:", e)
for w in warnings:
    print("WARN:", w)
for a in advisories:
    print("WARN (advisory):", a)
if errors or (strict and warnings):
    print(f"UI design contract check failed: {len(errors)} error(s), {len(warnings)} warning(s).")
    sys.exit(1)
source_label = "Design-to-HTML" if html_source else "Figma"
print(f"UI design contract passed ({source_label}): {len(pages)} PAGE(s), {len(color_rows)} color token(s), "
      f"{len(type_rows)} text style(s), {len(code_text_by_page)} design-code file(s), "
      f"{len(layout_pairs)} assertion(s), {len(set(p for p in page_platforms if p))} platform(s).")
