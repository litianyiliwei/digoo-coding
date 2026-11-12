#!/usr/bin/env python3
"""Validate independent verification report and machine-readable evidence.

UI Changes are verified by independent runtime geometry measurements
(`layout_checks` + `figma-layout-check.json`), not by screenshots.
"""
import argparse, json, re, sys
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("--report", required=True)
p.add_argument("--evidence", required=True)
a = p.parse_args()
root = Path(__file__).resolve().parents[1]


def resolve(raw):
    x = Path(raw)
    x = (root / x).resolve() if not x.is_absolute() else x.resolve()
    x.relative_to(root.resolve())
    return x


try:
    report = resolve(a.report)
    evidence = resolve(a.evidence)
    if not report.is_file() or not evidence.is_file():
        raise ValueError("Report and evidence JSON must both exist")
    md = report.read_text(encoding="utf-8")
    d = json.loads(evidence.read_text(encoding="utf-8"))
    required = [
        "change_id", "verdict", "source_revision", "revision_stable", "read_only",
        "verifier_identity", "builder_identity", "acceptance_checks", "test_runs", "findings",
    ]
    missing = [k for k in required if k not in d]
    if missing:
        raise ValueError("Missing evidence fields: " + ", ".join(missing))
    errors = []
    if d["verdict"] != "PASS":
        errors.append("verdict is not PASS")
    if not d["source_revision"]:
        errors.append("source_revision is empty")
    if d["revision_stable"] is not True:
        errors.append("revision_stable must be true")
    if d["read_only"] is not True:
        errors.append("read_only must be true")
    if not d["verifier_identity"] or not d["builder_identity"] or d["verifier_identity"] == d["builder_identity"]:
        errors.append("verifier_identity and builder_identity must be present and distinct")
    if not d["acceptance_checks"]:
        errors.append("acceptance_checks is empty")
    for ac in d["acceptance_checks"]:
        if not ac.get("id") or ac.get("result") != "PASS" or not ac.get("evidence"):
            errors.append(f"AC not independently passed: {ac.get('id', '<missing>')}")
    if not d["test_runs"]:
        errors.append("test_runs is empty")
    for t in d["test_runs"]:
        if not t.get("command") or t.get("exit_code") != 0:
            errors.append(f"Test command failed or missing exit code: {t.get('command', '<missing>')}")
        if not t.get("log"):
            errors.append(f"Test run log is missing: {t.get('command', '<missing>')}")
        else:
            lp = Path(t["log"])
            lp = (root / lp).resolve() if not lp.is_absolute() else lp.resolve()
            try:
                lp.relative_to(root.resolve())
            except ValueError:
                errors.append("Test log path escapes project root")
            else:
                if not lp.is_file():
                    errors.append(f"Test log file does not exist: {t['log']}")
    blockers = [f for f in d["findings"] if f.get("severity") in ("BLOCKER", "CRITICAL")]
    if blockers:
        errors.append(f"{len(blockers)} blocker/critical finding(s) remain")
    if not any(x in md for x in ("判定：PASS", "Verdict: PASS", "Verdict：PASS")):
        errors.append("Markdown report does not state PASS")
    for heading in ("## 1. 验证范围", "## 2. 验收标准", "## 3. 测试与检查", "## 7. 最终判定"):
        if heading not in md:
            errors.append(f"Markdown report missing section: {heading}")

    # UI-bearing Changes require per-PAGE independent runtime geometry evidence.
    change = d["change_id"]
    base = root / "openspec" / "changes" / str(change) / "design"
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

    def resolve_artifact(raw):
        value = str(raw).strip().strip("`").strip().split("#", 1)[0]
        candidates = [base / value, root / value]
        if value.startswith("design/"):
            candidates.append(base / value[len("design/"):])
        return next((x for x in candidates if x.is_file()), None)

    if ui_change:
        if "## UI 一致性验证" not in md:
            errors.append("UI Change report missing section: ## UI 一致性验证")
        checks = d.get("layout_checks") or []
        if not checks:
            errors.append("UI Change requires layout_checks with per-PAGE runtime geometry evidence")
        covered = set()
        for ui in checks:
            pid = ui.get("page_id")
            covered.add(pid)
            if not re.fullmatch(r"PAGE-\d{3}", str(pid or "")):
                errors.append(f"layout_check has invalid page_id: {pid!r}")
                continue
            if not re.search(r"\d+:\d+", str(ui.get("figma_node", ""))):
                errors.append(f"{pid}: layout_check missing Figma node")
            if not isinstance(ui.get("asserted_elements"), int) or ui["asserted_elements"] <= 0:
                errors.append(f"{pid}: asserted_elements must be a positive integer")
            if not isinstance(ui.get("max_delta_px"), (int, float)):
                errors.append(f"{pid}: max_delta_px must be numeric")
            if not isinstance(ui.get("tolerance_px"), (int, float)) or ui["tolerance_px"] <= 0:
                errors.append(f"{pid}: tolerance_px must be a positive number")
            if ui.get("max_delta_px", 0) > ui.get("tolerance_px", 0):
                errors.append(f"{pid}: max_delta_px exceeds tolerance_px")
            if ui.get("missing_elements"):
                errors.append(f"{pid}: missing asserted elements: {ui['missing_elements']}")
            if ui.get("result") != "PASS":
                errors.append(f"UI check not PASS: {pid}")
            if not str(ui.get("evidence", "")).strip():
                errors.append(f"UI check missing evidence: {pid}")
            elif not resolve_artifact(ui.get("evidence", "")):
                errors.append(f"{pid}: layout evidence file not found: {ui.get('evidence')}")
            elif "figma-layout-check.json" not in str(ui.get("evidence", "")):
                errors.append(f"{pid}: layout evidence must reference figma-layout-check.json")
            differences = str(ui.get("differences", "")).strip()
            if differences and differences.lower() not in {"-", "—", "无", "n/a", "none"}:
                if not ui.get("deviation_approved"):
                    errors.append(f"{pid}: recorded differences require deviation_approved=true")
                if not str(ui.get("approved_by", "")).strip():
                    errors.append(f"{pid}: approved deviation requires approved_by")
        for pid in expected_pages:
            if pid not in covered:
                errors.append(f"UI check missing PAGE: {pid}")
        if not any("check-figma-layout.py" in str(t.get("command", "")) for t in d["test_runs"]):
            errors.append("UI Change requires an independent check-figma-layout.py test run")

    if errors:
        print("INDEPENDENT_VERIFICATION_FAILED")
        for e in errors:
            print(" - " + e)
        sys.exit(3)
    print(f"INDEPENDENT_VERIFICATION_PASS change_id={d['change_id']} "
          f"AC={len(d['acceptance_checks'])} tests={len(d['test_runs'])}")
except Exception as e:
    print(f"ERROR: {e}", file=sys.stderr)
    sys.exit(2)
