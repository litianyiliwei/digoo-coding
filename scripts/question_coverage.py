#!/usr/bin/env python3
"""Validate a stage evidence file's question-coverage block.

The policy lives in ``docs/STEP-ARTIFACT-CONTRACTS.json`` under
``question_coverage_policy``. If that key is absent, a conservative built-in
policy for stages 02/03/05/07 is used so older packages still get a useful
check.

Each required checklist item must appear exactly once in the evidence's
``question_coverage`` array. The status decides which fields are mandatory:

- ``answered``: ``landing`` must point to an existing artifact (optionally with
  ``#heading``); this is the evidence that the answer reached the artifact.
- ``open``: ``owner``, ``blocking`` and ``open_question`` are required; the
  open-question file must exist.
- ``n/a``: ``reason`` is required.
- ``deferred``: ``reason``, ``approver`` and ``target_step`` are required.

The checker proves structure and provenance, not that the answer is correct.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DEFAULT_POLICY: dict[str, Any] = {
    "checklist": "docs/QUESTION-COVERAGE-CHECKLIST.md",
    "stages": {
        "02-requirements-analysis": {
            "required_items": [
                "02-T01-01", "02-T02-01", "02-T03-01", "02-T04-01", "02-T04-02",
                "02-T05-01", "02-T06-01", "02-T07-01", "02-T07-02", "02-T08-01",
                "02-T09-01", "02-T10-01", "02-T11-01", "02-T13-01", "02-T14-01",
                "02-T15-01",
            ]
        },
        "03-project-architecture-baseline": {
            "required_items": [
                "03-T01-01", "03-T02-01", "03-T02-02", "03-T03-01", "03-T04-01",
                "03-T05-01", "03-T06-01", "03-T07-01", "03-T07-02", "03-T08-01",
                "03-T09-01", "03-T10-01", "03-T11-01", "03-T12-01", "03-T13-01",
                "03-T14-01",
            ]
        },
        "05-feature-requirements": {
            "required_items": [
                "05-T01-01", "05-T03-01", "05-T04-01", "05-T05-01", "05-T06-01",
                "05-T07-01", "05-T08-01", "05-T09-01", "05-T10-01", "05-T11-01",
                "05-T14-01", "05-T15-01", "05-T13-01",
            ]
        },
        "07-detailed-design": {
            "required_items": [
                "07-T01-01", "07-T04-01", "07-T05-01", "07-T06-01", "07-T07-01",
                "07-T08-01", "07-T09-01", "07-T10-01", "07-T11-01", "07-T12-01",
                "07-T12-02", "07-T15-01", "07-T15-02", "07-T13-01", "07-T03-01",
            ]
        },
    },
}

STATUS_ALIASES = {
    "answered": "answered",
    "answer": "answered",
    "已答": "answered",
    "n/a": "n/a",
    "na": "n/a",
    "not applicable": "n/a",
    "不适用": "n/a",
    "open": "open",
    "pending": "open",
    "待确认": "open",
    "deferred": "deferred",
    "delay": "deferred",
    "延后": "deferred",
}

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def load_policy(root: Path) -> dict[str, Any]:
    """Read question_coverage_policy from the contract, falling back to the default."""
    contract = root / "docs" / "STEP-ARTIFACT-CONTRACTS.json"
    try:
        data = json.loads(contract.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return DEFAULT_POLICY
    policy = data.get("question_coverage_policy")
    if isinstance(policy, dict) and isinstance(policy.get("stages"), dict):
        if policy["stages"]:
            return policy
    return DEFAULT_POLICY


def _resolve(value: str, change_id: str | None) -> str:
    if change_id:
        return str(value).replace("<change-id>", change_id)
    return str(value)


def _inside(root: Path, rel: str, change_id: str | None) -> Path | None:
    rel = _resolve(rel.strip(), change_id)
    if not rel or "<change-id>" in rel:
        return None
    path = (root / rel).resolve()
    try:
        path.relative_to(root.resolve())
    except ValueError:
        return None
    return path


def _validate_path(value: Any, root: Path, change_id: str | None, label: str) -> list[str]:
    raw = str(value or "").strip()
    if not raw:
        return [f"{label} is required"]
    path_part, heading = raw, ""
    if "#" in raw:
        path_part, heading = raw.split("#", 1)
        heading = heading.strip()
    path = _inside(root, path_part, change_id)
    if path is None:
        return [f"{label} escapes the project root or still contains <change-id>: {raw}"]
    if not path.is_file():
        return [f"{label} file missing: {path_part}"]
    if heading:
        body = path.read_text(encoding="utf-8", errors="replace")
        if heading not in body:
            return [f"{label} heading not found in {path_part}: {heading}"]
    return []


def _validate_entry(entry: dict[str, Any], root: Path, change_id: str | None) -> list[str]:
    errors: list[str] = []
    item_id = str(entry.get("item_id") or "").strip()
    if not item_id:
        return ["item_id is required"]

    raw_status = str(entry.get("status") or "").strip()
    status = STATUS_ALIASES.get(raw_status.lower())
    if not status:
        return [f"{item_id}: status must be answered/n/a/open/deferred (got {raw_status!r})"]

    date = entry.get("date")
    if date is not None and str(date).strip():
        if not DATE_RE.match(str(date).strip()):
            errors.append(f"{item_id}: date must be YYYY-MM-DD")

    if status == "answered":
        errors.extend(_validate_path(entry.get("landing"), root, change_id, f"{item_id}: landing"))
    elif status == "open":
        if not str(entry.get("owner") or "").strip():
            errors.append(f"{item_id}: open requires owner")
        if not str(entry.get("blocking") or "").strip():
            errors.append(f"{item_id}: open requires blocking")
        errors.extend(
            _validate_path(entry.get("open_question"), root, change_id, f"{item_id}: open_question")
        )
    elif status == "n/a":
        if not str(entry.get("reason") or "").strip():
            errors.append(f"{item_id}: n/a requires reason")
    elif status == "deferred":
        if not str(entry.get("reason") or "").strip():
            errors.append(f"{item_id}: deferred requires reason")
        if not str(entry.get("approver") or "").strip():
            errors.append(f"{item_id}: deferred requires approver")
        if not str(entry.get("target_step") or "").strip():
            errors.append(f"{item_id}: deferred requires target_step")
    return errors


def validate_coverage(evidence: dict[str, Any], step_id: str, root: Path) -> list[str]:
    """Return question-coverage errors; an empty list means the stage passed."""
    policy = load_policy(root)
    rule = policy.get("stages", {}).get(step_id)
    if not rule:
        return []

    required = [str(x).strip() for x in (rule.get("required_items") or []) if str(x).strip()]
    if not required:
        return [f"{step_id}: question_coverage policy has no required_items"]

    entries = evidence.get("question_coverage")
    if entries is None:
        return [f"{step_id}: evidence.question_coverage is required (one entry per required item)"]
    if not isinstance(entries, list) or not entries:
        return [f"{step_id}: evidence.question_coverage must be a non-empty array"]

    change_id = evidence.get("change_id") or None
    errors: list[str] = []
    seen: dict[str, dict[str, Any]] = {}
    required_set = set(required)

    for index, entry in enumerate(entries, 1):
        if not isinstance(entry, dict):
            errors.append(f"entry {index}: must be an object")
            continue
        item_id = str(entry.get("item_id") or "").strip()
        if not item_id:
            errors.append(f"entry {index}: item_id is required")
            continue
        if item_id in seen:
            errors.append(f"duplicate item_id: {item_id}")
            continue
        seen[item_id] = entry
        if item_id not in required_set:
            errors.append(f"unknown item_id for {step_id}: {item_id}")
        errors.extend(_validate_entry(entry, root, change_id))

    missing = [item for item in required if item not in seen]
    if missing:
        errors.append(f"{step_id}: missing required items: {', '.join(missing)}")

    return list(dict.fromkeys(errors))


def policy_for(step_id: str, root: Path) -> dict[str, Any] | None:
    return load_policy(root).get("stages", {}).get(step_id)
