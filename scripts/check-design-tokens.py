#!/usr/bin/env python3
"""Static, exact comparison between Figma tokens and the project token layer.

No browser and no screenshots: compare the actual values read from Figma
(`## 设计令牌（实际值）` in figma-audit.md) with CSS custom properties in the
project's global token file(s). This is the deterministic half of visual
regression; runtime geometry is covered by check-figma-layout.py.
"""
import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CSS_VAR_RE = re.compile(r"--([A-Za-z0-9_-]+)\s*:\s*([^;]+);")
TOKEN_SECTION = "## 设计令牌（实际值）"


def section(text, title):
    start = text.find(title)
    if start < 0:
        return ""
    end = text.find("\n## ", start + len(title))
    return text[start:end if end >= 0 else len(text)]


def table_rows(section_text):
    rows = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        if re.match(r"^\|[\s:|-]+\|$", stripped):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if cells and cells[0] in ("变量",):
            continue
        rows.append(cells)
    return rows


def parse_css(paths):
    values = {}
    for path in paths:
        if not path.is_file():
            continue
        for name, value in CSS_VAR_RE.findall(path.read_text(encoding="utf-8")):
            values[f"--{name}"] = value.strip()
    return values


def resolve(value, values, depth=0):
    if depth > 6:
        return value
    match = re.fullmatch(r"var\(\s*(--[A-Za-z0-9_-]+)\s*(?:,\s*(.*))?\)", value.strip())
    if not match:
        return value
    name, fallback = match.group(1), match.group(2)
    if name in values:
        return resolve(values[name], values, depth + 1)
    return fallback.strip() if fallback else value


def norm_value(value, kind):
    text = value.strip().strip("`").strip('"').strip("'").strip()
    text = re.sub(r"\s+", "", text.lower())
    if kind == "COLOR":
        return text
    if kind == "NUMBER":
        if re.fullmatch(r"[0-9.]+", text):
            return text + "px"
        return text
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--change", required=True)
    parser.add_argument("--tokens", action="append", required=True,
                        help="Global token CSS file; repeatable")
    args = parser.parse_args()

    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", args.change):
        print("Invalid change-id; use lowercase kebab-case.", file=sys.stderr)
        sys.exit(2)
    base = ROOT / "openspec/changes" / args.change / "design"
    audit = base / "figma-audit.md"
    if not audit.is_file():
        print(f"BLOCKED: missing {audit.relative_to(ROOT)}", file=sys.stderr)
        sys.exit(2)
    token_paths = [Path(p) if Path(p).is_absolute() else ROOT / p for p in args.tokens]
    missing_files = [str(p) for p in token_paths if not p.is_file()]
    if missing_files:
        print(f"BLOCKED: token file(s) not found: {', '.join(missing_files)}", file=sys.stderr)
        sys.exit(2)

    text = audit.read_text(encoding="utf-8")
    rows = table_rows(section(text, TOKEN_SECTION))
    if not rows:
        print(f"BLOCKED: {TOKEN_SECTION} has no token rows", file=sys.stderr)
        sys.exit(2)

    values = parse_css(token_paths)
    errors = []
    checked = 0
    for cells in rows:
        if len(cells) < 4:
            errors.append(f"token row is incomplete: {cells}")
            continue
        name, kind, actual, mapping = cells[0], cells[1].upper(), cells[2], cells[3]
        var_names = re.findall(r"--[A-Za-z0-9_-]+", mapping)
        if not var_names:
            errors.append(f"{name}: no CSS variable mapping in {mapping!r}")
            continue
        for var in var_names:
            if var not in values:
                errors.append(f"{name}: CSS variable {var} is not defined in the token file(s)")
                continue
            if kind not in ("COLOR", "NUMBER"):
                continue
            resolved = resolve(values[var], values)
            expected = norm_value(actual, kind)
            got = norm_value(resolved, kind)
            checked += 1
            if expected != got:
                errors.append(
                    f"{name}: expected {expected!r} from Figma, but {var} is {got!r}"
                )

    if errors:
        for err in errors:
            print("ERROR:", err)
        print(f"Design token check failed: {len(errors)} issue(s).")
        sys.exit(1)
    print(f"Design token check passed: {checked} token(s) exactly match the token layer.")


if __name__ == "__main__":
    main()
