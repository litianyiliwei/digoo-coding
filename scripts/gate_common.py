#!/usr/bin/env python3
"""Shared parsers for module-package and Change-slice gates.

Every function resolves the project root from the module-level ``ROOT`` unless an
explicit ``root`` argument is given, so tests may replace ``ROOT`` with a temp dir.

``parse_slice`` returns:
  primary (str), owner_module (str), related_modules (list[str]), shape (str),
  packages (list[str]), owned (list[str]),
  integration (list[{"path","reason","task"}]), module_card (str),
  frozen (list[{"id","path"}]), out_of_context (str),
  present (list of canonical field names found in the block).

``parse_roadmap`` returns {"rows": [dict], "amendments": [dict]} with table rows
keyed by the header names as written in the roadmap.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MAIN_ROADMAP_HEADINGS = {
    "## candidate changes",
    "## 1. 路线图总表",
    "## roadmap overview",
    "## 1. roadmap",
}
AMENDMENT_ROADMAP_HEADINGS = {"## roadmap amendments", "## 路线图修订"}

EXCLUDED_PATTERNS = (
    "openspec/changes/{change_id}/**",
    "openspec/changes/archive/**",
    "workflow/**",
)
EXCLUDED_EXACT = {
    "workflow-state.json",
    "toolkit-lock.json",
    "docs/architecture/baseline-status.md",
    "docs/architecture/baseline-manifest.json",
    "docs/architecture/constraint-registry.json",
    "docs/project/toolchain-report.md",
}

SLICE_HEADING_RE = re.compile(r"^\s*###\s+(implementation slice|实现切片)\s*$", re.I)
NEXT_HEADING_RE = re.compile(r"^#{1,3}\s")
TOP_BULLET_RE = re.compile(r"^-\s+(.*)$")
NESTED_BULLET_RE = re.compile(r"^\s+-\s+(.*)$")

CHANGE_ID_KEYS = {"change id", "change-id", "change_id", "变更 id", "变更id", "变更编号"}
STRATEGIES = {"none", "footprint", "module-packages"}
MODULE_LIST_FIELDS = ("frontend_paths", "backend_paths", "shared_paths", "capabilities")
SLICE_FIELD_ALIASES = {
    "primary capability": "primary",
    "owner module": "owner_module",
    "related modules": "related_modules",
    "slice type/coverage": "shape",
    "slice type": "shape",
    "slice shape": "shape",
    "code packages": "packages",
    "owned paths": "owned",
    "integration paths": "integration",
    "module card": "module_card",
    "frozen approvals": "frozen",
    "out of context": "out_of_context",
}


def _resolve(root: Path | None) -> Path:
    return Path(root) if root is not None else ROOT


def _posix(relpath: str) -> str:
    relpath = relpath.replace("\\", "/")
    return relpath[2:] if relpath.startswith("./") else relpath


def strategy(root: Path | None = None) -> str:
    """Return the project's module strategy; ``none`` only when no layout exists."""
    layout = load_code_layout(root)
    if layout is None:
        return "none"
    value = layout.get("strategy")
    path = _resolve(root) / "docs/architecture/code-layout.json"
    if not isinstance(value, str) or value.strip() not in STRATEGIES:
        raise RuntimeError(
            f"invalid strategy {value!r} in {path}; "
            "expected one of none, footprint, module-packages"
        )
    return value.strip()


