#!/usr/bin/env python3
"""Fail-closed structural check for human acceptance evidence.

Human UI acceptance compares the running system directly with the Figma file.
No screenshots are required or accepted as the primary evidence. The machine
geometry evidence (`figma-layout-check.json`) is still required from stage 08.
"""
from pathlib import Path
import json, re, sys

ROOT = Path(__file__).resolve().parents[1]
if len(sys.argv) != 2:
    print("Usage: check-acceptance.py <change-id>", file=sys.stderr)
    sys.exit(2)
change_id = sys.argv[1]
if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", change_id):
    print("Invalid change-id; use lowercase kebab-case.", file=sys.stderr)
    sys.exit(2)
path = ROOT / "openspec/changes" / change_id / "design/evidence/acceptance.md"
if not path.is_file():
    print(f"MISSING: {path.relative_to(ROOT)}", file=sys.stderr)
    sys.exit(1)
text = path.read_text(encoding="utf-8")
errors = []
match = re.search(r"(?im)^-\s*Overall result:\s*(.+?)\s*$", text)
accepted = {"accepted", "accepted with approved deviations"}
if not match or match.group(1).strip().lower() not in accepted:
    errors.append("Overall result must be ACCEPTED or ACCEPTED WITH APPROVED DEVIATIONS.")
for marker in ("TODO", "TBD", "待确认", "Pending", "pending", "NOT ACCEPTED"):
    if marker in text:
        errors.append(f"Unresolved marker remains in acceptance evidence: {marker}")
rows = []
for line_no, line in enumerate(text.splitlines(), 1):
    s = line.strip()
    if not s.startswith("|") or "---" in s:
        continue
    cells = [x.strip() for x in s.strip("|").split("|")]
    if cells and cells[0].lower() == "ac id":
        continue
    if cells and re.fullmatch(r"AC-\d+", cells[0]):
        rows.append((line_no, cells))
if not rows:
    errors.append("At least one AC-### result row is required.")
allowed = {"pass", "passed", "accepted", "n/a", "approved deviation"}
for line_no, cells in rows:
    while len(cells) < 5:
        cells.append("")
    result = cells[1].lower()
    evidence = cells[2]
    reviewer = cells[4]
    if result not in allowed:
        errors.append(f"Line {line_no}: AC result {cells[1]!r} is not an accepted status.")
    if not evidence or evidence.lower() in {"todo", "tbd", "pending", "n/a"}:
        errors.append(f"Line {line_no}: AC evidence must identify an actual test/report/manual evidence.")
    if not reviewer or reviewer.lower() in {"todo", "tbd", "pending"}:
        errors.append(f"Line {line_no}: reviewer is required.")

# UI-bearing Changes require a signed per-PAGE live acceptance table.
base = ROOT / "openspec/changes" / change_id / "design"
audit = base / "figma-audit.md"
ui_change = False
expected_pages = []
if audit.is_file():
    audit_text = audit.read_text(encoding="utf-8")
    ui_change = not re.search(r"^- 设计来源状态：N/A\s*$", audit_text, re.M)
    start = audit_text.find("## PAGE 与节点")
    if start < 0:
        start = audit_text.find("## 页面覆盖")
    if start >= 0:
        endsec = audit_text.find("\n## ", start + 1)
        expected_pages = sorted(set(re.findall(
            r"PAGE-\d{3}", audit_text[start:endsec if endsec >= 0 else len(audit_text)])))

if ui_change:
    if "## UI acceptance" not in text:
        errors.append("UI Change acceptance evidence missing section: ## UI acceptance")
    else:
        start = text.find("## UI acceptance")
        endsec = text.find("\n## ", start + len("## UI acceptance"))
        ui_section = text[start:endsec if endsec >= 0 else len(text)]
        ui_rows = []
        for line in ui_section.splitlines():
            s = line.strip()
            if not s.startswith("|") or "---" in s:
                continue
            cells = [x.strip() for x in s.strip("|").split("|")]
            if cells and cells[0].lower() == "page":
                continue
            if cells and re.fullmatch(r"PAGE-\d{3}", cells[0]):
                ui_rows.append(cells)
        if not ui_rows:
            errors.append("## UI acceptance must contain per-PAGE rows")
        allowed_ui = {"accepted", "approved", "pass", "passed", "approved deviation", "deviation approved"}
        covered = set()
        for cells in ui_rows:
            while len(cells) < 7:
                cells.append("")
            pid = cells[0]
            covered.add(pid)
            if cells[1].lower() not in allowed_ui:
                errors.append(f"UI acceptance {pid}: result must be ACCEPTED/DEVIATION_APPROVED")
            if not cells[2] or not re.search(r"\d+:\d+", cells[2]):
                errors.append(f"UI acceptance {pid}: Figma node is required")
            if not cells[3] or cells[3].lower() in {"todo", "tbd", "pending"}:
                errors.append(f"UI acceptance {pid}: a live system entry (URL or route) is required")
            method = cells[5].strip()
            if method not in {"机器证据签收", "并排核对"}:
                errors.append(f"UI acceptance {pid}: 验收方式 must be 机器证据签收 or 并排核对")
            deviation = cells[4].strip()
            if deviation and deviation.lower() not in {"-", "—", "无", "n/a", "none"}:
                if "审批" not in deviation and cells[1].lower() not in {"approved deviation", "deviation approved"}:
                    errors.append(f"UI acceptance {pid}: recorded deviation must name the approver")
            if not cells[6] or cells[6].lower() in {"todo", "tbd", "pending"}:
                errors.append(f"UI acceptance {pid}: reviewer is required")
        for pid in expected_pages:
            if pid not in covered:
                errors.append(f"UI acceptance missing PAGE: {pid}")

    # The machine geometry evidence must exist and pass before human sign-off.
    layout_check = base / "evidence/figma-layout-check.json"
    if not layout_check.is_file():
        errors.append("UI acceptance requires evidence/figma-layout-check.json")
    else:
        try:
            evidence = json.loads(layout_check.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"figma-layout-check.json is invalid JSON: {exc}")
            evidence = {}
        if evidence:
            if evidence.get("result") != "PASS":
                errors.append("figma-layout-check.json result is not PASS")
            pages = {p.get("page_id"): p for p in evidence.get("pages", [])}
            for pid in expected_pages:
                page = pages.get(pid)
                if not page or page.get("result") != "PASS":
                    errors.append(f"{pid}: figma-layout-check.json is missing or not PASS")
                elif page.get("missing_elements"):
                    errors.append(f"{pid}: figma-layout-check.json has missing elements")
                elif page.get("max_delta_px", 0) > page.get("tolerance_px", 0):
                    errors.append(f"{pid}: figma-layout-check.json max delta exceeds tolerance")

if errors:
    for e in errors:
        print("ERROR:", e)
    print(f"Acceptance check failed: {len(errors)} issue(s).")
    sys.exit(1)
print(f"Acceptance evidence structurally passed: {len(rows)} AC row(s). Human judgment is still required.")
