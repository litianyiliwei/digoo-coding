#!/usr/bin/env python3
"""Validate the unified design.md and its ``Implementation Slice``.

Full mode (default) keeps the legacy five-section/subsection checks and the UI
contract checks. ``--slice-only`` validates only ``## Design Decisions`` and
``### Implementation Slice``; it is the 07 -> 08 hard gate and skips the other
sections and every UI check.

The slice rules follow the project module strategy (``gate_common.strategy``):

* ``none`` (missing/invalid layout has its own error) - no slice is required;
* ``footprint`` - only ``Owned paths`` and ``Integration paths`` are required;
  the capability/owner fields are optional and an owner of ``N/A`` is absent;
* ``module-packages`` - all eight fields are required; the primary capability
  and owner/related modules must exist in the registries, the owner must equal
  the capability's owner, owned/code-package paths must stay under the
  owner/related module roots, integration paths must match
  ``code-layout.json`` and carry a reason plus a task ID when declared (empty
  or ``N/A`` means no integration entries), and the module card must carry
  create/update wording (or ``N/A + reason``). Module card files are implicitly
  owned by ``check-change-footprint.py`` for every owner/related module path.

Reuses the shared parsers in ``gate_common``.
"""
from __future__ import annotations

from pathlib import Path
import csv
import re
import sys

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
import gate_common as gm  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

USAGE = (
    "Usage: check-design-sections.py --change <change-id> "
    "[--strict] [--slice-only]"
)

CHANGE_ID_RE = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*")
ABSOLUTE_PATH_RE = re.compile(r"^(?:/|[A-Za-z]:)")
WILDCARD_PATH_RE = re.compile(r"[*?]")
MODULE_CARD_ACTION_RE = re.compile(r"(?i)^(?:create|update)\b|^(?:新建|创建|更新)")
NA_REASON_RE = re.compile(r"(?i)^N/A\s*[+＋:：\-—]?\s*")
PLACEHOLDER_SEGMENT_RE = re.compile(r"<[^/>]+>")

REQUIRED_SLICE_FIELDS = {
    "module-packages": (
        ("primary", "Primary capability"),
        ("owner_module", "Owner module"),
        ("related_modules", "Related modules"),
        ("shape", "Slice type/coverage"),
        ("packages", "Code packages"),
        ("owned", "Owned paths"),
        ("integration", "Integration paths"),
        ("module_card", "Module card"),
    ),
    "footprint": (
        ("owned", "Owned paths"),
        ("integration", "Integration paths"),
    ),
}

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


def split_sections(text: str) -> dict:
    lines = text.splitlines()
    sections = {}
    current = None
    for line in lines:
        if line.startswith("## ") and not line.startswith("### "):
            current = line[3:].strip()
            sections[current] = []
        elif current is not None:
            sections[current].append(line)
    return sections


def body_for(sections, canonical):
    for alias in SECTION_ALIASES.get(canonical, [canonical]):
        if alias in sections:
            return "\n".join(sections[alias])
    return ""


# -- slice helpers ------------------------------------------------------------
def _is_na(value: str) -> bool:
    return (value or "").strip().upper().startswith("N/A")


def _norm_path(value: str) -> str:
    value = str(value or "").strip().replace("\\", "/")
    while value.startswith("./"):
        value = value[2:]
    value = re.sub(r"/+", "/", value)
    return value.strip("/")


def _path_problem(value: str) -> str:
    """Return why a slice path is unsafe, or ``""`` when it is acceptable."""
    raw = str(value or "").strip().replace("\\", "/")
    if ABSOLUTE_PATH_RE.match(raw):
        return "is an absolute path"
    segments = raw.split("/")
    if any(segment == "." for segment in segments):
        return "contains a '.' segment"
    if any(segment == ".." for segment in segments):
        return "contains a '..' segment"
    if WILDCARD_PATH_RE.search(raw):
        return "contains a wildcard character"
    return ""


