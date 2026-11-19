#!/usr/bin/env python3
"""Validate docs/architecture/quality-gates.json structure and selection.

When the file is absent and ``--require-materialized`` is not passed, static
analysis has not been adopted: the checker reports ``QUALITY_GATES_NOT_ADOPTED``
and exits 0 so stage 03 can freeze the baseline without the gates. With
``--require-materialized`` (08/09/CI adopted mode), a missing file is an error.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from quality_gates import GATES_REL, validate_gates

ROOT = Path(__file__).resolve().parents[1]
TECHNOLOGY_REL = "docs/architecture/technology-decisions.md"
TECHNOLOGY_SECTION_RE = re.compile(r"(?m)^##\s+Static Analysis Toolchain")


def validate_technology(root: Path, data: dict) -> list[str]:
    """Cross-check technology-decisions.md against the selected stack languages."""
    path = root / TECHNOLOGY_REL
    if not path.is_file():
        return [f"{TECHNOLOGY_REL} is missing"]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"cannot read {TECHNOLOGY_REL}: {exc}"]

    errors: list[str] = []
    if not TECHNOLOGY_SECTION_RE.search(text):
        errors.append(
            f"{TECHNOLOGY_REL} is missing the '## Static Analysis Toolchain' section"
        )
    stacks = data.get("stacks") if isinstance(data, dict) else None
    if isinstance(stacks, list):
        lowered = text.lower()
        for stack in stacks:
            if not isinstance(stack, dict):
                continue
            language = stack.get("language")
            if isinstance(language, str) and language.strip() and language.lower() not in lowered:
                errors.append(
                    f"{TECHNOLOGY_REL} does not mention stack language: {language}"
                )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(ROOT), help="Project root (defaults to this package)")
    parser.add_argument("--strict", action="store_true",
                        help="Also cross-check technology-decisions.md")
    parser.add_argument("--require-materialized", action="store_true",
                        help="Also require stack roots and config files to exist")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    gates_path = root / GATES_REL
    if not gates_path.is_file():
        if args.require_materialized:
            print(f"ERROR: cannot read {GATES_REL}: file is missing (--require-materialized expects adopted gates)")
            return 1
        print(f"QUALITY_GATES_NOT_ADOPTED: {GATES_REL} is absent; static-analysis gates are dormant.")
        return 0
    try:
        data = json.loads(gates_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        print(f"ERROR: cannot read {GATES_REL}: {exc}")
        return 1

    errors = validate_gates(data, root, require_materialized=args.require_materialized)
    if args.strict:
        errors.extend(validate_technology(root, data))

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("QUALITY_GATES_CHECK_PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
