#!/usr/bin/env python3
"""Validate stage method evidence (OpenSpec/Superpowers participation).

The policy lives in docs/STEP-ARTIFACT-CONTRACTS.json under ``method_policy``.
If that key is absent, a conservative built-in policy is used so old packages
still get a useful check.

Each stage evidence JSON carries a ``methods`` array. A method entry records the
skill used, the mode, the questions asked, alternatives compared, decisions
made, open questions, the artifact section where the result was written, and a
real evidence path. The validator is intentionally conservative: it proves that
the evidence exists and has the required shape, not that a human agreed with it.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DEFAULT_POLICY: dict[str, dict[str, Any]] = {
    "02-requirements-analysis": {
        "required": [
            {"skill": "brainstorming", "min_questions": 3, "min_alternatives": 1, "min_decisions": 1, "requires_artifact": True},
            {"skill": "internet-research", "min_questions": 3, "min_alternatives": 2, "min_decisions": 1, "requires_artifact": True},
        ]
    },
    "03-project-architecture-baseline": {
        "required": [
            {"skill": "brainstorming", "min_questions": 4, "min_alternatives": 2, "min_decisions": 1, "requires_artifact": True,
             "required_topics": ["新系统", "现有系统", "代码地址", "第三方接口"]}
        ]
    },
    "04-proposal-planning": {
        "required": [
            {"skill": "brainstorming", "min_questions": 2, "min_alternatives": 2, "min_decisions": 1, "requires_artifact": True}
        ]
    },
    "05-feature-requirements": {
        "required": [
            {"skill": "brainstorming", "min_questions": 3, "min_alternatives": 1, "min_decisions": 1, "requires_artifact": True}
        ]
    },
    "06-figma-design-review": {
        "optional": True,
        "required": [
            {"skill": "brainstorming", "min_questions": 2, "min_alternatives": 1, "min_decisions": 1, "requires_artifact": True}
        ],
    },
    "07-detailed-design": {
        "required": [
            {"skill": "brainstorming", "min_questions": 4, "min_alternatives": 2, "min_decisions": 1, "requires_artifact": True,
             "required_topics": ["现有功能", "新功能", "代码地址", "第三方接口"]},
            {"skill": "writing-plans", "min_questions": 0, "min_alternatives": 0, "min_decisions": 1, "requires_artifact": True},
        ]
    },
    "08-implementation-orchestrator": {
        "required": [
            {"skill": "test-driven-development", "min_questions": 0, "min_alternatives": 0, "min_decisions": 1, "requires_artifact": False},
            {"skill": "verification-before-completion", "min_questions": 0, "min_alternatives": 0, "min_decisions": 1, "requires_artifact": False},
        ]
    },
    "09-independent-verification": {
        "required": [
            {"skill": "verification-before-completion", "min_questions": 0, "min_alternatives": 0, "min_decisions": 1, "requires_artifact": False}
        ]
    },
    "10-acceptance-audit": {
        "required": [
            {"skill": "verification-before-completion", "min_questions": 0, "min_alternatives": 0, "min_decisions": 1, "requires_artifact": False}
        ]
    },
}

VALID_MODES = {"full", "stage-scoped", "equivalent"}


def load_policy(root: Path) -> dict[str, dict[str, Any]]:
    """Read method_policy from the contract, falling back to DEFAULT_POLICY."""
    contract = root / "docs" / "STEP-ARTIFACT-CONTRACTS.json"
    try:
        data = json.loads(contract.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_POLICY
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


def _as_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(x) for x in value if str(x).strip()]
    return []


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

    questions = _as_list(entry.get("questions"))
    alternatives = _as_list(entry.get("alternatives"))
    decisions = _as_list(entry.get("decisions"))
    if required:
        if len(questions) < int(required.get("min_questions", 0)):
            errors.append(f"{skill}: needs at least {required.get('min_questions', 0)} recorded questions")
        if len(alternatives) < int(required.get("min_alternatives", 0)):
            errors.append(f"{skill}: needs at least {required.get('min_alternatives', 0)} recorded alternatives")
        if len(decisions) < int(required.get("min_decisions", 0)):
            errors.append(f"{skill}: needs at least {required.get('min_decisions', 0)} recorded decisions")
        topics = [str(t) for t in (required.get("required_topics") or []) if str(t).strip()]
        searchable = " ".join(questions + alternatives + decisions + [str(entry.get("summary") or "")])
        for topic in topics:
            if topic.lower() not in searchable.lower():
                errors.append(f"{skill}: missing required topic '{topic}' in questions/alternatives/decisions/summary")

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


def validate_methods(evidence: dict[str, Any], step_id: str, root: Path) -> list[str]:
    """Return method-evidence errors; an empty list means the stage passed."""
    policy = load_policy(root)
    rule = policy.get(step_id)
    if not rule:
        return []
    methods = evidence.get("methods")
    if methods is None or not isinstance(methods, list) or not methods:
        if rule.get("optional"):
            return []
        return [f"{step_id}: evidence.methods is required (at least one method entry)"]
    if not isinstance(methods, list):
        return [f"{step_id}: evidence.methods must be an array"]

    change_id = evidence.get("change_id") or None
    errors: list[str] = []
    for entry in methods:
        errors.extend(_validate_entry(entry, root, change_id, None))

    required_specs = rule.get("required") or []
    for spec in required_specs:
        wanted = str(spec.get("skill") or "").lower()
        candidates = [e for e in methods if isinstance(e, dict) and wanted in str(e.get("skill") or "").lower()]
        if not candidates:
            errors.append(f"{step_id}: missing required method skill: {spec.get('skill')}")
            continue
        candidate_errors: list[list[str]] = []
        for entry in candidates:
            candidate_errors.append(_validate_entry(entry, root, change_id, spec))
        if all(errs for errs in candidate_errors):
            errors.append(f"{step_id}: no valid evidence for required method skill: {spec.get('skill')}")
            errors.extend(candidate_errors[0])
    return list(dict.fromkeys(errors))


def method_policy_for(step_id: str, root: Path) -> dict[str, Any] | None:
    return load_policy(root).get(step_id)
