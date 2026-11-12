#!/usr/bin/env python3
"""Validate code-review evidence content for stage 08.

UI Changes are gated by machine-readable runtime geometry evidence
(`design/evidence/figma-layout-check.json`), not by screenshots. The
`## UI fidelity` table is the human summary of that evidence.
"""
from pathlib import Path
import json, re, sys

ROOT = Path(__file__).resolve().parents[1]
args = sys.argv[1:]
strict = "--strict" in args
change = None
if "--change" in args:
    idx = args.index("--change")
    if idx + 1 >= len(args):
        print("Usage: check-code-review.py --change <change-id> [--strict]", file=sys.stderr)
        sys.exit(2)
    change = args[idx + 1]
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", change):
        print("Invalid change-id", file=sys.stderr)
        sys.exit(2)
    args = args[:idx] + args[idx + 2:]
args = [a for a in args if a != "--strict"]
if args or not change:
    print("Usage: check-code-review.py --change <change-id> [--strict]", file=sys.stderr)
    sys.exit(2)

path = ROOT / "openspec/changes" / change / "design/evidence/code-review.md"
if not path.is_file() or not path.stat().st_size:
    print(f"ERROR: missing code-review evidence: {path.relative_to(ROOT)}")
    print("Stage 08 must record the code review in design/evidence/code-review.md.")
    sys.exit(1)

base = ROOT / "openspec/changes" / change / "design"
layout_check_path = base / "evidence/figma-layout-check.json"


def resolve_artifact(raw):
    value = raw.strip().strip("`").strip().split("#", 1)[0]
    candidates = [base / value, ROOT / value]
    if value.startswith("design/"):
        candidates.append(base / value[len("design/"):])
    return next((p for p in candidates if p.is_file()), None)


def ui_change():
    audit = base / "figma-audit.md"
    if not audit.is_file():
        return False
    text = audit.read_text(encoding="utf-8")
    return not re.search(r"^- 设计来源状态：N/A\s*$", text, re.M)


def page_ids():
    audit = base / "figma-audit.md"
    if not audit.is_file():
        return []
    text = audit.read_text(encoding="utf-8")
    start = text.find("## PAGE 与节点")
    if start < 0:
        start = text.find("## 页面覆盖")
    end = text.find("\n## ", start + 1) if start >= 0 else -1
    scope = text[start:end if end >= 0 else len(text)] if start >= 0 else text
    return sorted(set(re.findall(r"PAGE-\d{3}", scope)))


text = path.read_text(encoding="utf-8")
errors = []
markers = ("TODO", "TBD", "PENDING", "待确认", "待补充")
for marker in markers:
    if marker.lower() in text.lower():
        errors.append(f"unresolved marker remains: {marker}")

for field in ("Change ID", "Reviewer/tool", "Review date/commit"):
    m = re.search(rf"^-\s*{re.escape(field)}\s*[:：]\s*(.+?)\s*$", text, re.M)
    if not m or not m.group(1).strip() or m.group(1).strip().upper() in {"TODO", "TBD", "PENDING", "N/A", "待确认", "待补充"}:
        errors.append(f"{field} must be filled with a real value")

conclusion = re.search(r"^-\s*Review conclusion\s*[:：]\s*(.+?)\s*$", text, re.M)
allowed_conclusions = {"pass", "passed", "approved", "no blocking findings", "no-blocking-findings"}
if not conclusion or conclusion.group(1).strip().lower() not in allowed_conclusions:
    errors.append("Review conclusion must be PASS/APPROVED/NO_BLOCKING_FINDINGS; unresolved findings block stage 08")

required_sections = ["## Findings by severity", "## Spec compliance, security, data consistency, failure paths"]
for section in required_sections:
    if section not in text:
        errors.append(f"missing section: {section}")

findings_section = ""
start = text.find("## Findings by severity")
if start >= 0:
    end = text.find("\n## ", start + len("## Findings by severity"))
    findings_section = text[start:end if end >= 0 else len(text)]
rows = [line.strip() for line in findings_section.splitlines()
        if line.strip().startswith("|")
        and "Severity" not in line
        and not re.match(r"^\|[\s:|-]+\|$", line.strip())]
no_findings = re.search(r"^-\s*Findings\s*[:：]\s*(none|no findings|无)\s*$", text, re.M | re.I)
if not rows and not no_findings:
    errors.append('Findings must list at least one row, or declare "- Findings: none"')

allowed_status = {"fixed", "resolved", "closed", "accepted", "risk-accepted", "n/a", "none"}
for row in rows:
    cells = [c.strip() for c in row.strip("|").split("|")]
    if len(cells) < 5 or any(not c for c in cells[:5]):
        errors.append(f"finding row is incomplete: {row}")
        continue
    status = cells[4].lower()
    if status not in allowed_status:
        errors.append(f"finding status must be one of {sorted(allowed_status)}; got {cells[4]!r}")
    if any(c.lower() in {"todo", "tbd", "pending", "open"} for c in cells):
        errors.append(f"finding row contains unresolved placeholder: {row}")

