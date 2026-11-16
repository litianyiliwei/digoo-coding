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
    "设计决策": ["### 范围与非目标", "### 关键决策与权衡", "### 现有代码变更影响", "### 设计任务分解与接口范围", "### 设计缺口与准入结论"],
    "接口设计": ["### 接口清单", "### 接口边界清单", "### 契约与错误语义", "### 接口追踪"],
    "前端详细设计": [
        "### 路由与组件树", "### 设计令牌与实现映射", "### PAGE→BLOCK→Figma 规格",
        "### PAGE→BLOCK→组件映射", "### 组件职责与状态", "### 事件处理",
        "### 状态覆盖", "### 测试映射", "### 响应式与视口规则", "### 页面几何与保真断言",
    ],
    "后端详细设计": ["### API 执行链", "### API→IO 映射", "### IO 契约", "### 数据模型与迁移", "### 非数据库 IO", "### 领域类型与方法", "### 错误与一致性", "### 共享关注点", "### 测试覆盖", "### 未决决策"],
    "测试设计": ["### 测试策略", "### 测试环境与替身", "### 人工验证"],
}
SUBSECTION_ALIASES = {
    "### 范围与非目标": ["### 范围与非目标", "### Scope and Non-Goals"],
    "### 关键决策与权衡": ["### 关键决策与权衡", "### Key Decisions and Trade-offs"],
    "### 现有代码变更影响": ["### 现有代码变更影响", "### Existing Code Change Impact"],
    "### 设计任务分解与接口范围": ["### 设计任务分解与接口范围", "### Design Task Breakdown and Interface Scope"],
    "### 设计缺口与准入结论": ["### 设计缺口与准入结论", "### Design Gaps and Entry Conclusion"],
    "### 接口清单": ["### 接口清单", "### Interface Inventory"],
    "### 接口边界清单": ["### 接口边界清单", "### Interface Boundary Inventory"],
    "### 契约与错误语义": ["### 契约与错误语义", "### Contracts and Error Semantics"],
    "### 接口追踪": ["### 接口追踪", "### Interface Traceability"],
    "### 路由与组件树": ["### 路由与组件树", "### Routing and Component Tree"],
    "### 设计令牌与实现映射": ["### 设计令牌与实现映射", "### Design Tokens and Implementation Mapping"],
    "### PAGE→BLOCK→Figma 规格": ["### PAGE→BLOCK→Figma 规格", "### PAGE→BLOCK→Figma Specifications"],
    "### PAGE→BLOCK→组件映射": ["### PAGE→BLOCK→组件映射", "### PAGE→BLOCK→Component Mapping"],
    "### 组件职责与状态": ["### 组件职责与状态", "### Component Responsibilities and States"],
    "### 事件处理": ["### 事件处理", "### Event Handling"],
    "### 状态覆盖": ["### 状态覆盖", "### State Coverage"],
    "### 测试映射": ["### 测试映射", "### Test Mapping"],
    "### 响应式与视口规则": ["### 响应式与视口规则", "### Responsive and Viewport Rules"],
    "### 页面几何与保真断言": ["### 页面几何与保真断言", "### Page Geometry and Fidelity Assertions"],
    "### API 执行链": ["### API 执行链", "### API Execution Chain"],
    "### API→IO 映射": ["### API→IO 映射", "### API→IO Mapping"],
    "### IO 契约": ["### IO 契约", "### IO Contracts"],
    "### 数据模型与迁移": ["### 数据模型与迁移", "### Data Model and Migration"],
    "### 非数据库 IO": ["### 非数据库 IO", "### Non-Database IO"],
    "### 领域类型与方法": ["### 领域类型与方法", "### Domain Types and Methods"],
    "### 错误与一致性": ["### 错误与一致性", "### Errors and Consistency"],
    "### 共享关注点": ["### 共享关注点", "### Shared Concerns"],
    "### 测试覆盖": ["### 测试覆盖", "### Test Coverage"],
    "### 未决决策": ["### 未决决策", "### Open Decisions"],
    "### 测试策略": ["### 测试策略", "### Test Strategy"],
    "### 测试环境与替身": ["### 测试环境与替身", "### Test Environment and Doubles"],
    "### 人工验证": ["### 人工验证", "### Manual Verification"],
}


