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
p.add_argument("--root", default=str(Path(__file__).resolve().parents[1]),
               help="Project root (defaults to this repository)")
a = p.parse_args()
root = Path(a.root).resolve()
GATES_REL = "docs/architecture/quality-gates.json"


def resolve(raw):
    x = Path(raw)
    x = (root / x).resolve() if not x.is_absolute() else x.resolve()
    x.relative_to(root.resolve())
    return x


def blocking_gate_pairs(gates_doc):
    """Return the blocking ``(stack_id, tool_id)`` set, or None if malformed."""
    if not isinstance(gates_doc, dict):
        return None
    stacks = gates_doc.get("stacks")
    if not isinstance(stacks, list):
        return None
    blocking = set()
    for stack in stacks:
        if not isinstance(stack, dict) or not isinstance(stack.get("id"), str):
            continue
        tools = stack.get("tools")
        for tool in tools if isinstance(tools, list) else []:
            if (isinstance(tool, dict)
                    and isinstance(tool.get("id"), str)
                    and tool.get("mode") == "blocking"):
                blocking.add((stack["id"], tool["id"]))
    return blocking


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
    change = d["change_id"]
    stories = root / "openspec" / "changes" / str(change) / "design" / "user-stories.md"
    if stories.is_file():
        expected_acs = set(re.findall(r"AC-\d{3}", stories.read_text(encoding="utf-8")))
        reported_acs = {str(ac.get("id", "")).strip() for ac in d["acceptance_checks"]}
        missing_acs = sorted(expected_acs - reported_acs)
        extra_acs = sorted(reported_acs - expected_acs)
        if missing_acs:
            errors.append("independent acceptance_checks missing AC(s): " + ", ".join(missing_acs))
        if extra_acs:
            errors.append("independent acceptance_checks reference unknown AC(s): " + ", ".join(extra_acs))
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
    for zh, en in (
        ("## 1. 验证范围", "## 1. Verification Scope"),
        ("## 2. 验收标准", "## 2. Acceptance Criteria"),
        ("## 3. 测试与检查", "## 3. Test and Check"),
        ("## 7. 最终判定", "## 7. Final Verdict"),
    ):
        if zh not in md and en not in md:
            errors.append(f"Markdown report missing section: {zh} / {en}")

    # Static-analysis integration: once the project adopts quality gates, the
    # independent verification must cover every blocking stack/tool with its
    # own independent evidence file.
    gates_path = root / GATES_REL
    if gates_path.is_file():
        try:
            gates_doc = json.loads(gates_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            errors.append(f"cannot read {GATES_REL}: {exc}")
            gates_doc = None
        blocking = blocking_gate_pairs(gates_doc) if gates_doc is not None else None
        if gates_doc is not None and blocking is None:
            errors.append(f"{GATES_REL} does not define a valid blocking stack/tool set")
        if blocking is not None:
            checks = d.get("static_checks")
            if not isinstance(checks, list) or not checks:
                errors.append(
                    "quality-gates.json exists but evidence lacks a non-empty "
                    "static_checks block"
                )
                checks = []
            reported = set()
            for index, check in enumerate(checks):
                label = f"static_checks[{index}]"
                if not isinstance(check, dict):
                    errors.append(f"{label} must be an object")
                    continue
                stack_id = check.get("stack_id")
                tool_id = check.get("tool")
                if (isinstance(stack_id, str) and stack_id.strip()
                        and isinstance(tool_id, str) and tool_id.strip()):
                    reported.add((stack_id, tool_id))
                else:
                    errors.append(f"{label}: stack_id and tool must be non-empty strings")
                if check.get("result") != "PASS":
                    errors.append(
                        f"{label}: result must be PASS, found {check.get('result')!r}"
                    )
                if check.get("exit_code") != 0:
                    errors.append(
                        f"{label}: exit_code must be 0, found {check.get('exit_code')!r}"
                    )
                command = check.get("command")
                if not isinstance(command, str) or not command.strip():
                    errors.append(f"{label}: command must be a non-empty string")
                raw_evidence = check.get("evidence")
                if not isinstance(raw_evidence, str) or not raw_evidence.strip():
                    errors.append(f"{label}: evidence must be a non-empty path")
                    continue
                try:
                    nested_path = resolve(raw_evidence)
                except ValueError:
                    errors.append(
                        f"{label}: evidence escapes the project root: {raw_evidence}"
                    )
                    continue
                if not nested_path.is_file():
                    errors.append(f"{label}: evidence file does not exist: {raw_evidence}")
                    continue
                try:
                    nested = json.loads(nested_path.read_text(encoding="utf-8"))
                except (OSError, ValueError) as exc:
                    errors.append(f"{label}: evidence is not readable JSON: {exc}")
                    continue
                if nested.get("independent") is not True:
                    errors.append(f"{label}: evidence must have independent: true")
                if nested.get("verdict") != "PASS":
                    errors.append(
                        f"{label}: evidence verdict must be PASS, found "
                        f"{nested.get('verdict')!r}"
                    )
                verifier = nested.get("verifier_identity")
                builder = nested.get("builder_identity")
                if not (isinstance(verifier, str) and verifier.strip()):
                    errors.append(f"{label}: evidence verifier_identity must be non-empty")
                if not (isinstance(builder, str) and builder.strip()):
                    errors.append(f"{label}: evidence builder_identity must be non-empty")
                if (isinstance(verifier, str) and verifier.strip()
                        and isinstance(builder, str) and builder.strip()
                        and verifier.strip() == builder.strip()):
                    errors.append(
                        f"{label}: evidence verifier_identity and builder_identity "
                        "must be distinct"
                    )
            missing = sorted(blocking - reported)
            extra = sorted(reported - blocking)
            if missing:
                errors.append(
                    "static_checks missing blocking gate(s): "
                    + ", ".join(f"{stack}/{tool}" for stack, tool in missing)
                )
            if extra:
                errors.append(
                    "static_checks reference non-blocking gate(s): "
                    + ", ".join(f"{stack}/{tool}" for stack, tool in extra)
                )

    # UI-bearing Changes require per-PAGE independent runtime geometry evidence.
    base = root / "openspec" / "changes" / str(change) / "design"
    audit = base / "figma-audit.md"
    ui_change = False
    expected_pages = []
    if audit.is_file():
        audit_text = audit.read_text(encoding="utf-8")
        ui_change = not re.search(r"^- (?:设计来源状态|Design source status)[:：]\s*N/A\s*$", audit_text, re.M)
        start = audit_text.find("## PAGE 与节点")
        if start < 0:
            start = audit_text.find("## PAGEs and Nodes")
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
        if "## UI 一致性验证" not in md and "## UI Consistency Verification" not in md:
            errors.append("UI Change report missing section: ## UI Consistency Verification (UI 一致性验证)")
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
            if not re.search(r"\d+\s*:\s*\d+|[A-Za-z_][A-Za-z0-9_.:-]+", str(ui.get("figma_node", ""))):
                errors.append(f"{pid}: layout_check missing design source reference (HTML data-node-id or Figma node)")
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
            elif "figma-layout-check" not in str(ui.get("evidence", "")):
                errors.append(f"{pid}: layout evidence must reference a figma-layout-check JSON file (08 or independent)")
            differences = str(ui.get("differences", "")).strip()
            if differences and differences.lower() not in {"-", "—", "无", "n/a", "none"}:
                if not ui.get("deviation_approved"):
                    errors.append(f"{pid}: recorded differences require deviation_approved=true")
                if not str(ui.get("approved_by", "")).strip():
                    errors.append(f"{pid}: approved deviation requires approved_by")
        for pid in expected_pages:
            if pid not in covered:
                errors.append(f"UI check missing PAGE: {pid}")
        extra_pages = sorted(covered - set(expected_pages)) if expected_pages else []
        if extra_pages:
            errors.append("layout_checks reference PAGE(s) outside the frozen figma-audit PAGE list: " + ", ".join(extra_pages))
        if not any("check-figma-layout.py" in str(t.get("command", "")) for t in d["test_runs"]):
            errors.append("UI Change requires an independent check-figma-layout.py test run")
        if not any("check-design-tokens.py" in str(t.get("command", "")) for t in d["test_runs"]):
            errors.append("UI Change requires an independent check-design-tokens.py test run")

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
