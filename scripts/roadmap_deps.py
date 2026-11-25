#!/usr/bin/env python3
"""Proposal-roadmap dependency graph: parse, validate, and runtime states.

The roadmap is the single machine-readable source of proposal dependencies:

- main table ``Dependencies`` column: ``none`` / ``N/A`` or a ``;`` list of
  registered Change IDs;
- ``## Roadmap Amendments`` table ``Depends On`` column under the same rule;
  only rows with all approval fields filled participate in the graph.

``parse`` reuses ``gate_common.parse_roadmap`` for row parsing and reads only
the table headers and the Ordering Rationale section itself, so no second row
parser exists. ``validate`` returns ``(errors, warnings)``. ``dependency_states``
evaluates direct and transitive dependencies against ``workflow-state.json``.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
import gate_common as gm  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
ROADMAP_REL = "docs/product/proposal-roadmap.md"

DEPENDENCY_KEYS = {
    "dependencies",
    "depends on",
    "depends-on",
    "depends_on",
    "依赖",
    "依赖提案",
    "依赖的提案",
}
APPROVAL_FIELDS = ("Reason", "Requester", "Approver", "Date", "Baseline Impact")
CHANGE_ID_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
TOKEN_SPLIT_RE = re.compile(r"[;；]")
PLACEHOLDER = "PENDING"
RATIONALE_HEADINGS = ("ordering rationale", "排序理由", "顺序理由")
RATIONALE_ARROW_RE = re.compile(r"\s*(?:←|<-|<--|<==?)\s*")


def _resolve(root: Path | None) -> Path:
    return Path(root) if root is not None else ROOT


def _norm(value: str) -> str:
    return " ".join((value or "").strip().casefold().split())


def _row_change_id(row: dict) -> str:
    for key, value in row.items():
        if _norm(key) in gm.CHANGE_ID_KEYS:
            return (value or "").strip()
    return ""


def _cell(row: dict, keys) -> str:
    normalized = {_norm(key) for key in keys}
    for key, value in row.items():
        if _norm(key) in normalized:
            return (value or "").strip()
    return ""


def _is_placeholder_id(change_id: str) -> bool:
    change_id = (change_id or "").strip()
    upper = change_id.upper()
    return (
        not change_id
        or upper == PLACEHOLDER
        or "TODO" in upper
        or (change_id.startswith("<") and change_id.endswith(">"))
    )


def _is_placeholder_cell(value: str) -> bool:
    value = (value or "").strip()
    upper = value.upper()
    return (
        not value
        or upper == PLACEHOLDER
        or "TODO" in upper
        or (value.startswith("<") and value.endswith(">"))
    )


def _is_no_dependency(value: str) -> bool:
    upper = (value or "").strip().upper()
    return upper in {"NONE", "N/A"} or upper.startswith("N/A ")


def _tokens(value: str) -> list[str]:
    return [item.strip() for item in TOKEN_SPLIT_RE.split(value or "") if item.strip()]


def _dependency_tokens(value: str) -> tuple[list[str], bool]:
    """Return (tokens, placeholder). ``none``/``N/A`` yield no tokens."""
    if not (value or "").strip():
        return [], True
    if _is_placeholder_cell(value):
        return [], True
    tokens = [
        token for token in _tokens(value)
        if not _is_no_dependency(token)
    ]
    return tokens, False


def _amendment_approved(row: dict) -> bool:
    return all(
        not _is_placeholder_cell(_cell(row, (label,))) for label in APPROVAL_FIELDS
    )


def _table_header(lines: list[str], headings) -> list[str]:
    for index, line in enumerate(lines):
        if line.strip().casefold() in headings:
            cursor = index + 1
            while cursor < len(lines):
                stripped = lines[cursor].strip()
                if stripped.startswith("|"):
                    return [_norm(cell) for cell in stripped.strip("|").split("|")]
                if stripped.startswith("## "):
                    break
                cursor += 1
    return []


def _rationale(lines: list[str]) -> list[str]:
    for index, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("## "):
            continue
        heading = stripped.casefold()
        if any(marker in heading for marker in RATIONALE_HEADINGS):
            body = []
            for follow in lines[index + 1:]:
                if follow.strip().startswith("## "):
                    break
                body.append(follow)
            return body
    return []


def _header_has_dependencies(columns: list[str]) -> bool:
    return any(column in DEPENDENCY_KEYS for column in columns)


def parse(root: Path | None = None) -> dict:
    """Parse the roadmap dependency entries without judging their validity."""
    base = _resolve(root)
    path = base / ROADMAP_REL
    result = {
        "present": path.is_file(),
        "entries": [],
        "edges": [],
        "registered": [],
        "graph": {},
        "main_columns": [],
        "amendment_columns": [],
        "main_ids": [],
        "rationale": [],
        "errors": [],
        "warnings": [],
    }
    if not path.is_file():
        return result
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return result
    try:
        roadmap = gm.parse_roadmap(root=base)
    except RuntimeError:
        return result

    result["main_columns"] = _table_header(lines, gm.MAIN_ROADMAP_HEADINGS)
    result["amendment_columns"] = _table_header(lines, gm.AMENDMENT_ROADMAP_HEADINGS)
    result["rationale"] = _rationale(lines)

    main_ids: list[str] = []
    for order, row in enumerate(roadmap.get("rows", [])):
        change_id = _row_change_id(row)
        if _is_placeholder_id(change_id):
            continue
        raw = _cell(row, DEPENDENCY_KEYS)
        dependants, placeholder = _dependency_tokens(raw)
        main_ids.append(change_id)
        result["entries"].append(
            {
                "change_id": change_id,
                "depends_on": dependants,
                "source": "main",
                "approved": True,
                "placeholder": placeholder,
                "raw": raw,
                "order": order,
            }
        )
    amendment_ids: list[str] = []
    for order, row in enumerate(roadmap.get("amendments", [])):
        change_id = _row_change_id(row)
        if _is_placeholder_id(change_id):
            continue
        approved = _amendment_approved(row)
        raw = _cell(row, DEPENDENCY_KEYS)
        dependants, placeholder = _dependency_tokens(raw)
        amendment_ids.append(change_id if approved else "")
        result["entries"].append(
            {
                "change_id": change_id,
                "depends_on": dependants,
                "source": "amendment",
                "approved": approved,
                "placeholder": placeholder,
                "raw": raw,
                "order": order,
            }
        )
    result["main_ids"] = main_ids
    result["registered"] = main_ids + [item for item in amendment_ids if item]
    for entry in result["entries"]:
        if not entry["approved"]:
            continue
        graph = result["graph"].setdefault(entry["change_id"], [])
        for dependency in entry["depends_on"]:
            graph.append(dependency)
            result["edges"].append(
                {
                    "change": entry["change_id"],
                    "depends_on": dependency,
                    "source": entry["source"],
                }
            )
    return result


def _find_cycles(graph: dict[str, list[str]]) -> list[list[str]]:
    cycles: list[list[str]] = []
    visited: set[str] = set()
    active: list[str] = []

    def visit(node: str):
        if node in active:
            start = active.index(node)
            cycles.append(active[start:] + [node])
            return
        if node in visited:
            return
        visited.add(node)
        active.append(node)
        for dependency in graph.get(node, []):
            if dependency in graph:
                visit(dependency)
        active.pop()

    for node in graph:
        visit(node)
    return cycles


def validate(parsed: dict, require_dependencies: bool = False) -> tuple[list[str], list[str], list[str]]:
    """Validate dependency syntax, graph shape, ordering and rationale."""
    errors: list[str] = []
    warnings: list[str] = []
    advisories: list[str] = []
    if not parsed.get("present"):
        return errors, warnings, advisories

    if require_dependencies:
        if parsed["main_ids"] and "dependencies" not in parsed["main_columns"]:
            errors.append("roadmap table is missing Dependencies column")
        if parsed["amendment_columns"] and not any(
            column in {"depends on", "depends-on", "depends_on"}
            for column in parsed["amendment_columns"]
        ):
            errors.append(
                "roadmap amendments table is missing Depends On column"
            )

    registered = set(parsed["registered"])
    for entry in parsed["entries"]:
        columns = (
            parsed["main_columns"]
            if entry["source"] == "main"
            else parsed["amendment_columns"]
        )
        if entry["placeholder"]:
            if not _header_has_dependencies(columns):
                # A missing column is reported once above when required; other
                # strategies may legitimately omit dependency information.
                continue
            message = (
                f"dependency column is not filled for {entry['change_id']!r}"
            )
            if require_dependencies:
                errors.append(message)
            else:
                advisories.append(message)
            continue
        if not entry["approved"]:
            continue
        seen: set[str] = set()
        for dependency in entry["depends_on"]:
            if not CHANGE_ID_RE.fullmatch(dependency):
                errors.append(
                    f"{entry['change_id']}: invalid dependency id {dependency!r}; "
                    "use lowercase kebab-case"
                )
                continue
            if dependency == entry["change_id"]:
                errors.append(
                    f"{entry['change_id']}: Change depends on itself"
                )
            if dependency in seen:
                errors.append(
                    f"{entry['change_id']}: duplicate dependency {dependency!r}"
                )
            seen.add(dependency)
            if dependency not in registered:
                errors.append(
                    f"{entry['change_id']}: unknown dependency {dependency!r} "
                    "(not in the main roadmap or an approved amendment)"
                )

    graph_ids = set(parsed["graph"])
    graph = {
        node: [dep for dep in deps if dep in graph_ids]
        for node, deps in parsed["graph"].items()
    }
    for cycle in _find_cycles(graph):
        errors.append("dependency cycle: " + " -> ".join(cycle))

    main_positions = {
        change_id: index
        for index, change_id in enumerate(parsed["main_ids"])
    }
    for edge in parsed["edges"]:
        change, dependency = edge["change"], edge["depends_on"]
        if (
            change in main_positions
            and dependency in main_positions
            and main_positions[dependency] > main_positions[change]
        ):
            advisories.append(
                f"{change}: dependency {dependency!r} is listed after it; "
                "explain the ordering in Ordering Rationale or reorder rows"
            )
        rationale = "\n".join(parsed["rationale"])
        pattern = re.compile(
            r"(?<![\w-])" + re.escape(change) + RATIONALE_ARROW_RE.pattern
            + re.escape(dependency) + r"\s*[:：]"
        )
        if not pattern.search(rationale):
            advisories.append(
                f"{change}: ordering rationale is missing '- {change} ← "
                f"{dependency}: <reason>'"
            )
    return errors, warnings, advisories


def _state_ids(value) -> set[str]:
    ids: set[str] = set()
    for item in value or []:
        if isinstance(item, dict):
            identifier = item.get("change_id") or item.get("id")
            if isinstance(identifier, str) and identifier.strip():
                ids.add(identifier.strip())
        elif isinstance(item, str) and item.strip():
            ids.add(item.strip())
    return ids


def _accepted_changes(state: dict) -> set[str]:
    completed = _state_ids(state.get("completed_changes"))
    transitions = {
        row.get("change_id")
        for row in state.get("transition_history") or []
        if isinstance(row, dict)
        and row.get("step_id") == "10-acceptance-audit"
        and isinstance(row.get("change_id"), str)
    }
    return completed & transitions


def _base_status(
    parsed: dict, state: dict, change_id: str
) -> tuple[str, str]:
    completed = _accepted_changes(state)
    if change_id in completed:
        return "ACCEPTED", ""
    changes = state.get("changes") or {}
    lane = changes.get(change_id) if isinstance(changes, dict) else None
    if isinstance(lane, dict) and str(lane.get("status", "")).upper() == "ACTIVE":
        return "ACTIVE", str(lane.get("current_step") or "")
    if state.get("active_change_id") == change_id and change_id not in completed:
        return "ACTIVE", str(state.get("current_step") or "")
    if change_id in _state_ids(state.get("abandoned_changes")):
        return "ABANDONED", ""
    if change_id in set(parsed.get("registered") or []):
        return "NOT_STARTED", ""
    return "UNKNOWN", ""


def dependency_states(parsed: dict, state: dict, change_id: str) -> list[dict]:
    """Return the status of every direct dependency plus transitive breakage."""
    graph = parsed.get("graph") or {}
    cycles = _find_cycles(graph)
    cycle_nodes = {node for cycle in cycles for node in cycle}
    results: list[dict] = []

    def reaches_cycle(node: str, seen: frozenset[str]) -> bool:
        if node in cycle_nodes:
            return True
        if node in seen:
            return False
        return any(
            reaches_cycle(upstream, seen | {node})
            for upstream in graph.get(node, [])
        )

    def evaluate(node: str, path: list[str], visiting: tuple[str, ...]) -> dict:
        if node in visiting:
            return {"status": "BROKEN", "chain": path + [node]}
        status, stage = _base_status(parsed, state, node)
        if status == "ACCEPTED":
            for upstream in graph.get(node, []):
                outcome = evaluate(upstream, path + [node], visiting + (node,))
                if outcome["status"] != "ACCEPTED":
                    return {
                        "status": "BROKEN",
                        "chain": outcome.get("chain") or path + [node],
                    }
            return {"status": "ACCEPTED", "stage": stage}
        return {"status": status, "stage": stage, "chain": path + [node]}

    for dependency in graph.get(change_id, []):
        if reaches_cycle(dependency, frozenset()):
            item = {
                "id": dependency,
                "status": "BROKEN",
                "stage": "",
                "chain": [change_id] + _cycle_chain(dependency, graph),
            }
            results.append(item)
            continue
        outcome = evaluate(dependency, [change_id], (change_id,))
        item = {
            "id": dependency,
            "status": outcome["status"],
            "stage": outcome.get("stage", ""),
        }
        if outcome["status"] == "BROKEN":
            item["chain"] = outcome.get("chain") or [change_id, dependency]
        results.append(item)
    return results


def _cycle_chain(node: str, graph: dict[str, list[str]]) -> list[str]:
    """Return one short cycle path starting at ``node`` for error output."""
    stack = [(node, [node])]
    seen: set[str] = set()
    while stack:
        current, path = stack.pop()
        if current in seen:
            continue
        seen.add(current)
        for upstream in graph.get(current, []):
            if upstream == node:
                return path + [upstream]
            if upstream in graph and upstream not in path:
                stack.append((upstream, path + [upstream]))
    return [node]
