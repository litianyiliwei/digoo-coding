#!/usr/bin/env python3
"""Validate required subsections inside the unified design.md."""
from pathlib import Path
import csv, re, sys

ROOT = Path(__file__).resolve().parents[1]
args = sys.argv[1:]
change = None
if "--change" in args:
    idx = args.index("--change")
    if idx + 1 >= len(args):
        print("Usage: check-design-sections.py --change <change-id>", file=sys.stderr)
        sys.exit(2)
    change = args[idx + 1]
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", change):
        print("Invalid change-id", file=sys.stderr)
        sys.exit(2)
    args = args[:idx] + args[idx + 2:]
args = [a for a in args if a != "--strict"]
if args or not change:
    print("Usage: check-design-sections.py --change <change-id>", file=sys.stderr)
    sys.exit(2)

DESIGN = ROOT / "openspec/changes" / change / "design.md"
if not DESIGN.is_file():
    print(f"ERROR: missing design.md: {DESIGN.relative_to(ROOT)}")
    sys.exit(1)

text = DESIGN.read_text(encoding="utf-8")
lines = text.splitlines()
sections = {}
current = None
for line in lines:
    if line.startswith("## ") and not line.startswith("### "):
        current = line[3:].strip()
        sections[current] = []
    elif current is not None:
        sections[current].append(line)

REQUIRED = {
    "设计决策": ["### 范围与非目标", "### 关键决策与权衡", "### 设计任务分解与接口范围", "### 设计缺口与准入结论"],
    "接口设计": ["### 接口清单", "### 契约与错误语义", "### 接口追踪"],
    "前端详细设计": [
        "### 路由与组件树", "### 设计令牌与实现映射", "### PAGE→BLOCK→Figma 规格",
        "### PAGE→BLOCK→组件映射", "### 组件职责与状态", "### 事件处理",
        "### 状态覆盖", "### 测试映射", "### 响应式与视口规则", "### 页面几何与保真断言",
    ],
    "后端详细设计": ["### API 执行链", "### API→IO 映射", "### IO 契约", "### 数据模型与迁移", "### 非数据库 IO", "### 领域类型与方法", "### 错误与一致性", "### 共享关注点", "### 测试覆盖", "### 未决决策"],
    "测试设计": ["### 测试策略", "### 测试环境与替身", "### 人工验证"],
}
SECTION_ALIASES = {
    "设计决策": ["设计决策"],
    "接口设计": ["接口设计"],
    "前端详细设计": ["前端详细设计"],
    "后端详细设计": ["后端详细设计"],
    "测试设计": ["测试设计"],
}

errors, warnings = [], []
frontend_body = ""
for section, required in REQUIRED.items():
    aliases = SECTION_ALIASES[section]
    present = next((a for a in aliases if a in sections), None)
    if not present:
        errors.append(f"design.md missing section: ## {section}")
        continue
    body = "\n".join(sections[present]).strip()
    if not body:
        errors.append(f"## {section} is empty; fill content or write N/A with a reason")
        continue
    if section == "前端详细设计":
        frontend_body = body
    if re.search(r"x-api-scope:\s*none", body, re.I) and "### " not in body:
        continue
    if body.upper().startswith("N/A") and "### " not in body:
        continue
    for sub in required:
        if sub not in body:
            errors.append(f"## {section} missing required subsection: {sub}")

# UI Changes must carry actual tokens, not only variable names.
audit = ROOT / "openspec/changes" / change / "design/figma-audit.md"
ui_change = False
if audit.is_file():
    audit_text = audit.read_text(encoding="utf-8")
    ui_change = not re.search(r"^- 设计来源状态：N/A\s*$", audit_text, re.M)
if ui_change and frontend_body:
    if not re.search(r"--[A-Za-z0-9_-]+", frontend_body):
        errors.append("UI 前端详细设计必须包含 token → CSS 变量/Element Plus 映射（例如 --color-brand）")
    if not re.search(r"\d+px", frontend_body):
        errors.append("UI 前端详细设计必须包含实际尺寸/字号/间距（px），不能只写变量名")
    if "figma-layout.csv" not in frontend_body:
        errors.append("UI 前端详细设计必须引用 design/figma-layout.csv（07 填写 route/dom_selector）")
    if "figma-code/" not in frontend_body:
        errors.append("UI 前端详细设计必须引用 design/figma-code/（get_design_context 落盘的设计代码）")
    if "check-figma-layout.py" not in frontend_body:
        errors.append("UI 前端详细设计必须写明运行态几何断言命令 check-figma-layout.py")
    if not re.search(r"1440\s*[×x]\s*900|1440", frontend_body):
        errors.append("UI 前端详细设计必须声明 1440×900 基准视口")
    if not re.search(r"(\.css|tokens?\.css|token 文件)", frontend_body, re.I):
        errors.append("UI 前端详细设计必须声明全局 token 文件路径，供 check-design-tokens.py 比对")

    layout = ROOT / "openspec/changes" / change / "design/figma-layout.csv"
    if not layout.is_file():
        errors.append("UI Change missing design/figma-layout.csv")
    else:
        with layout.open(newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            fields = set(reader.fieldnames or [])
            required_layout = {
                "page_id", "route", "element_id", "figma_node_id", "x", "y", "width",
                "height", "dom_selector", "assert_geometry", "assert_text",
                "tolerance_px", "text_content", "font_size", "font_weight",
            }
            missing = required_layout - fields
            if missing:
                errors.append("figma-layout.csv missing columns: " + ", ".join(sorted(missing)))
            else:
                rows = list(reader)
                if not rows:
                    errors.append("figma-layout.csv has no assertion rows")
                for row in rows:
                    where = f"{row.get('page_id','?')}/{row.get('element_id','?')}"
                    route = (row.get("route") or "").strip()
                    selector = (row.get("dom_selector") or "").strip()
                    if not route or route.upper() == "PENDING":
                        errors.append(f"{where}: route is not filled by 07")
                    if not selector or selector.upper() == "PENDING":
                        errors.append(f"{where}: dom_selector is not filled by 07")

    responsive = sections.get("前端详细设计", [])
    responsive_body = "\n".join(responsive)
    if "### 响应式与视口规则" in responsive_body:
        start = responsive_body.find("### 响应式与视口规则")
        end = responsive_body.find("\n### ", start + len("### 响应式与视口规则"))
        resp = responsive_body[start:end if end >= 0 else len(responsive_body)]
        if "1440" not in resp:
            errors.append("### 响应式与视口规则 must state the 1440×900 baseline")
        if not re.search(r"\|.*PAGE", resp):
            warnings.append("### 响应式与视口规则 should contain a per-PAGE table")

if errors:
    for e in errors:
        print("ERROR:", e)
for w in warnings:
    print("WARN:", w)
if errors:
    print(f"Design section check failed: {len(errors)} issue(s).")
    sys.exit(1)
print("Design section check passed: design.md has the required unified subsections.")
