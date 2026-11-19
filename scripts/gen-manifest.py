#!/usr/bin/env python3
"""Generate and verify process/TOOLKIT-MANIFEST.json (the vendored-set registry).

Manifest shape:
  {"version", "state_schema", "files": [{"path", "install", "sha256", "class", "vendor"}], "exclude"}
Text files are hashed after universal-newline normalization (LF); binary files
are hashed as raw bytes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_SCHEMA = "1.0"


def manifest_path() -> Path:
    return ROOT / "process" / "TOOLKIT-MANIFEST.json"


def lock_path() -> Path:
    return ROOT / "toolkit-lock.json"


def version_path() -> Path:
    return ROOT / "VERSION"

TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".txt", ".sh", ".py", ".csv"}
VENDOR_DIRS = [".claude/skills", ".claude/hooks", "prompts", "templates", "scripts", "process"]
EXTRA_VENDOR_FILES = [".claude/settings.json"]
SKIP_DIR_NAMES = {"__pycache__", ".superpowers", ".git"}
SKIP_PREFIXES = ("process/proposals/", "process/examples/")
SKIP_FILES = {"process/TOOLKIT-MANIFEST.json"}
INSTALL_OVERRIDES = {"templates/project-setup/toolkit-ci.yml": ".github/workflows/toolkit-ci.yml"}
PROJECT_OUTPUT_DIRS = ("docs", "openspec", "design", "workflow")
EXCLUDE = [
    "README.md", "README-zh.md", "LICENSE", ".gitattributes", "VERSION",
    ".github/workflows/ci.yml", "AGENTS.md", "AGENTS-zh.md",
    "toolkit-lock.json", "workflow-state.json",
    "process/proposals/", "process/examples/", "process/TOOLKIT-MANIFEST.json",
]


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def content_bytes(path: Path) -> bytes:
    if path.suffix.lower() in TEXT_SUFFIXES:
        return path.read_text(encoding="utf-8").encode("utf-8")
    return path.read_bytes()


def sha256(path: Path) -> str:
    return hashlib.sha256(content_bytes(path)).hexdigest()


def class_for(relpath: str) -> str:
    if Path(relpath).name.startswith("STAGE-IO-OVERVIEW"):
        return "generated"
    return "toolkit"


def collect() -> list[dict]:
    files: dict[str, dict] = {}
    for rel_dir in VENDOR_DIRS:
        base = ROOT / rel_dir
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            if any(part in SKIP_DIR_NAMES for part in path.parts):
                continue
            relpath = rel(path)
            if relpath.startswith(SKIP_PREFIXES) or relpath in SKIP_FILES:
                continue
            files[relpath] = {
                "path": relpath,
                "install": INSTALL_OVERRIDES.get(relpath, relpath),
                "sha256": sha256(path),
                "class": class_for(relpath),
                "vendor": True,
            }
    for relpath in EXTRA_VENDOR_FILES:
        path = ROOT / relpath
        if path.is_file():
            files[relpath] = {
                "path": relpath,
                "install": INSTALL_OVERRIDES.get(relpath, relpath),
                "sha256": sha256(path),
                "class": "toolkit",
                "vendor": True,
            }
    return [files[key] for key in sorted(files)]


def build() -> dict:
    version = version_path().read_text(encoding="utf-8").strip() if version_path().is_file() else ""
    return {"version": version, "state_schema": STATE_SCHEMA, "migrations": [],
            "files": collect(), "exclude": EXCLUDE}


def rendered(doc: dict) -> str:
    return json.dumps(doc, ensure_ascii=False, indent=2) + "\n"


def source_mode_guard() -> str:
    for rel_dir in PROJECT_OUTPUT_DIRS:
        if (ROOT / rel_dir).exists():
            return f"project output directory present: {rel_dir}/"
    if (ROOT / "workflow-state.json").exists():
        return "workflow-state.json present"
    return ""


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if lock_path().is_file():
        print("TOOLKIT_PROJECT_MODE=skip (toolkit-lock.json present; the manifest is generated in the toolkit source repository only)")
        return 0
    reason = source_mode_guard()
    if reason:
        print(f"ERROR: gen-manifest runs in the toolkit source repository only ({reason})",
              file=sys.stderr)
        return 2
    doc = build()
    text = rendered(doc)
    if args.write:
        target = manifest_path()
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
        print(f"Wrote {target.relative_to(ROOT)} ({len(doc['files'])} vendored file(s))")
        return 0
    if args.check:
        target = manifest_path()
        if not target.is_file():
            print("ERROR: missing manifest; run gen-manifest.py --write", file=sys.stderr)
            return 1
        current = target.read_text(encoding="utf-8")
        if current != text:
            detail = "content differs"
            try:
                old = json.loads(current)
                old_files = {f["path"]: f["sha256"] for f in old.get("files", [])}
                new_files = {f["path"]: f["sha256"] for f in doc["files"]}
                changed = sorted(set(old_files) ^ set(new_files))
                changed += sorted(p for p in set(old_files) & set(new_files) if old_files[p] != new_files[p])
                detail = ", ".join(changed[:10]) or "header fields"
            except Exception:
                pass
            print(f"ERROR: manifest is stale ({detail}); run gen-manifest.py --write", file=sys.stderr)
            return 1
        print(f"Toolkit manifest is current ({len(doc['files'])} vendored file(s))")
        return 0
    parser.print_usage(sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