def load_code_layout(root: Path | None = None) -> dict | None:
    """Load docs/architecture/code-layout.json; None when the file is absent."""
    path = _resolve(root) / "docs/architecture/code-layout.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(f"invalid code-layout.json at {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise RuntimeError(f"invalid code-layout.json at {path}: top level must be an object")
    return data


def _load_registry(
    root: Path | None, relpath: str, list_fields: tuple[str, ...]
) -> list[dict]:
    """Load a semicolon-separated CSV registry, splitting ``list_fields``."""
    path = _resolve(root) / relpath
    if not path.is_file():
        return []
    try:
        with path.open(newline="", encoding="utf-8-sig") as handle:
            rows = []
            for raw in csv.DictReader(handle):
                row = {
                    (key or "").strip(): (value or "").strip()
                    for key, value in raw.items()
                }
                for field in list_fields:
                    row[field] = _split_list(row.get(field, ""))
                rows.append(row)
            return rows
    except OSError as exc:
        raise RuntimeError(f"cannot read {path.name} at {path}: {exc}") from exc


def load_capabilities(root: Path | None = None) -> list[dict]:
    """Load the capability registry; ``code_packages``/``related_modules`` are lists."""
    return _load_registry(
        root,
        "docs/product/capabilities.csv",
        ("code_packages", "related_modules"),
    )


def load_modules(root: Path | None = None) -> list[dict]:
    """Load the module registry; path and capability columns are split into lists."""
    return _load_registry(root, "docs/product/modules.csv", MODULE_LIST_FIELDS)


def _row_change_id(row: dict) -> str:
    for key, value in row.items():
        normalized = " ".join(key.strip().casefold().split())
        if normalized in CHANGE_ID_KEYS:
            return value.strip()
    return ""


def _is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def _table_after(lines: list[str], heading_index: int) -> list[dict]:
    index = heading_index + 1
    while index < len(lines):
        stripped = lines[index].strip()
        if stripped.startswith("|"):
            break
        if stripped.startswith("## "):
            return []
        index += 1
    table_lines = []
    while index < len(lines) and lines[index].strip().startswith("|"):
        table_lines.append(lines[index].strip())
        index += 1
    if not table_lines:
        return []
    rows = [[cell.strip() for cell in line.strip("|").split("|")] for line in table_lines]
    if len(rows) < 2:
        return []
    header = rows[0]
    data = [row for row in rows[1:] if not _is_separator(row)]
    return [
        {header[i]: (row[i] if i < len(row) else "") for i in range(len(header))}
        for row in data
        if row
    ]


def parse_roadmap(root: Path | None = None) -> dict:
    """Parse the main roadmap table and the amendment table."""
    result = {"rows": [], "amendments": []}
    path = _resolve(root) / "docs/product/proposal-roadmap.md"
    if not path.is_file():
        return result
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise RuntimeError(f"cannot read proposal-roadmap.md at {path}: {exc}") from exc
    for index, line in enumerate(lines):
        heading = line.strip().casefold()
        if heading in MAIN_ROADMAP_HEADINGS and not result["rows"]:
            result["rows"] = _table_after(lines, index)
        elif heading in AMENDMENT_ROADMAP_HEADINGS and not result["amendments"]:
            result["amendments"] = _table_after(lines, index)
    return result


def find_change(roadmap: dict, change_id: str) -> dict | None:
    """Return the main or amendment row for ``change_id``."""
    for section in ("rows", "amendments"):
        for row in roadmap.get(section, []):
            if _row_change_id(row) == change_id:
                return row
    return None


def registered_change(roadmap: dict, change_id: str) -> bool:
    """True when the Change appears in the main roadmap or an approved amendment row."""
    return find_change(roadmap, change_id) is not None


def capability_rows(registry: list[dict], slug: str) -> list[dict]:
    """Return capability registry rows whose ``capability_slug`` equals ``slug``."""
    return [
        row for row in registry if (row.get("capability_slug") or "").strip() == slug
    ]


def module_rows(registry: list[dict], slug: str) -> list[dict]:
    """Return module registry rows whose ``module_slug`` equals ``slug``."""
    return [
        row for row in registry if (row.get("module_slug") or "").strip() == slug
    ]


def _path_list(value) -> list[str]:
    values = value if isinstance(value, list) else _split_list(value or "")
    return [
        item.strip()
        for item in values
        if item.strip() and item.strip().upper() != "N/A"
    ]


def module_paths(registry: list[dict], slugs: list[str]) -> list[str]:
    """Return frontend/backend module paths for ``slugs``, deduplicated in input order."""
    paths = []
    seen = set()
    for slug in slugs:
        for row in module_rows(registry, slug):
            for field in ("frontend_paths", "backend_paths"):
                for path in _path_list(row.get(field)):
                    if path not in seen:
                        seen.add(path)
                        paths.append(path)
    return paths


# Transitional alias kept for callers that still import the old name.
package_paths = module_paths


def _glob_to_regex(pattern: str) -> str:
    pattern = pattern.replace("\\", "/")
    parts = []
    index = 0
    while index < len(pattern):
        char = pattern[index]
        if char == "*":
            if index + 1 < len(pattern) and pattern[index + 1] == "*":
                index += 2
                if index < len(pattern) and pattern[index] == "/":
                    parts.append("(?:[^/]+/)*")
                    index += 1
                else:
                    parts.append(".*")
            else:
                parts.append("[^/]*")
                index += 1
        elif char == "?":
            parts.append("[^/]")
            index += 1
        else:
            parts.append(re.escape(char))
            index += 1
    return "".join(parts)


def path_matches(relpath: str, pattern: str) -> bool:
    """Match a repository-relative path: ``*`` stays in one segment, ``**`` crosses."""
    return re.fullmatch(_glob_to_regex(pattern), _posix(relpath)) is not None


def excluded(relpath: str, change_id: str) -> bool:
    """True for Change design/evidence, workflow state and generated baseline files."""
    relpath = _posix(relpath)
    if relpath in EXCLUDED_EXACT:
        return True
    return any(
        path_matches(relpath, pattern.format(change_id=change_id))
        for pattern in EXCLUDED_PATTERNS
    )


def enumerate_files(root: Path | None = None, change_id: str = "") -> dict[str, str]:
    """Hash tracked and untracked files via git, applying ``excluded`` and skipping missing."""
    base = _resolve(root)
    try:
        proc = subprocess.run(
            ["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
            cwd=str(base),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        raise RuntimeError(f"git ls-files failed in {base}: {exc}") from exc
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or "unknown git error"
        raise RuntimeError(f"git ls-files failed in {base}: {detail}")
    files = {}
    for entry in proc.stdout.split("\0"):
        if not entry:
            continue
        relpath = _posix(entry)
        if excluded(relpath, change_id):
            continue
        path = base / relpath
        if not path.is_file():
            continue
        try:
            files[relpath] = hashlib.sha256(path.read_bytes()).hexdigest()
        except OSError as exc:
            raise RuntimeError(f"cannot read {path}: {exc}") from exc
    return {relpath: files[relpath] for relpath in sorted(files)}


def fingerprint(files: dict[str, str]) -> str:
    """SHA-256 of the canonical (sorted, compact) JSON form of the file map."""
    canonical = json.dumps(files, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _split_list(value: str) -> list[str]:
    return [item.strip() for item in value.split(";") if item.strip()]


def _split_related(value: str) -> list[str]:
    if value.strip().upper().startswith("N/A"):
        return []
    return _split_list(value)


def _slice_entry(text: str) -> dict:
    match = re.match(r"(.+?)\s+[—–-]\s+(.*)$", text)
    if not match:
        return {"path": text.strip(), "reason": "", "task": ""}
    path = match.group(1).strip()
    rest = match.group(2).strip()
    task_match = re.search(r"[;；]\s*task\s+([A-Za-z0-9_.:-]+)\s*$", rest, re.I)
    if task_match:
        return {
            "path": path,
            "reason": rest[: task_match.start()].strip(),
            "task": task_match.group(1).strip(),
        }
    return {"path": path, "reason": rest, "task": ""}


def _frozen_entry(text: str) -> dict:
    match = re.match(r"(.+?)\s+[—–-]\s+(.*)$", text)
    if not match:
        return {"id": text.strip(), "path": ""}
    return {"id": match.group(1).strip(), "path": match.group(2).strip()}


def _field_name(label: str) -> str:
    label = re.sub(r"\s*\(.*\)\s*$", "", label.strip().lower())
    label = " ".join(label.split())
    label = re.sub(r"\s*/\s*", "/", label)
    return SLICE_FIELD_ALIASES.get(label, "")


def parse_slice(design_text: str) -> dict:
    """Parse the ``### Implementation Slice`` / ``### 实现切片`` block of design.md."""
    result = {
        "primary": "",
        "owner_module": "",
        "related_modules": [],
        "shape": "",
        "packages": [],
        "owned": [],
        "integration": [],
        "module_card": "",
        "frozen": [],
        "out_of_context": "",
        "present": [],
    }
    lines = design_text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if SLICE_HEADING_RE.match(line):
            start = index
            break
    if start is None:
        return result
    body = []
    for line in lines[start + 1:]:
        if NEXT_HEADING_RE.match(line):
            break
        body.append(line)

    current = ""
    for line in body:
        nested = NESTED_BULLET_RE.match(line)
        if nested:
            text = nested.group(1).strip()
            if current == "integration":
                result["integration"].append(_slice_entry(text))
            elif current == "frozen":
                result["frozen"].append(_frozen_entry(text))
            continue
        top = TOP_BULLET_RE.match(line)
        if not top:
            continue
        content = top.group(1)
        # A full-width colon is as acceptable as an ASCII one; split only on the
        # first separator so reason text keeps its own punctuation.
        separator = re.search(r"[:：]", content)
        if separator is None:
            current = ""
            continue
        label = content[: separator.start()]
        value = content[separator.end():]
        field = _field_name(label)
        current = field
        value = value.strip()
        if not field:
            continue
        if field not in result["present"]:
            result["present"].append(field)
        if field in ("integration", "frozen"):
            if value and not value.upper().startswith("N/A"):
                parser = _slice_entry if field == "integration" else _frozen_entry
                result[field].append(parser(value))
        elif field == "related_modules":
            result["related_modules"] = _split_related(value)
        elif field in ("packages", "owned"):
            result[field] = _split_list(value)
        else:
            result[field] = value
    return result