def _slice_path_prefix(value: str) -> str:
    """Return the concrete prefix of an owned/package path.

    Approved design §5.4 writes owned paths as subtrees (``server/.../export/**``),
    so a strictly trailing ``/**`` is a subtree marker and is stripped before
    path-safety and containment checks. Only that exact trailing form is
    accepted; embedded ``*``/``?`` remain wildcards.
    """
    raw = str(value or "").strip().replace("\\", "/")
    if len(raw) > len("/**") and raw.endswith("/**"):
        return raw[: -len("/**")]
    return raw


def _within(path: str, roots: list[str]) -> bool:
    folded = _norm_path(path).casefold()
    for root in roots:
        normalized = _norm_path(root).casefold()
        if not normalized:
            continue
        if folded == normalized or folded.startswith(normalized + "/"):
            return True
    return False


def _real_values(items: list[str]) -> list[str]:
    return [item.strip() for item in items if item.strip() and not _is_na(item)]


def _integration_matches(relpath: str, pattern: str) -> bool:
    """Match a layout integration path, treating ``<org>`` segments as one segment."""
    if gm.path_matches(relpath, pattern):
        return True
    expanded = PLACEHOLDER_SEGMENT_RE.sub("*", pattern)
    return expanded != pattern and gm.path_matches(relpath, expanded)


def _module_card_problem(value: str) -> str:
    value = (value or "").strip()
    if not value:
        return "must not be empty"
    if _is_na(value):
        reason = NA_REASON_RE.sub("", value).strip()
        return "" if reason else "must be create/update wording or 'N/A + reason'"
    if MODULE_CARD_ACTION_RE.match(value):
        return ""
    return "must be create/update wording or 'N/A + reason'"


