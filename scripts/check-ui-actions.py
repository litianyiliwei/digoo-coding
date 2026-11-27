#!/usr/bin/env python3
"""Verify that every functional UI control has a navigation or API action mapping.

Stage 07 inventories functional UI controls (buttons, icons, links, menu items,
tabs) in `design/ui-actions.csv`. Every row must map the control to exactly one
action:

  * navigate   -> `route` (address) plus `route_params` (input parameters)
  * api        -> `operation_id` that exists in `api/openapi.yaml`
  * local-ui   -> pure presentation state with no business meaning (expand /
                  collapse, tab switch, dialog open/close, local sort/filter of
                  an already loaded view); the agent records it with a reason in
                  `notes`, no user confirmation needed
  * local-only -> no navigation/API but with business meaning; requires
                  explicit user confirmation (`confirmation` + `approver` +
                  `confirmed_at`)

A control with no mapping must stop the stage: the agent has to present the
unmapped control to the user and record the user's confirmation. Coverage is
cross-checked against `design/figma-layout.csv` and the PAGE design code in
`design/figma-code/`.

Exit codes:
  0 PASS (or N/A when the Change has no UI)
  1 FAIL
  2 usage
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_COLUMNS = [
    "page_id", "element_id", "figma_node_id", "element_type", "label", "event",
    "action_type", "route", "route_params", "operation_id", "handler", "test_id",
    "confirmation", "approver", "confirmed_at", "notes",
]
ELEMENT_TYPES = {"button", "icon", "link", "menu", "tab", "form", "other"}
ACTION_TYPES = {"navigate", "api", "local-ui", "local-only"}
NONE_PARAMS = {"none", "无", "{}", "[]", "-"}
PLACEHOLDER = re.compile(r"\bTODO\b|\bTBD\b|PENDING|待确认|待补充|\[填充\]")
PAGE_RE = re.compile(r"PAGE-\d{3}")
DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
ROUTE_RE = re.compile(r"(/[A-Za-z0-9_./:{}()\-\*]*|[A-Za-z][A-Za-z0-9_.:-]*)")
INTERACTIVE_HINT = re.compile(
    r"按钮|图标|链接|菜单|标签页|选项卡|开关|控件|操作入口|"
    r"button|icon|link|menu|tab|control",
    re.I,
)
NON_INTERACTIVE = re.compile(r"非交互|装饰|decorative|non-interactive", re.I)
CODE_SUFFIXES = {".vue", ".tsx", ".jsx", ".js", ".ts", ".html"}
TAG_RE = re.compile(r"<[A-Za-z][^<>]*>", re.S)


def fail(message: str, code: int = 1) -> None:
    print(message)
    sys.exit(code)


def has_placeholder(value: str) -> bool:
    return bool(PLACEHOLDER.search(value or ""))


def normalize(value) -> str:
    return (value or "").strip()


def is_confirmed(value: str) -> bool:
    text = normalize(value).lower()
    if not text:
        return False
    if any(word in text for word in ("待", "未", "pending", "unconfirmed", "tbd")):
        return False
    return any(word in text for word in ("用户已确认", "已确认", "confirmed", "approved"))


def load_csv(path: Path, required: list[str], label: str) -> list[dict[str, str]]:
    if not path.is_file():
        raise FileNotFoundError(f"missing {label}: {path}")
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        fields = set(reader.fieldnames or [])
        missing = [column for column in required if column not in fields]
        if missing:
            raise ValueError(f"{label} missing columns: {', '.join(missing)}")
        return [
            {normalize(key): normalize(value) for key, value in row.items() if key is not None}
            for row in reader
        ]


def ui_is_declared(base: Path) -> bool:
    audit = base / "figma-audit.md"
    if audit.is_file():
        text = audit.read_text(encoding="utf-8")
        if re.search(
            r"^- (?:设计来源状态|Design source status)[:：]\s*N/A\s*$", text, re.M
        ):
            return False
        return True
    if (base / "ui-actions.csv").is_file():
        return True
    if (base / "figma-layout.csv").is_file():
        return True
    code_dir = base / "figma-code"
    if code_dir.is_dir() and any(
        path.suffix.lower() in CODE_SUFFIXES for path in code_dir.iterdir() if path.is_file()
    ):
        return True
    return False


def is_control_tag(tag: str) -> bool:
    lower = tag.lower()
    if re.search(r"<(el-|van-|u-|uni-)?button(?=[\s/>])", lower):
        return True
    if re.search(r"<(router-link|nuxt-link|el-link|link|routerlink)(?=[\s/>])", lower):
        return True
    if re.search(r"<a\b", lower) and "href" in lower:
        return True
    if any(
        marker in lower
        for marker in ("@click", "@tap", "v-on:click", "onclick=", "onclick={")
    ):
        return True
    return False


def design_code_controls(path: Path) -> int:
    text = path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return sum(1 for tag in TAG_RE.finditer(text) if is_control_tag(tag.group(0)))


def openapi_operation_ids(path: Path) -> tuple[set[str], bool]:
    text = path.read_text(encoding="utf-8")
    ids = set(re.findall(r"operationId:\s*[\"']?([A-Za-z0-9_.\-]+)", text))
    api_scope_none = bool(re.search(r"x-api-scope:\s*none", text, re.I))
    return ids, api_scope_none


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--change", required=True)
    parser.add_argument("--root", default=str(ROOT), help="Project root (defaults to this package)")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", args.change):
        fail("Invalid change-id; use lowercase kebab-case.", 2)
    root = Path(args.root).resolve()
    base = root / "openspec/changes" / args.change / "design"
    if not (root / "openspec/changes" / args.change).is_dir():
        fail(f"Change not found: openspec/changes/{args.change}")

    if not ui_is_declared(base):
        print("UI action check skipped: no UI declared for this Change (N/A).")
        return 0

    actions_path = base / "ui-actions.csv"
    try:
        actions = load_csv(actions_path, REQUIRED_COLUMNS, "ui-actions.csv")
    except (FileNotFoundError, ValueError) as exc:
        fail(f"FAIL: {exc}")
    if not actions:
        fail("FAIL: UI Change must inventory at least one functional control in design/ui-actions.csv")

    errors: list[str] = []
    warnings: list[str] = []

    try:
        layout = load_csv(
            base / "figma-layout.csv",
            ["page_id", "element_id", "figma_node_id", "dom_selector", "notes"],
            "figma-layout.csv",
        )
    except (FileNotFoundError, ValueError):
        layout = []

    openapi = base.parent / "api" / "openapi.yaml"
    operation_ids: set[str] = set()
    api_scope_none = False
    if openapi.is_file():
        operation_ids, api_scope_none = openapi_operation_ids(openapi)

    test_cases_path = base / "test-cases.csv"
    test_cases_text = (
        test_cases_path.read_text(encoding="utf-8") if test_cases_path.is_file() else ""
    )

    seen: set[tuple[str, str]] = set()
    rows_by_page: dict[str, int] = {}
    known_pages = {
        row.get("page_id", "") for row in layout if PAGE_RE.fullmatch(row.get("page_id", ""))
    }
    code_dir = base / "figma-code"
    if code_dir.is_dir():
        for path in code_dir.iterdir():
            if path.is_file() and path.suffix.lower() in CODE_SUFFIXES:
                match = PAGE_RE.search(path.name)
                if match:
                    known_pages.add(match.group(0))
    for row in actions:
        page = row.get("page_id", "")
        element = row.get("element_id", "")
        where = f"{page or '?'}/{element or '?'}"
        if not PAGE_RE.fullmatch(page):
            errors.append(f"{where}: page_id must look like PAGE-001")
        elif known_pages and page not in known_pages:
            errors.append(
                f"{where}: page_id {page} is not in figma-layout.csv or figma-code/; "
                "use a frozen PAGE ID"
            )
        if not element:
            errors.append(f"{where}: element_id is required")
        key = (page, element)
        if key in seen:
            errors.append(f"{where}: duplicate row (each control is inventoried once)")
        seen.add(key)
        rows_by_page[page] = rows_by_page.get(page, 0) + 1

        label = row.get("label", "")
        if not label or has_placeholder(label):
            errors.append(f"{where}: label is required (use the UI text or accessible name)")
        element_type = row.get("element_type", "").lower()
        if element_type not in ELEMENT_TYPES:
            errors.append(f"{where}: element_type must be one of {', '.join(sorted(ELEMENT_TYPES))}")

        action_type = row.get("action_type", "").lower()
        if action_type not in ACTION_TYPES:
            errors.append(
                f"{where}: '{label or element}' has no navigation/API mapping; "
                "record action_type=navigate/api/local-ui/local-only. If it has business "
                "meaning but neither, prompt the user to confirm and record the confirmation."
            )
            continue

        if action_type == "local-ui":
            if not row.get("notes") or has_placeholder(row.get("notes", "")):
                errors.append(
                    f"{where}: local-ui action requires a reason in `notes` "
                    "(which presentation state it toggles)"
                )

        elif action_type == "navigate":
            route = row.get("route", "")
            params = row.get("route_params", "")
            if not route or has_placeholder(route) or not ROUTE_RE.fullmatch(route):
                errors.append(f"{where}: navigate action requires a concrete route (address) in `route`")
            if not params or has_placeholder(params):
                errors.append(
                    f"{where}: navigate action requires `route_params` (input parameters); "
                    "write NONE when the route takes no parameters"
                )
            elif params.lower() in NONE_PARAMS and (":" in route or "{" in route):
                errors.append(
                    f"{where}: route {route!r} declares path parameters; "
                    "list the actual input parameters in route_params instead of NONE"
                )

        elif action_type == "api":
            operation_id = row.get("operation_id", "")
            if not operation_id or has_placeholder(operation_id):
                errors.append(f"{where}: api action requires `operation_id` (the API being called)")
            elif not openapi.is_file():
                errors.append(
                    f"{where}: api action requires api/openapi.yaml so operation_id "
                    f"{operation_id!r} can be verified"
                )
            elif api_scope_none:
                errors.append(
                    f"{where}: action calls API {operation_id!r} but openapi.yaml declares x-api-scope: none"
                )
            elif operation_id not in operation_ids:
                errors.append(
                    f"{where}: operation_id {operation_id!r} is not defined in api/openapi.yaml"
                )

        elif action_type == "local-only":
            if not is_confirmed(row.get("confirmation", "")):
                errors.append(
                    f"{where}: '{label or element}' has neither navigation (route + params) "
                    "nor an API call; prompt the user to confirm, then record "
                    "confirmation/approver/confirmed_at"
                )
            elif not row.get("approver") or has_placeholder(row["approver"]):
                errors.append(f"{where}: confirmed local-only action requires the `approver` name")
            elif not DATE.fullmatch(row.get("confirmed_at", "")):
                errors.append(f"{where}: confirmed local-only action requires `confirmed_at` as YYYY-MM-DD")
            if not row.get("notes") or has_placeholder(row.get("notes", "")):
                errors.append(f"{where}: local-only action requires a reason in `notes`")

        test_id = row.get("test_id", "")
        if test_id and test_id.upper() != "N/A":
            if not test_cases_path.is_file():
                errors.append(f"{where}: test_id {test_id!r} cannot be verified without design/test-cases.csv")
            elif test_id not in test_cases_text:
                errors.append(f"{where}: test_id {test_id!r} is not registered in design/test-cases.csv")

    # Coverage: interactive elements visible in the geometry assertion table.
    covered = {(row.get("page_id", ""), row.get("element_id", "")) for row in actions}
    covered_nodes = {row.get("figma_node_id", "") for row in actions if row.get("figma_node_id")}
    for row in layout:
        hint_source = " ".join(
            [row.get("notes", ""), row.get("text_content", "")]
        )
        if not INTERACTIVE_HINT.search(hint_source) or NON_INTERACTIVE.search(hint_source):
            continue
        page, element = row.get("page_id", ""), row.get("element_id", "")
        if (page, element) in covered or row.get("figma_node_id", "") in covered_nodes:
            continue
        message = (
            f"{page}/{element}: this assertion-table element looks interactive but has no "
            "ui-actions.csv row; map it to route+params or operationId, or record a "
            "user-confirmed local-only action"
        )
        (errors if args.strict else warnings).append(message)

    # Coverage: controls present in the target-framework design code.
    code_dir = base / "figma-code"
    if code_dir.is_dir():
        for path in sorted(code_dir.iterdir()):
            if not path.is_file() or path.suffix.lower() not in CODE_SUFFIXES:
                continue
            match = PAGE_RE.search(path.name)
            if not match:
                continue
            page = match.group(0)
            detected = design_code_controls(path)
            if detected <= 0:
                continue
            inventoried = rows_by_page.get(page, 0)
            if detected > inventoried:
                message = (
                    f"{page}: design code {path.name} has {detected} interactive control(s) "
                    f"but ui-actions.csv inventories {inventoried}; enumerate every functional "
                    "button/icon/link/menu/tab and map route+params or operationId, or ask the "
                    "user to confirm a local-only action"
                )
                (errors if args.strict else warnings).append(message)

    for warning in warnings:
        print("WARN:", warning)
    for error in errors:
        print("ERROR:", error)
    if errors:
        print(f"UI action check failed: {len(errors)} issue(s).")
        return 1

    print(
        "UI action check passed: "
        f"{len(actions)} control(s) mapped to navigate/api/local-ui/local-only; "
        f"{len(layout)} assertion row(s) cross-checked."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
