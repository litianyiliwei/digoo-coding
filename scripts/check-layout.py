#!/usr/bin/env python3
"""Enforce toolkit/project layout ownership.

Toolkit mode: the repository contains toolkit content only (no project outputs,
no state, no OpenSpec artifacts).
Project mode: the repository contains vendored toolkit paths recorded in
toolkit-lock.json plus project-owned paths; toolkit files may not live under
project output directories, and composed files must carry paired managed
blocks.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TOOLKIT_ROOT_ENTRIES = {
    ".claude", ".github", "prompts", "templates", "scripts", "process",
    ".gitignore", ".gitattributes", "README.md", "README-zh.md", "LICENSE",
    "AGENTS.md", "AGENTS-zh.md", "VERSION", ".superpowers", "_trash", ".git",
}
TOOLKIT_CLAUDE_CHILDREN = {"skills", "hooks", "settings.json", "settings.local.json"}

PROJECT_ROOT_BUILTINS = {
    "README.md", "README-zh.md", "LICENSE", ".gitattributes", ".gitignore",
    "AGENTS.md", "AGENTS-zh.md", "toolkit-lock.json", "project-extensions.json",
    "workflow-state.json", ".toolkit-upgrade.lock", ".env.example", "Makefile", "Dockerfile",
    "docker-compose.yml", "compose.yml", "compose.yaml",
    "package.json", "package-lock.json", "pnpm-lock.yaml", "yarn.lock",
    "pyproject.toml", "requirements.txt", "Pipfile", "Pipfile.lock", "poetry.lock",
    "go.mod", "go.sum", "Cargo.toml", "Cargo.lock", "Gemfile", "Gemfile.lock",
    ".github", "docs", "openspec", "workflow", "design", "src", "tests",
    ".superpowers", "_trash", ".git",
}
PROJECT_DOCS_CHILDREN = {"product", "architecture", "adr", "project"}
PROJECT_OPENSPEC_CHILDREN = {"config.yaml", "changes", "specs"}
MANAGED_FILES = ("AGENTS.md", "AGENTS-zh.md", "openspec/config.yaml", ".gitignore")
FORBIDDEN_FOR_VENDOR = ("docs/", "openspec/changes/", "openspec/specs/", "design/", "workflow/")


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def git_tracked_paths() -> set[str] | None:
    """Tracked paths relative to ROOT, or None outside a readable Git work tree."""
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "ls-files", "-z"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    return {path for path in result.stdout.split("\0") if path}


def git_ignored(relpath: str) -> bool:
    try:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "check-ignore", "-q", "--", relpath],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
    except OSError:
        return False
    return result.returncode == 0


def in_repository(relpath: str, tracked: set[str] | None) -> bool:
    """Whether a layout entry belongs to the repository.

    Untracked paths that Git ignores (node_modules, .venv, dist) are local
    artifacts, not repository content. Outside Git, keep scanning everything.
    """
    if tracked is None:
        return True
    prefix = relpath.rstrip("/") + "/"
    if relpath in tracked or any(path.startswith(prefix) for path in tracked):
        return True
    return not git_ignored(relpath)


def declared_docs_children(paths: set[str]) -> set[str]:
    children = set()
    for declared in paths:
        parts = [part for part in declared.replace("\\", "/").split("/") if part]
        if len(parts) >= 2 and parts[0] == "docs":
            children.add(parts[1])
    return children


def extensions() -> dict:
    data = load_json(ROOT / "project-extensions.json") or {}
    return {"root": set(data.get("root") or []), "paths": set(data.get("paths") or [])}


def check_toolkit_mode() -> list[str]:
    errors: list[str] = []
    for entry in sorted(ROOT.iterdir()):
        if entry.name not in TOOLKIT_ROOT_ENTRIES:
            errors.append(f"root entry not allowed in toolkit mode: {entry.name}")
    claude = ROOT / ".claude"
    if claude.is_dir():
        for child in sorted(claude.iterdir()):
            if child.name not in TOOLKIT_CLAUDE_CHILDREN:
                errors.append(f".claude entry not allowed in toolkit mode: {child.name}")
        skills = claude / "skills"
        if skills.is_dir():
            for skill in sorted(skills.iterdir()):
                if skill.name.startswith("openspec-"):
                    errors.append(f"third-party Skill belongs to projects, not the toolkit: .claude/skills/{skill.name}")
    for forbidden in ("docs", "openspec", "workflow", "design", "src", "tests", "workflow-state.json"):
        if (ROOT / forbidden).exists() and forbidden not in TOOLKIT_ROOT_ENTRIES:
            errors.append(f"project-only path present in toolkit repository: {forbidden}")
    return errors


def check_project_mode() -> list[str]:
    errors: list[str] = []
    lock_path = ROOT / "toolkit-lock.json"
    if not lock_path.is_file():
        return ["missing toolkit-lock.json (project repositories must be installed by toolkit-sync)"]
    lock = load_json(lock_path)
    if not isinstance(lock, dict) or not isinstance(lock.get("files"), dict):
        return ["toolkit-lock.json is unreadable or has no files map"]
    vendored = set()
    for relpath in lock["files"]:
        vendored.add(relpath.split("/", 1)[0])
        if any(relpath.startswith(prefix) for prefix in FORBIDDEN_FOR_VENDOR):
            errors.append(f"vendored path placed under a project output directory: {relpath}")
    ext = extensions()
    tracked = git_tracked_paths()
    for entry in sorted(ROOT.iterdir()):
        name = entry.name
        if not in_repository(name, tracked):
            continue
        if name in vendored or name in PROJECT_ROOT_BUILTINS or name in ext["root"]:
            continue
        errors.append(
            f"root entry is not vendored, built-in project-root, or declared: {name} "
            f'(declare it in project-extensions.json: {{"root": ["{name}"]}})'
        )
    docs = ROOT / "docs"
    if docs.is_dir():
        allowed_docs = PROJECT_DOCS_CHILDREN | declared_docs_children(ext["paths"])
        for child in sorted(docs.iterdir()):
            relpath = f"docs/{child.name}"
            if not in_repository(relpath, tracked):
                continue
            if child.name not in allowed_docs:
                errors.append(
                    f"docs child not allowed in project mode: {relpath} "
                    f'(declare it in project-extensions.json: {{"paths": ["{relpath}"]}})'
                )
    openspec = ROOT / "openspec"
    if openspec.is_dir():
        for child in sorted(openspec.iterdir()):
            if child.name not in PROJECT_OPENSPEC_CHILDREN:
                errors.append(f"openspec child not allowed in project mode: openspec/{child.name}")
    for managed in MANAGED_FILES:
        path = ROOT / managed
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if text.count("toolkit:begin") != 1 or text.count("toolkit:end") != 1:
            errors.append(f"managed block markers are missing or unpaired: {managed}")
    return errors


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["toolkit", "project", "auto"], default="auto")
    args = parser.parse_args(argv)
    mode = args.mode
    if mode == "auto":
        mode = "project" if (ROOT / "toolkit-lock.json").is_file() else "toolkit"
    errors = check_project_mode() if mode == "project" else check_toolkit_mode()
    if errors:
        print("LAYOUT_FAILED")
        for error in errors:
            print(" - " + error)
        return 1
    print(f"LAYOUT_OK ({mode})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
