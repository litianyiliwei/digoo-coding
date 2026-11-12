#!/usr/bin/env python3
"""Parameterized visual regression: compare Figma geometry with runtime DOM.

Expected values come from the compact assertion table `design/figma-layout.csv`
(which is derived from Figma's `get_design_context` / `get_metadata`). Actual
values come from the running DOM measured with Playwright at the frozen viewport
(default 1440x900). No screenshots are involved.

Exit codes:
  0 PASS
  1 FAIL (missing element / geometry / text / font mismatch)
  2 BLOCKED (missing inputs, Playwright unavailable, login/browser failure)
"""
import argparse
import csv
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAYOUT_REQUIRED = [
    "page_id", "route", "element_id", "figma_node_id", "x", "y", "width", "height",
    "dom_selector", "assert_geometry", "assert_text", "tolerance_px",
    "text_content", "font_size", "font_weight", "notes",
]
PAGE_RE = re.compile(r"PAGE-\d{3}")


class Blocked(Exception):
    pass


def fail(msg, code=1):
    print(msg, file=sys.stderr)
    sys.exit(code)


def load_csv(path, required):
    if not path.is_file():
        raise Blocked(f"missing input: {path.relative_to(ROOT)}")
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        fields = set(reader.fieldnames or [])
        missing = [c for c in required if c not in fields]
        if missing:
            raise Blocked(f"{path.relative_to(ROOT)} missing columns: {', '.join(missing)}")
        return [{(k or ''): (v or '').strip() for k, v in row.items()} for row in reader]


def num(value, field, where):
    try:
        return float(str(value).strip())
    except ValueError:
        raise Blocked(f"{where}: {field} must be numeric, got {value!r}")


def truthy(value):
    return str(value).strip().lower() in {"1", "true", "yes", "y", "是"}


def norm_text(value):
    return re.sub(r"\s+", " ", (value or "").strip())