def check_slice(design_text: str, errors: list[str]) -> None:
    """Validate ``### Implementation Slice`` against the module strategy."""
    parsed = gm.parse_slice(design_text)
    try:
        strategy = gm.strategy(root=ROOT)
    except RuntimeError as exc:
        errors.append(str(exc))
        return
    if strategy == "none":
        return

    present = set(parsed["present"])
    required = REQUIRED_SLICE_FIELDS[strategy]
    required_fields = {field for field, _ in required}

    for field, label in required:
        if field not in present:
            errors.append(f"### Implementation Slice missing required field: {label}")

    capabilities = gm.load_capabilities(root=ROOT)
    modules = gm.load_modules(root=ROOT)
    layout = gm.load_code_layout(root=ROOT) or {}
    raw_patterns = layout.get("integration_paths") if isinstance(layout, dict) else None
    integration_patterns = (
        [item for item in raw_patterns if isinstance(item, str)]
        if isinstance(raw_patterns, list)
        else []
    )

    primary = ""
    if "primary" in present:
        value = (parsed["primary"] or "").strip()
        if not value or _is_na(value):
            if "primary" in required_fields:
                errors.append(
                    "### Implementation Slice field Primary capability "
                    "must not be empty or N/A"
                )
        else:
            primary = value
            if not gm.capability_rows(capabilities, primary):
                errors.append(
                    f"### Implementation Slice Primary capability {primary!r} "
                    "is not in docs/product/capabilities.csv"
                )

    if "shape" in present:
        value = (parsed["shape"] or "").strip()
        if (not value or _is_na(value)) and "shape" in required_fields:
            errors.append(
                "### Implementation Slice field Slice type/coverage "
                "must not be empty or N/A"
            )

    owner = ""
    if "owner_module" in present:
        value = (parsed["owner_module"] or "").strip()
        if not value or _is_na(value):
            if strategy == "module-packages":
                errors.append(
                    "### Implementation Slice field Owner module "
                    "must not be empty or N/A"
                )
        else:
            owner = value
            if not gm.module_rows(modules, owner):
                errors.append(
                    f"### Implementation Slice Owner module {owner!r} "
                    "is not in docs/product/modules.csv"
                )

    related: list[str] = []
    if "related_modules" in present:
        for slug in parsed["related_modules"]:
            if gm.module_rows(modules, slug):
                related.append(slug)
            else:
                errors.append(
                    f"### Implementation Slice Related module {slug!r} "
                    "is not in docs/product/modules.csv"
                )

    if strategy == "module-packages" and primary and owner:
        expected = {
            (row.get("owner_module") or "").strip()
            for row in gm.capability_rows(capabilities, primary)
            if (row.get("owner_module") or "").strip()
        }
        if expected and owner not in expected:
            errors.append(
                f"### Implementation Slice Owner module {owner!r} must equal "
                f"capability {primary!r} owner_module "
                f"{', '.join(sorted(expected))!r} in docs/product/capabilities.csv"
            )

    module_slugs = ([owner] if owner else []) + related
    roots = gm.module_paths(modules, module_slugs)

    for field, label in (("packages", "Code packages"), ("owned", "Owned paths")):
        if field not in present:
            continue
        values = _real_values(parsed[field])
        if not values:
            if field in required_fields:
                errors.append(
                    f"### Implementation Slice field {label} "
                    "must not be empty or N/A"
                )
            continue
        for raw in values:
            prefix = _slice_path_prefix(raw)
            problem = _path_problem(prefix)
            if problem:
                errors.append(
                    f"### Implementation Slice {label} path {raw!r} {problem}"
                )
                continue
            if roots and not _within(prefix, roots):
                errors.append(
                    f"### Implementation Slice {label} path {raw!r} is outside "
                    f"the owner/related module paths ({', '.join(roots)})"
                )

    if "integration" in present:
        entries = parsed["integration"]
        # Empty or N/A integration paths mean no integration entries; the design
        # requires only that declared values match layout patterns.
        for entry in entries:
            path = (entry.get("path") or "").strip()
            reason = (entry.get("reason") or "").strip()
            task = (entry.get("task") or "").strip()
            problem = _path_problem(path)
            if problem:
                errors.append(
                    f"### Implementation Slice integration path {path!r} {problem}"
                )
            elif not any(
                _integration_matches(path, pattern)
                for pattern in integration_patterns
            ):
                errors.append(
                    f"### Implementation Slice integration path {path!r} does not "
                    "match code-layout.json integration_paths"
                )
            if not reason:
                errors.append(
                    f"### Implementation Slice integration path {path!r} "
                    "must state a reason"
                )
            if not task:
                errors.append(
                    f"### Implementation Slice integration path {path!r} "
                    "must end with '; task <TASK-ID>'"
                )

    # Wording only: the card path itself is implicitly owned by
    # ``check-change-footprint.py`` for every owner/related module path.
    if strategy == "module-packages" and "module_card" in present:
        problem = _module_card_problem(parsed["module_card"])
        if problem:
            errors.append(f"### Implementation Slice Module card {problem}")


# -- legacy full-mode checks --------------------------------------------------
def check_sections(sections, errors: list[str]) -> str:
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
    return frontend_body


def check_interface(sections, errors: list[str]) -> None:
    # Cross-boundary interfaces must point at the machine-readable catalog unless N/A.
    interface_body = body_for(sections, "接口设计")
    if not interface_body.strip().upper().startswith("N/A") and has_subsection(interface_body, "### 接口边界清单"):
        boundary = extract_subsection(interface_body, "### 接口边界清单")
        if not boundary.strip().upper().startswith("N/A") and "interface-catalog.csv" not in boundary:
            errors.append("## 接口设计 ### 接口边界清单 / ### Interface Boundary Inventory must reference interface-catalog.csv unless N/A")


def check_existing_code(sections, errors: list[str]) -> None:
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


