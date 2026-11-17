#!/usr/bin/env python3
"""Compile every literal regex used by the process gate scripts.

This catches the class of failure where a full-width punctuation character
(e.g. ``）``) is used where an ASCII group close ``)`` was intended. Such a
pattern compiles at import time and only crashes when the gate reaches the
branch that uses it, which previously made UI stages fail silently.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKERS = sorted((ROOT / "scripts").glob("check-*.py"))
REGEX_FUNCS = {"compile", "search", "match", "fullmatch", "findall", "finditer", "sub"}


def literal_regexes(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr not in REGEX_FUNCS:
            continue
        base = func.value
        if not isinstance(base, ast.Name) or base.id != "re":
            continue
        if not node.args:
            continue
        arg = node.args[0]
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            yield node.lineno, arg.value


def main() -> int:
    errors = []
    for path in CHECKERS:
        try:
            patterns = list(literal_regexes(path))
        except SyntaxError as exc:
            errors.append(f"{path.relative_to(ROOT)}:{exc.lineno}: syntax error: {exc.msg}")
            continue
        for line, pattern in patterns:
            try:
                re.compile(pattern)
            except re.error as exc:
                errors.append(f"{path.relative_to(ROOT)}:{line}: invalid regex: {exc}")
    if errors:
        print("CHECKER_REGEX_FAILED")
        for error in errors:
            print(" - " + error)
        return 1
    print(f"CHECKER_REGEX_PASSED ({len(CHECKERS)} checkers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