def parse_viewport(raw):
    match = re.fullmatch(r"(\d+)x(\d+)", raw.strip().lower())
    if not match:
        raise Blocked(f"--viewport must look like 1440x900, got {raw!r}")
    return int(match.group(1)), int(match.group(2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--change", required=True)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--viewport", default="1440x900")
    parser.add_argument("--out")
    parser.add_argument("--storage-state", default="")
    parser.add_argument("--login-account", default="")
    parser.add_argument("--login-password", default="")
    parser.add_argument("--login-path", default="/api/v1/platform/auth/login")
    parser.add_argument("--token-key", default="platform.token")
    parser.add_argument("--frame-selector", default="#app")
    parser.add_argument("--page", action="append", default=[])
    args = parser.parse_args()

    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", args.change):
        fail("Invalid change-id; use lowercase kebab-case.", 2)
    base = ROOT / "openspec/changes" / args.change / "design"
    layout_path = base / "figma-layout.csv"
    out_path = Path(args.out) if args.out else base / "evidence/figma-layout-check.json"
    if not out_path.is_absolute():
        out_path = ROOT / out_path

    try:
        layout = load_csv(layout_path, LAYOUT_REQUIRED)
        width, height = parse_viewport(args.viewport)
    except Blocked as exc:
        fail(f"BLOCKED: {exc}", 2)

    layout_by_page = {}
    for row in layout:
        pid = row["page_id"]
        if not PAGE_RE.fullmatch(pid):
            fail(f"FAIL: invalid page_id in figma-layout.csv: {pid!r}", 1)
        if not row["route"] or row["route"].upper() == "PENDING":
            fail(f"FAIL: {pid}/{row['element_id']} has no route (07 must fill it)", 1)
        if not row["dom_selector"] or row["dom_selector"].upper() == "PENDING":
            fail(f"FAIL: {pid}/{row['element_id']} has no dom_selector (07 must fill it)", 1)
        if row["assert_geometry"].upper() not in {"Y", "N"}:
            fail(f"FAIL: {pid}/{row['element_id']} assert_geometry must be Y/N", 1)
        if row["assert_text"].upper() not in {"Y", "N"}:
            fail(f"FAIL: {pid}/{row['element_id']} assert_text must be Y/N", 1)
        for field in ("x", "y", "width", "height", "tolerance_px"):
            num(row[field], field, f"{pid}/{row['element_id']}")
        layout_by_page.setdefault(pid, []).append(row)
    if not layout_by_page:
        fail("FAIL: figma-layout.csv has no rows", 1)

    pages_arg = [p for p in args.page if p]
    if pages_arg:
        missing = [p for p in pages_arg if p not in layout_by_page]
        if missing:
            fail(f"FAIL: requested page(s) not in figma-layout.csv: {', '.join(missing)}", 1)
        page_ids = pages_arg
    else:
        page_ids = sorted(layout_by_page)

    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:  # noqa: BLE001
        fail(f"BLOCKED: Python Playwright is unavailable ({exc}). "
             "Install playwright and its browser, or implement an equivalent "
             "project runner and record it in design.md.", 2)

    result = {
        "change_id": args.change,
        "tool": "scripts/check-figma-layout.py",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "base_url": args.base_url,
        "viewport": {"width": width, "height": height},
        "frame_selector": args.frame_selector,
        "pages": [],
        "result": "PASS",
    }

    try:
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            for pid in page_ids:
                rows = layout_by_page[pid]
                route = rows[0]["route"]
                url = args.base_url.rstrip("/") + (route if route.startswith("/") else "/" + route)
                context_args = {"viewport": {"width": width, "height": height}}
                if args.storage_state:
                    context_args["storage_state"] = args.storage_state
                context = browser.new_context(**context_args)
                if args.login_account and route != "/login":
                    login_url = args.base_url.rstrip("/") + args.login_path
                    response = context.request.post(login_url, data={
                        "account": args.login_account,
                        "password": args.login_password,
                    })
                    if not response.ok:
                        fail(f"BLOCKED: login failed for {pid} (HTTP {response.status})", 2)
                    token = response.json().get("token") or response.json().get("data", {}).get("token")
                    if not token:
                        fail(f"BLOCKED: login response has no token for {pid}", 2)
                    context.add_init_script(
                        f"sessionStorage.setItem({args.token_key!r}, {token!r});"
                    )
                page = context.new_page()
                page.goto(url, wait_until="networkidle")

                frame_rect = None
                if args.frame_selector:
                    frame = page.locator(args.frame_selector).first
                    if frame.count():
                        frame_rect = frame.bounding_box()
                origin_x = float(frame_rect["x"]) if frame_rect else 0.0
                origin_y = float(frame_rect["y"]) if frame_rect else 0.0

                page_result = {
                    "page_id": pid,
                    "route": route,
                    "url": url,
                    "result": "PASS",
                    "element_count": len(rows),
                    "max_delta_px": 0.0,
                    "tolerance_px": max(num(row["tolerance_px"], "tolerance_px", pid) for row in rows),
                    "missing_elements": [],
                    "mismatches": [],
                    "elements": [],
                }
                for row in rows:
                    element_id = row["element_id"]
                    tol = num(row["tolerance_px"], "tolerance_px", pid)
                    selector = row["dom_selector"]
                    expected = {
                        "x": num(row["x"], "x", pid),
                        "y": num(row["y"], "y", pid),
                        "width": num(row["width"], "width", pid),
                        "height": num(row["height"], "height", pid),
                    }
                    element = {
                        "element_id": element_id,
                        "figma_node_id": row["figma_node_id"],
                        "dom_selector": selector,
                        "tolerance_px": tol,
                        "assert_geometry": truthy(row["assert_geometry"]),
                        "assert_text": truthy(row["assert_text"]),
                        "expected": expected,
                        "result": "PASS",
                        "issues": [],
                    }
                    loc = page.locator(selector).first
                    if loc.count() == 0:
                        element["result"] = "FAIL"
                        element["issues"].append("element not found")
                        page_result["missing_elements"].append(element_id)
                    else:
                        box = loc.bounding_box()
                        if box is None:
                            element["result"] = "FAIL"
                            element["issues"].append("element has no layout box")
                            page_result["missing_elements"].append(element_id)
                        else:
                            actual = {
                                "x": round(float(box["x"]) - origin_x, 2),
                                "y": round(float(box["y"]) - origin_y, 2),
                                "width": round(float(box["width"]), 2),
                                "height": round(float(box["height"]), 2),
                            }
                            element["actual"] = actual
                            delta = {
                                key: round(abs(actual[key] - expected[key]), 2)
                                for key in ("x", "y", "width", "height")
                            }
                            element["delta"] = delta
                            max_delta = max(delta.values()) if element["assert_geometry"] else 0.0
                            element["max_delta_px"] = max_delta
                            page_result["max_delta_px"] = max(page_result["max_delta_px"], max_delta)
                            if element["assert_geometry"] and max_delta > tol:
                                element["result"] = "FAIL"
                                element["issues"].append(
                                    f"geometry delta {max_delta}px exceeds tolerance {tol}px"
                                )
                            if element["assert_text"]:
                                expected_text = norm_text(row.get("text_content", ""))
                                actual_text = norm_text(loc.evaluate("el => el.textContent"))
                                element["text_expected"] = expected_text
                                element["text_actual"] = actual_text
                                if expected_text and actual_text != expected_text:
                                    element["result"] = "FAIL"
                                    element["issues"].append(
                                        f"text mismatch: expected {expected_text!r}, "
                                        f"actual {actual_text!r}"
                                    )
                            font_expected = {}
                            if row.get("font_size") and row["font_size"].upper() != "N/A":
                                size = row["font_size"].strip()
                                font_expected["font_size"] = size if "px" in size else f"{size}px"
                            if row.get("font_weight") and row["font_weight"].upper() != "N/A":
                                font_expected["font_weight"] = row["font_weight"].strip()
                            if font_expected:
                                actual_font = loc.evaluate(
                                    "el => { const s = getComputedStyle(el); "
                                    "return {font_size: s.fontSize, font_weight: s.fontWeight}; }"
                                )
                                element["font_expected"] = font_expected
                                element["font_actual"] = actual_font
                                for key, value in font_expected.items():
                                    if str(actual_font.get(key, "")) != str(value):
                                        element["result"] = "FAIL"
                                        element["issues"].append(
                                            f"{key} mismatch: expected {value!r}, "
                                            f"actual {actual_font.get(key)!r}"
                                        )
                    if element["result"] != "PASS":
                        page_result["mismatches"].append(
                            {"element_id": element_id, "issues": element["issues"]}
                        )
                        page_result["result"] = "FAIL"
                    page_result["elements"].append(element)
                if page_result["result"] != "PASS":
                    result["result"] = "FAIL"
                result["pages"].append(page_result)
                context.close()
            browser.close()
    except Exception as exc:  # noqa: BLE001
        fail(f"BLOCKED: runtime layout measurement failed ({type(exc).__name__}: {exc})", 2)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "change_id": args.change,
        "viewport": result["viewport"],
        "result": result["result"],
        "pages": [
            {
                "page_id": p["page_id"],
                "result": p["result"],
                "elements": p["element_count"],
                "max_delta_px": p["max_delta_px"],
                "missing_elements": p["missing_elements"],
            }
            for p in result["pages"]
        ],
        "out": str(out_path),
    }, ensure_ascii=False))
    sys.exit(0 if result["result"] == "PASS" else 1)


if __name__ == "__main__":
    main()