def has_subsection(body: str, canonical: str) -> bool:
    return any(variant in body for variant in SUBSECTION_ALIASES.get(canonical, [canonical]))


def extract_subsection(body: str, canonical: str) -> str:
    for variant in SUBSECTION_ALIASES.get(canonical, [canonical]):
        start = body.find(variant)
        if start < 0:
            continue
        rest = body[start + len(variant):]
        end = rest.find("\n### ")
        return rest[:end if end >= 0 else len(rest)].strip()
    return ""


SECTION_ALIASES = {
    "设计决策": ["设计决策", "Design Decisions"],
    "接口设计": ["接口设计", "Interface Design"],
    "前端详细设计": ["前端详细设计", "Frontend Detailed Design"],
    "后端详细设计": ["后端详细设计", "Backend Detailed Design"],
    "测试设计": ["测试设计", "Test Design"],
}


def body_for(sections, canonical):
    for alias in SECTION_ALIASES.get(canonical, [canonical]):
        if alias in sections:
            return "\n".join(sections[alias])
    return ""

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
    for required_sub in required:
        if not has_subsection(body, required_sub):
            errors.append(f"## {section} missing required subsection: {required_sub}")

# Cross-boundary interfaces must point at the machine-readable catalog unless N/A.
interface_body = body_for(sections, "接口设计")
if not interface_body.strip().upper().startswith("N/A") and has_subsection(interface_body, "### 接口边界清单"):
    boundary = extract_subsection(interface_body, "### 接口边界清单")
    if not boundary.strip().upper().startswith("N/A") and "interface-catalog.csv" not in boundary:
        errors.append("## 接口设计 ### 接口边界清单 / ### Interface Boundary Inventory must reference interface-catalog.csv unless N/A")

# Existing-code impact must be concrete when the Change modifies existing code.
decision_body = body_for(sections, "设计决策")
if not decision_body.strip().upper().startswith("N/A") and has_subsection(decision_body, "### 现有代码变更影响"):
    existing_code = extract_subsection(decision_body, "### 现有代码变更影响")
    if not existing_code:
        errors.append("### 现有代码变更影响 / ### Existing Code Change Impact is empty; write impact analysis or N/A + reason")
    elif not existing_code.upper().startswith("N/A"):
        if not any(k in existing_code for k in ("代码地址", "仓库", "分支", "commit", "code address", "repository", "branch")):
            errors.append("### 现有代码变更影响 / ### Existing Code Change Impact must record code address/repository/branch/commit when modifying existing code")
        if not any(k in existing_code for k in ("文件", "类", "函数", "接口", "表", "测试", "file", "class", "function", "interface", "table", "test")):
            errors.append("### 现有代码变更影响 / ### Existing Code Change Impact must list affected files/classes/functions/interfaces/tables/tests")
        if not any(k in existing_code for k in ("修改策略", "兼容", "回滚", "迁移", "change strategy", "compatibility", "rollback", "migration")):
            errors.append("### 现有代码变更影响 / ### Existing Code Change Impact must state change strategy/compatibility/migration/rollback")

# UI Changes must carry actual tokens, not only variable names.
audit = ROOT / "openspec/changes" / change / "design/figma-audit.md"
ui_change = False
if audit.is_file():
    audit_text = audit.read_text(encoding="utf-8")
    ui_change = not re.search(r"^- (?:设计来源状态|Design source status）[:：]\s*N/A\s*$", audit_text, re.M)
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

    responsive_body = body_for(sections, "前端详细设计")
    if has_subsection(responsive_body, "### 响应式与视口规则"):
        resp = extract_subsection(responsive_body, "### 响应式与视口规则")
        if "1440" not in resp:
            errors.append("### 响应式与视口规则 / ### Responsive and Viewport Rules must state the 1440×900 baseline")
        if not re.search(r"\|.*PAGE", resp):
            warnings.append("### 响应式与视口规则 / ### Responsive and Viewport Rules should contain a per-PAGE table")

if errors:
    for e in errors:
        print("ERROR:", e)
for w in warnings:
    print("WARN:", w)
if errors:
    print(f"Design section check failed: {len(errors)} issue(s).")
    sys.exit(1)
print("Design section check passed: design.md has the required unified subsections.")