# UI Changes must carry machine-readable runtime geometry evidence and a human summary.
if ui_change():
    expected_pages = page_ids()
    if "## UI fidelity" not in text:
        errors.append("UI Change must include a ## UI fidelity section in code-review.md")
    else:
        start_ui = text.find("## UI fidelity")
        end_ui = text.find("\n## ", start_ui + len("## UI fidelity"))
        ui_section = text[start_ui:end_ui if end_ui >= 0 else len(text)]
        ui_rows = []
        for line in ui_section.splitlines():
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue
            if re.match(r"^\|[\s:|-]+\|$", stripped):
                continue
            head = [c.strip() for c in stripped.strip("|").split("|")]
            if head and head[0] == "PAGE":
                continue
            ui_rows.append(stripped)
        allowed_ui_status = {"pass", "fixed", "approved", "deviation_approved", "accepted"}
        covered = set()
        for row in ui_rows:
            cells = [c.strip() for c in row.strip("|").split("|")]
            if len(cells) < 6 or any(not c for c in cells[:6]):
                errors.append(f"UI fidelity row is incomplete: {row}")
                continue
            page = re.search(r"PAGE-\d{3}", cells[0])
            if not page:
                errors.append(f"UI fidelity row missing PAGE id: {row}")
                continue
            pid = page.group(0)
            if expected_pages and pid not in expected_pages:
                errors.append(f"UI fidelity row references unknown PAGE: {pid}")
            covered.add(pid)
            if not re.search(r"\d+:\d+", cells[1]):
                errors.append(f"UI fidelity row missing Figma node: {row}")
            if "figma-layout-check.json" not in cells[3] or not resolve_artifact(
                    (re.findall(r"`([^`]+)`", cells[3]) or [cells[3]])[0]):
                errors.append(f"UI fidelity row missing existing figma-layout-check.json evidence: {row}")
            status = cells[5].lower()
            if status not in allowed_ui_status:
                errors.append(f"UI fidelity conclusion must be PASS/FIXED/APPROVED/DEVIATION_APPROVED; got {cells[5]!r}")
            differences = cells[4].strip()
            benign = {"", "-", "—", "无", "n/a", "none"}
            if differences.lower() not in benign and status != "deviation_approved":
                errors.append(f"UI fidelity row records a difference but is not DEVIATION_APPROVED: {row}")
            if status == "deviation_approved":
                approver = cells[6] if len(cells) > 6 else ""
                if not approver and "审批人" not in cells[4]:
                    errors.append(f"DEVIATION_APPROVED row must name the approver: {row}")
            if any(c.lower() in {"todo", "tbd", "pending", "open"} for c in cells):
                errors.append(f"UI fidelity row contains unresolved placeholder: {row}")
        if expected_pages:
            for pid in expected_pages:
                if pid not in covered:
                    errors.append(f"UI fidelity missing PAGE row: {pid}")

    # Primary machine gate: runtime geometry evidence must exist and pass.
    if not layout_check_path.is_file():
        errors.append("UI Change requires design/evidence/figma-layout-check.json "
                      "(run scripts/check-figma-layout.py)")
    else:
        try:
            evidence = json.loads(layout_check_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"figma-layout-check.json is invalid JSON: {exc}")
            evidence = {}
        if evidence:
            if evidence.get("change_id") != change:
                errors.append(f"figma-layout-check.json change_id {evidence.get('change_id')!r} != {change!r}")
            if evidence.get("result") != "PASS":
                errors.append("figma-layout-check.json result is not PASS")
            evidence_pages = {p.get("page_id"): p for p in evidence.get("pages", [])}
            for pid in expected_pages:
                page = evidence_pages.get(pid)
                if not page:
                    errors.append(f"figma-layout-check.json covers no PAGE {pid}")
                    continue
                if page.get("result") != "PASS":
                    errors.append(f"{pid}: figma-layout-check.json result is not PASS")
                if page.get("missing_elements"):
                    errors.append(f"{pid}: missing asserted elements: {page['missing_elements']}")
                max_delta = page.get("max_delta_px")
                tolerance = page.get("tolerance_px")
                if not isinstance(max_delta, (int, float)) or not isinstance(tolerance, (int, float)):
                    errors.append(f"{pid}: figma-layout-check.json needs numeric max_delta_px/tolerance_px")
                elif max_delta > tolerance:
                    errors.append(f"{pid}: max geometry delta {max_delta}px exceeds tolerance {tolerance}px")
                if not page.get("element_count"):
                    errors.append(f"{pid}: figma-layout-check.json asserted zero elements")

if errors:
    for e in errors:
        print("ERROR:", e)
    print(f"Code review check failed: {len(errors)} issue(s).")
    sys.exit(1)
print(f"Code review check passed: {len(rows)} finding row(s), conclusion approved.")
