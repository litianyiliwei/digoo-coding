#!/usr/bin/env python3
"""Validate stage method evidence (OpenSpec/Superpowers participation).

The policy lives in process/STEP-ARTIFACT-CONTRACTS.json under ``method_policy``.
If that key is absent, a built-in policy is used so old packages still get a
useful check.

Each stage evidence JSON carries a ``methods`` array. A method entry records the
skill used, the mode, the questions asked, alternatives compared, decisions
made, open questions, the artifact section where the result was written, and a
real evidence path. The validator proves participation, mode, evidence, and
landing; it deliberately does not impose minimum counts on questions,
alternatives, or decisions, nor keyword-match the topics discussed. Those
counts measure form rather than substance, and stage review plus the
downstream-consumption test judge whether the method was actually used well.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DEFAULT_POLICY: dict[str, dict[str, Any]] = {
    "02-requirements-analysis": {
        "required": [
            {"skill": "brainstorming", "requires_artifact": True, "level": "advisory"},
            {"skill": "internet-research", "requires_artifact": True, "level": "advisory"},
            {"skill": "competitor-research", "requires_artifact": True, "level": "advisory"},
        ]
    },
    "03-project-architecture-baseline": {
        "required": [
            {"skill": "brainstorming", "requires_artifact": True, "level": "advisory"}
        ]
    },
    "04-proposal-planning": {
        "required": [
            {"skill": "brainstorming", "requires_artifact": True, "level": "advisory"}
        ]
    },
    "05-feature-requirements": {
        "required": [
            {"skill": "brainstorming", "requires_artifact": True, "level": "advisory"},
            {"skill": "baseline-impact-classification", "requires_artifact": True, "level": "hard"},
        ]
    },
    "06-figma-design-review": {
        "optional": True,
        "required": [
            {"skill": "brainstorming", "requires_artifact": True, "level": "advisory"}
        ],
    },
    "07-detailed-design": {
        "required": [
            {"skill": "brainstorming", "requires_artifact": True, "level": "advisory"},
            {"skill": "writing-plans", "requires_artifact": True, "level": "advisory"},
            {"skill": "existing-code-impact-analysis", "requires_artifact": True, "level": "advisory"},
        ]
    },
    "08-implementation-orchestrator": {
        "required": [
            {"skill": "test-driven-development", "requires_artifact": False, "level": "advisory"},
            {"skill": "verification-before-completion", "requires_artifact": False, "level": "advisory"},
        ]
    },
    "09-independent-verification": {
        "required": [
            {"skill": "verification-before-completion", "requires_artifact": False, "level": "hard"}
        ]
    },
    "10-acceptance-audit": {
        "required": [
            {"skill": "verification-before-completion", "requires_artifact": False, "level": "hard"},
            {"skill": "baseline-impact-classification", "requires_artifact": True, "level": "hard"},
        ]
    },
}

VALID_MODES = {"full", "stage-scoped", "equivalent"}


def load_policy(root: Path) -> dict[str, dict[str, Any]]:
    """Read method_policy from the stage contract, falling back to DEFAULT_POLICY.

    The toolkit installs the contract under ``process/``; older package layouts
    may keep a copy under ``docs/``. Prefer the installed location so the JSON
    policy is actually authoritative.
    """
    for rel in ("process/STEP-ARTIFACT-CONTRACTS.json", "docs/STEP-ARTIFACT-CONTRACTS.json"):
        contract = root / rel
        try:
            data = json.loads(contract.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError):
            continue
        policy = data.get("method_policy")
        if isinstance(policy, dict) and policy:
            return policy
    return DEFAULT_POLICY


def _inside(root: Path, rel: str) -> Path | None:
    """Resolve a repo-relative path and return it only when it stays inside root."""
    if not rel or not str(rel).strip():
        return None
    rel = str(rel).strip()
    if "<change-id>" in rel:
        return None
    path = (root / rel).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        return None
    return path


def _resolve(rel: str, change_id: str | None) -> str:
    if change_id:
        return str(rel).replace("<change-id>", change_id)
    return str(rel)


def _heading_matches(path: Path, heading: str) -> bool:
    if not heading:
        return False
    body = path.read_text(encoding="utf-8", errors="replace")
    wanted = heading.lstrip("#").strip()
    return bool(wanted) and wanted in body


def _validate_entry(entry: Any, root: Path, change_id: str | None, required: dict[str, Any] | None) -> list[str]:
    errors: list[str] = []
    if not isinstance(entry, dict):
        return ["method entry must be an object"]
    skill = str(entry.get("skill") or "").strip()
    if not skill:
        errors.append("method entry requires skill")
    mode = str(entry.get("mode") or "").strip()
    if mode not in VALID_MODES:
        errors.append(f"method entry {skill or '<unknown>'}: mode must be one of {sorted(VALID_MODES)}")
    if mode == "equivalent" and not str(entry.get("reason") or "").strip():
        errors.append(f"method entry {skill or '<unknown>'}: equivalent mode requires reason")

    artifact_section = _resolve(str(entry.get("artifact_section") or ""), change_id)
    evidence = _resolve(str(entry.get("evidence") or ""), change_id)
    if required and required.get("requires_artifact") and not artifact_section:
        errors.append(f"{skill}: requires artifact_section")
    if not evidence:
        errors.append(f"{skill or '<unknown>'}: requires evidence path")
    elif _inside(root, evidence) is None:
        errors.append(f"{skill or '<unknown>'}: evidence path escapes project root: {evidence}")
    else:
        p = _inside(root, evidence)
        if p is None or not p.is_file():
            errors.append(f"{skill or '<unknown>'}: evidence file missing: {evidence}")
    if artifact_section:
        if "#" not in artifact_section:
            errors.append(f"{skill or '<unknown>'}: artifact_section must be '<path>#<heading>'")
        else:
            path_part, heading = artifact_section.split("#", 1)
            p = _inside(root, path_part)
            if p is None or not p.is_file():
                errors.append(f"{skill or '<unknown>'}: artifact section file missing: {path_part}")
            elif not _heading_matches(p, heading):
                errors.append(f"{skill or '<unknown>'}: artifact heading not found: {heading.strip()}")
    return errors


def _spec_level(spec: dict[str, Any]) -> str:
    """Return 'advisory' or 'hard'. Omitted level defaults to 'hard' for backward compatibility."""
    raw = str(spec.get("level") or "hard").strip().lower()
    return "advisory" if raw == "advisory" else "hard"


def validate_methods_detailed(
    evidence: dict[str, Any], step_id: str, root: Path
) -> tuple[list[str], list[str]]:
    """Return (hard_errors, advisory_warnings) for stage method evidence."""
    policy = load_policy(root)
    rule = policy.get(step_id)
    if not rule:
        return [], []
    required_specs = rule.get("required") or []
    methods = evidence.get("methods")
    if methods is not None and not isinstance(methods, list):
        return [f"{step_id}: evidence.methods must be an array"], []
    if not methods:
        if rule.get("optional"):
            return [], []
        hard_errors: list[str] = []
        advisory_warnings: list[str] = []
        for spec in required_specs:
            if _spec_level(spec) == "hard":
                hard_errors.append(f"{step_id}: missing required method skill: {spec.get('skill')}")
            else:
                advisory_warnings.append(f"{step_id}: missing advisory method skill: {spec.get('skill')}")
        if hard_errors:
            hard_errors.insert(0, f"{step_id}: evidence.methods is required (at least one method entry)")
        elif not required_specs:
            hard_errors.append(f"{step_id}: evidence.methods is required (at least one method entry)")
        return list(dict.fromkeys(hard_errors)), list(dict.fromkeys(advisory_warnings))

    change_id = evidence.get("change_id") or None
    hard_errors = []
    advisory_warnings = []
    for entry in methods:
        hard_errors.extend(_validate_entry(entry, root, change_id, None))

    for spec in required_specs:
        wanted = str(spec.get("skill") or "").lower()
        target = hard_errors if _spec_level(spec) == "hard" else advisory_warnings
        label = "required" if _spec_level(spec) == "hard" else "advisory"
        candidates = [e for e in methods if isinstance(e, dict) and wanted in str(e.get("skill") or "").lower()]
        if not candidates:
            target.append(f"{step_id}: missing {label} method skill: {spec.get('skill')}")
            continue
        candidate_errors: list[list[str]] = []
        for entry in candidates:
            candidate_errors.append(_validate_entry(entry, root, change_id, spec))
        if all(errs for errs in candidate_errors):
            target.append(f"{step_id}: no valid evidence for {label} method skill: {spec.get('skill')}")
            target.extend(candidate_errors[0])
    return list(dict.fromkeys(hard_errors)), list(dict.fromkeys(advisory_warnings))


def validate_methods(evidence: dict[str, Any], step_id: str, root: Path) -> list[str]:
    """Return blocking (hard) method-evidence errors; empty list means the stage passed."""
    hard_errors, _ = validate_methods_detailed(evidence, step_id, root)
    return hard_errors


def method_policy_for(step_id: str, root: Path) -> dict[str, Any] | None:
    return load_policy(root).get(step_id)
