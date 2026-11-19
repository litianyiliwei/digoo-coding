#!/usr/bin/env python3
"""Validate an optional stage evidence ``question_coverage`` block.

``process/QUESTION-COVERAGE-CHECKLIST.md`` is a recommended elicitation aid,
not a machine gate. An evidence file may omit the block entirely, and the block
does not have to cover a fixed item list.

If the block is present, each entry must have a valid status and the fields
that status requires:

- ``answered``: ``landing`` must point to an existing artifact (optionally with
  ``#heading``); this is the evidence that the answer reached the artifact.
- ``open``: ``owner``, ``blocking`` and ``open_question`` are required; the
  open-question file must exist.
- ``n/a``: ``reason`` is required.
- ``deferred``: ``reason``, ``approver`` and ``target_step`` are required.

Unknown item IDs are allowed, so a stage may record additional questions.
The checker proves structure and provenance, not that the answers are correct.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

DEFAULT_POLICY: dict[str, Any] = {
    "checklist": "process/QUESTION-COVERAGE-CHECKLIST.md",
    "checklist_zh": "process/QUESTION-COVERAGE-CHECKLIST-zh.md",
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
    """Read question_coverage_policy from the stage contract, falling back to the default.

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
        policy = data.get("question_coverage_policy")
        if isinstance(policy, dict) and policy:
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
    """Return optional question-coverage errors; an empty list means the stage passed.

    A stage may omit ``question_coverage`` entirely. When present, entries are
    shape-checked by status; no fixed item list is required.
    """
    entries = evidence.get("question_coverage")
    if entries is None:
        return []
    if not isinstance(entries, list):
        return [f"{step_id}: evidence.question_coverage must be an array when present"]
    if not entries:
        return []

    change_id = evidence.get("change_id") or None
    errors: list[str] = []
    seen: dict[str, dict[str, Any]] = {}

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
        errors.extend(_validate_entry(entry, root, change_id))

    return list(dict.fromkeys(errors))