def check_ui(change: str, sections, frontend_body: str, errors: list[str], warnings: list[str]) -> None:
    # UI Changes must carry actual tokens, not only variable names.
    audit = ROOT / "openspec/changes" / change / "design/figma-audit.md"
    ui_change = False
    if audit.is_file():
        audit_text = audit.read_text(encoding="utf-8")
        ui_change = not re.search(r"^- (?:设计来源状态|Design source status)[:：]\s*N/A\s*$", audit_text, re.M)
    if not (ui_change and frontend_body):
        return
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
    if "ui-actions.csv" not in frontend_body:
        errors.append("UI 前端详细设计必须引用 design/ui-actions.csv（功能按钮/图标交互清单）")
    if "check-ui-actions.py" not in frontend_body:
        errors.append("UI 前端详细设计必须写明按钮/图标跳转与 API 映射检查命令 check-ui-actions.py")
    event_body = extract_subsection(frontend_body, "### 事件处理")
    if not event_body:
        errors.append(
            "### 事件处理 / ### Event Handling is empty; explain handler behavior and "
            "reference the corresponding design/ui-actions.csv element_id"
        )
    elif "ui-actions.csv" not in event_body:
        errors.append(
            "### 事件处理 / ### Event Handling must reference design/ui-actions.csv by "
            "element_id; the CSV is the single machine-readable action inventory, so do "
            "not duplicate route/params/operationId mapping in prose"
        )
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

    actions = ROOT / "openspec/changes" / change / "design/ui-actions.csv"
    if not actions.is_file():
        errors.append("UI Change missing design/ui-actions.csv (button/icon action mapping)")

    responsive_body = body_for(sections, "前端详细设计")
    if has_subsection(responsive_body, "### 响应式与视口规则"):
        resp = extract_subsection(responsive_body, "### 响应式与视口规则")
        if "1440" not in resp:
            errors.append("### 响应式与视口规则 / ### Responsive and Viewport Rules must state the 1440×900 baseline")
        if not re.search(r"\|.*PAGE", resp):
            warnings.append("### 响应式与视口规则 / ### Responsive and Viewport Rules should contain a per-PAGE table")


def _parse_args(argv):
    args = list(sys.argv[1:] if argv is None else argv)
    slice_only = "--slice-only" in args
    args = [a for a in args if a not in ("--slice-only", "--strict")]
    change = None
    if "--change" in args:
        idx = args.index("--change")
        if idx + 1 >= len(args):
            print(USAGE, file=sys.stderr)
            return None, slice_only, 2
        change = args[idx + 1]
        if not CHANGE_ID_RE.fullmatch(change):
            print("Invalid change-id", file=sys.stderr)
            return None, slice_only, 2
        args = args[:idx] + args[idx + 2:]
    if args or not change:
        print(USAGE, file=sys.stderr)
        return None, slice_only, 2
    return change, slice_only, 0


def main(argv=None):
    change, slice_only, code = _parse_args(argv)
    if code:
        return code

    design = ROOT / "openspec/changes" / change / "design.md"
    if not design.is_file():
        print(f"ERROR: missing design.md: {design.relative_to(ROOT)}")
        return 1

    text = design.read_text(encoding="utf-8")
    sections = split_sections(text)
    errors: list[str] = []
    warnings: list[str] = []

    if slice_only:
        if not any(alias in sections for alias in SECTION_ALIASES["设计决策"]):
            errors.append("design.md missing section: ## 设计决策")
    else:
        frontend_body = check_sections(sections, errors)
        check_interface(sections, errors)
        check_existing_code(sections, errors)
        check_ui(change, sections, frontend_body, errors, warnings)

    check_slice(text, errors)

    for w in warnings:
        print("WARN:", w)
    for e in errors:
        print("ERROR:", e)
    if errors:
        print(f"Design section check failed: {len(errors)} issue(s).")
        return 1
    if slice_only:
        print("Design slice check passed: Implementation Slice is valid.")
    else:
        print("Design section check passed: design.md has the required unified subsections.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
