#!/usr/bin/env python3
"""Validate stage 03 existing-system and third-party baseline sections.

The stage 03 interview must answer whether the project is a new system or a
secondary development on an existing system, and which third-party interfaces
it depends on. This checker verifies that the answers are actually written into
the architecture baseline and that existing-system constraints / third-party
constraints are registered in the machine constraint registry.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXISTING_RE = re.compile(r"(?m)^(?:##|###)\s*(?:[0-9]+\.?\s*)?现有系统二开约束.*$")
THIRD_RE = re.compile(r"(?m)^(?:##|###)\s*(?:[0-9]+\.?\s*)?第三方接口依赖清单.*$")
API_THIRD_RE = re.compile(r"(?m)^(?:##|###)\s*(?:[0-9]+\.?\s*)?第三方接口与集成约定.*$")
PLACEHOLDER_RE = re.compile(r"TODO|TBD|PENDING|待确认|待补充|\[填充\]", re.I)
NONE_RE = re.compile(r"^(N/A|NONE|无|不适用)", re.I)


def section_body(text: str, pattern: re.Pattern[str]) -> str | None:
    match = pattern.search(text)
    if not match:
        return None
    start = match.end()
    next_heading = re.search(r"(?m)^(?:##|###)\s", text[start:])
    return (text[start:start + next_heading.start()] if next_heading else text[start:]).strip()


def is_none(body: str) -> bool:
    return bool(NONE_RE.match(body.strip()))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=str(ROOT), help="Project root (defaults to this package)")
    ap.add_argument("--strict", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    tech = root / "docs" / "architecture" / "technology-decisions.md"
    api = root / "docs" / "architecture" / "api-conventions.md"
    flows = root / "docs" / "architecture" / "data-flows.md"
    registry = root / "docs" / "architecture" / "constraint-registry.json"

    errors: list[str] = []
    if not tech.is_file():
        errors.append(f"missing {tech}")
        tech_text = ""
    else:
        tech_text = tech.read_text(encoding="utf-8", errors="replace")

    existing = section_body(tech_text, EXISTING_RE)
    third = section_body(tech_text, THIRD_RE)
    if existing is None:
        errors.append("technology-decisions.md missing heading: 现有系统二开约束")
    if third is None:
        errors.append("technology-decisions.md missing heading: 第三方接口依赖清单")
    if args.strict:
        for name, body in (("现有系统二开约束", existing), ("第三方接口依赖清单", third)):
            if body and PLACEHOLDER_RE.search(body):
                errors.append(f"technology-decisions.md section {name} still contains placeholders")
    if existing and is_none(existing):
        existing_active = False
    else:
        existing_active = bool(existing)
    third_active = bool(third) and not is_none(third)

    if existing_active:
        if not any(keyword in existing for keyword in ("代码地址", "仓库", "commit", "分支")):
            errors.append("现有系统二开约束 must record code access (代码地址/仓库/分支/commit)")
    if third_active:
        if not api.is_file():
            errors.append(f"missing {api}")
        else:
            api_text = api.read_text(encoding="utf-8", errors="replace")
            if not API_THIRD_RE.search(api_text):
                errors.append("api-conventions.md missing heading: 第三方接口与集成约定")
        if not flows.is_file():
            errors.append(f"missing {flows}")
        else:
            flow_text = flows.read_text(encoding="utf-8", errors="replace")
            if not re.search(r"第三方|EXTERNAL", flow_text):
                errors.append("data-flows.md does not mention third-party / EXTERNAL data flow")

    constraints: list[str] = []
    if registry.is_file():
        try:
            data = json.loads(registry.read_text(encoding="utf-8"))
            constraints = [str(c.get("id", "")) for c in data.get("constraints", []) if c.get("id")]
        except json.JSONDecodeError as exc:
            errors.append(f"constraint-registry.json invalid JSON: {exc}")
    else:
        errors.append(f"missing {registry}")
    if existing_active and not any(cid.upper().startswith("LEGACY-") for cid in constraints):
        errors.append("existing-system constraints missing: add LEGACY-* entries to constraint-registry.json")
    if third_active and not any(cid.upper().startswith("EXT-") for cid in constraints):
        errors.append("third-party constraints missing: add EXT-* entries to constraint-registry.json")

    for error in errors:
        print("ERROR:", error)
    if errors:
        print(f"Architecture baseline check failed: {len(errors)} error(s).")
        return 1
    print(f"Architecture baseline passed: existing-system={existing_active}, third-party={third_active}, "
          f"constraints={len(constraints)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
