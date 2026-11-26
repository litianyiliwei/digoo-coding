#!/usr/bin/env python3
"""Install, verify and upgrade a vendored toolkit inside a business project repository.

Commands:
  init    -- install a toolkit release into a project repository (first time only)
  verify  -- check vendored hashes, managed blocks and third-party presence

Text files (md/json/yaml/yml/txt/sh/py/csv) are hashed after newline
normalization (LF); binary files are hashed as raw bytes.
"""
from __future__ import annotations

import argparse
import json
import os
import shlex
import shutil
import subprocess
import sys
import tempfile
import types
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_REL = "process/TOOLKIT-MANIFEST.json"
LOCK_NAME = "toolkit-lock.json"
UPGRADE_LOCK = ".toolkit-upgrade.lock"
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".txt", ".sh", ".py", ".csv"}

MARK_HTML = ("<!-- toolkit:begin -->", "<!-- toolkit:end -->")
MARK_HASH = ("# toolkit:begin", "# toolkit:end")

AGENTS_TEMPLATES = {
    "AGENTS.md": ("templates/workflow/agents-managed.md", MARK_HTML),
    "AGENTS-zh.md": ("templates/workflow/agents-managed-zh.md", MARK_HTML),
}
GITIGNORE_TEMPLATE = "templates/project-setup/gitignore-block.txt"
OPENSPEC_TEMPLATE = "templates/project-setup/openspec-config.yaml"
STATE_TEMPLATE = "templates/workflow/workflow-state.default.json"


def sha_bytes(data: bytes, suffix: str = "") -> str:
    if suffix.lower() in TEXT_SUFFIXES:
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    return sha_bytes(path.read_bytes(), path.suffix)


class Source:
    """A readable toolkit release (local directory or temporary git clone)."""

    def __init__(self, base: Path, origin: str = ""):
        self.base = Path(base).resolve()
        self.origin = origin or f"local:{self.base}"

    def read(self, rel: str) -> bytes:
        return (self.base / rel).read_bytes()

    def manifest(self) -> dict:
        return json.loads((self.base / MANIFEST_REL).read_text(encoding="utf-8"))

    def files(self) -> list[str]:
        return [entry["path"] for entry in self.manifest().get("files", [])]

    def git_commit(self) -> str:
        try:
            return subprocess.check_output(
                ["git", "-C", str(self.base), "rev-parse", "HEAD"], text=True
            ).strip()
        except Exception:
            return ""


class GitRefSource:
    """Reads a local git repository at a specific ref (worktree untouched)."""

    def __init__(self, base: Path, ref: str):
        self.base = Path(base).resolve()
        self.ref = ref
        self.origin = f"local:{self.base}"

    def read(self, rel: str) -> bytes:
        return subprocess.check_output(
            ["git", "-C", str(self.base), "show", f"{self.ref}:{rel}"]
        )

    def manifest(self) -> dict:
        return json.loads(self.read(MANIFEST_REL).decode("utf-8"))

    def files(self) -> list[str]:
        return [entry["path"] for entry in self.manifest().get("files", [])]

    def git_commit(self) -> str:
        return subprocess.check_output(
            ["git", "-C", str(self.base), "rev-parse", self.ref], text=True
        ).strip()


def open_source(source: str, ref: str | None, workdir: Path | None = None) -> Source:
    path = Path(source)
    if path.is_dir():
        if ref:
            try:
                subprocess.run(["git", "-C", str(path), "rev-parse", "--is-inside-work-tree"],
                               check=True, capture_output=True)
            except Exception:
                raise ValueError(f"ref {ref!r} requires a git repository: {path}")
            return GitRefSource(path, ref)
        return Source(path, f"local:{path.resolve()}")
    workdir = workdir or Path(tempfile.mkdtemp(prefix="toolkit-sync-"))
    target = workdir / "toolkit"
    if target.exists():
        shutil.rmtree(target)
    subprocess.run(["git", "clone", "--quiet", source, str(target)], check=True)
    if ref:
        subprocess.run(["git", "-C", str(target), "checkout", "--quiet", ref], check=True)
    return Source(target, source)


def resolve_source(project_root, source: str = "", ref: str = "") -> Source:
    if source:
        return open_source(source, ref)
    lock = load_lock(Path(project_root))
    origin = lock.get("source", "")
    if origin.startswith("local:"):
        origin = origin[len("local:"):]
    if not origin:
        raise ValueError("no toolkit source recorded in toolkit-lock.json; pass --from")
    return open_source(origin, ref)


def origin_arg(origin: str) -> str:
    return origin[len("local:"):] if origin.startswith("local:") else origin


def wrap_block(body: str, markers: tuple[str, str]) -> str:
    begin, end = markers
    return f"{begin}\n{body.rstrip()}\n{end}\n"


def find_block_span(text: str, markers: tuple[str, str]) -> tuple[int, int] | None:
    begin, end = markers
    start = text.find(begin)
    if start < 0:
        return None
    stop = text.find(end, start + len(begin))
    if stop < 0:
        return None
    return start, stop + len(end)


def replace_block(text: str, body: str, markers: tuple[str, str]) -> str:
    span = find_block_span(text, markers)
    if span is None:
        raise ValueError("managed block markers are missing or unpaired")
    start, stop = span
    tail = text[stop:]
    if tail.startswith("\n"):
        tail = tail[1:]
    return text[:start] + wrap_block(body, markers) + tail


def compose_agents(root: Path, blocks: dict[str, str]) -> list[str]:
    changed = []
    for name, markers in ((n, m[1]) for n, m in AGENTS_TEMPLATES.items()):
        path = root / name
        body = blocks.get(name, "")
        wrapped = wrap_block(body, markers)
        if not path.is_file():
            path.write_text(wrapped, encoding="utf-8")
            changed.append(name)
            continue
        text = path.read_text(encoding="utf-8")
        if find_block_span(text, markers) is not None:
            new = replace_block(text, body, markers)
        else:
            new = wrapped + "\n" + text
        if new != text:
            path.write_text(new, encoding="utf-8")
            changed.append(name)
    return changed


def compose_openspec_config(root: Path, template: str) -> str | None:
    path = root / "openspec" / "config.yaml"
    span = find_block_span(template, MARK_HASH)
    if span is None:
        raise ValueError("openspec template is missing toolkit markers")
    start, stop = span
    toolkit_block = template[start:stop]
    if not path.is_file():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(template, encoding="utf-8")
        return "openspec/config.yaml"
    text = path.read_text(encoding="utf-8")
    if find_block_span(text, MARK_HASH) is not None:
        new = replace_block(text, template[start + len(MARK_HASH[0]) + 1:stop - len(MARK_HASH[1]) - 1], MARK_HASH)
    else:
        idx = text.find("context:")
        context = text[idx:] if idx >= 0 else "context: |\n  PENDING — written by the project at Stage 01.\n"
        new = toolkit_block + "\n" + context
    if new != text:
        path.write_text(new, encoding="utf-8")
        return "openspec/config.yaml"
    return None


def compose_gitignore(root: Path, block: str) -> str | None:
    path = root / ".gitignore"
    span = find_block_span(block, MARK_HASH)
    if span is None:
        raise ValueError("gitignore block is missing toolkit markers")
    start, stop = span
    block_text = block[start:stop]
    if not path.is_file():
        path.write_text(block_text + "\n", encoding="utf-8")
        return ".gitignore"
    text = path.read_text(encoding="utf-8")
    if find_block_span(text, MARK_HASH) is not None:
        new = replace_block(text, block[start + len(MARK_HASH[0]) + 1:stop - len(MARK_HASH[1]) - 1], MARK_HASH)
    else:
        new = block_text + "\n\n" + text
    if new != text:
        path.write_text(new, encoding="utf-8")
        return ".gitignore"
    return None


def scan_third_party(project: Path) -> dict:
    generated = []
    skills = project / ".claude" / "skills"
    if skills.is_dir():
        for entry in sorted(skills.glob("openspec-*")):
            generated.append(f".claude/skills/{entry.name}")
    commands = project / ".claude" / "commands"
    if commands.is_dir():
        for entry in sorted(commands.rglob("*.md")):
            generated.append(entry.relative_to(project).as_posix())
    cli = None
    executable = shutil.which("openspec")
    if executable:
        try:
            result = subprocess.run([executable, "version"], capture_output=True, text=True, timeout=10)
            cli = (result.stdout or result.stderr).strip()[:200] or None
        except Exception:
            cli = None
    return {"openspec_cli": cli, "generated_paths": generated}


def write_lock(project: Path, source: Source, manifest: dict, ref: str, commit: str,
               files: dict[str, str]) -> Path:
    data = {
        "version": manifest.get("version", ""),
        "source": source.origin,
        "ref": ref or "",
        "commit": commit or source.git_commit(),
        "installed_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "state_schema": manifest.get("state_schema", ""),
        "manifest_sha256": sha_bytes((source.base / MANIFEST_REL).read_bytes(), ".json"),
        "files": files,
        "third_party": scan_third_party(project),
        "forks": [],
        "upgrades": [],
    }
    path = project / LOCK_NAME
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def install_files(project: Path, source: Source, manifest: dict) -> dict[str, str]:
    files: dict[str, str] = {}
    for entry in manifest.get("files", []):
        if not entry.get("vendor", True):
            continue
        install = entry.get("install", entry["path"])
        target = project / install
        target.parent.mkdir(parents=True, exist_ok=True)
        data = source.read(entry["path"])
        target.write_bytes(data)
        files[install] = sha_bytes(data, Path(entry["path"]).suffix)
    return files


def validate_source_manifest(source, manifest: dict) -> None:
    for entry in manifest.get("files", []):
        if not entry.get("vendor", True):
            continue
        expected = entry.get("sha256")
        if not expected:
            continue
        actual = sha_bytes(source.read(entry["path"]), Path(entry["path"]).suffix)
        if actual != expected:
            raise ValueError(f"source manifest mismatch: {entry['path']}")


def init(project_root, source: Source, ref: str, commit: str) -> Path:
    project = Path(project_root)
    if (project / LOCK_NAME).exists():
        raise ValueError(f"project already installed ({LOCK_NAME} exists); use apply to upgrade")
    manifest = source.manifest()
    validate_source_manifest(source, manifest)
    files = install_files(project, source, manifest)
    blocks = {}
    for name, (template, _markers) in AGENTS_TEMPLATES.items():
        if (source.base / template).is_file():
            blocks[name] = source.read(template).decode("utf-8")
    compose_agents(project, blocks)
    if (source.base / OPENSPEC_TEMPLATE).is_file():
        compose_openspec_config(project, source.read(OPENSPEC_TEMPLATE).decode("utf-8"))
    if (source.base / GITIGNORE_TEMPLATE).is_file():
        compose_gitignore(project, source.read(GITIGNORE_TEMPLATE).decode("utf-8"))
    state = project / "workflow-state.json"
    if not state.exists() and (source.base / STATE_TEMPLATE).is_file():
        state.write_bytes(source.read(STATE_TEMPLATE))
    return write_lock(project, source, manifest, ref, commit, files)


def verify(project_root, require_lock: bool = False) -> list[str]:
    project = Path(project_root)
    errors: list[str] = []
    lock = project / LOCK_NAME
    if not lock.is_file():
        return ["missing toolkit-lock.json"] if require_lock else errors
    try:
        data = json.loads(lock.read_text(encoding="utf-8"))
    except Exception:
        return ["toolkit-lock.json is unreadable"]
    if not data.get("version"):
        errors.append("toolkit-lock.json has no version")
    for relpath, expected in (data.get("files") or {}).items():
        path = project / relpath
        if not path.is_file():
            errors.append(f"vendored file missing: {relpath}")
            continue
        if sha_file(path) != expected:
            errors.append(f"vendored file modified: {relpath}")
    managed = [
        ("AGENTS.md", MARK_HTML),
        ("AGENTS-zh.md", MARK_HTML),
        ("openspec/config.yaml", MARK_HASH),
        (".gitignore", MARK_HASH),
    ]
    for name, markers in managed:
        path = project / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        begin, end = markers
        if text.count(begin) != 1 or text.count(end) != 1:
            errors.append(f"managed block markers missing or unpaired: {name}")
    for relpath in (data.get("third_party") or {}).get("generated_paths") or []:
        if not (project / relpath).exists():
            errors.append(f"third-party generated path missing: {relpath}")
    vendored = set(data.get("files") or {})
    third = set((data.get("third_party") or {}).get("generated_paths") or [])
    for root in ("prompts", "templates", "scripts", "process", ".claude"):
        base = project / root
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            relpath = path.relative_to(project).as_posix()
            if relpath in vendored or relpath in third:
                continue
            if "__pycache__" in path.parts or path.suffix == ".pyc":
                continue
            if relpath in {".claude/settings.local.json",
                           "process/STAGE-IO-OVERVIEW.md",
                           "process/STAGE-IO-OVERVIEW-zh.md"}:
                continue
            errors.append(f"unexpected file in vendored tree: {relpath}")
    return errors


def load_lock(project: Path) -> dict:
    path = project / LOCK_NAME
    if not path.is_file():
        raise ValueError("project is not installed (missing toolkit-lock.json)")
    return json.loads(path.read_text(encoding="utf-8"))


def working_tree_dirty(project: Path) -> bool:
    if not (project / ".git").exists():
        return False
    result = subprocess.run(
        ["git", "-C", str(project), "status", "--porcelain", "--untracked-files=no"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return False
    return any(line.strip() for line in result.stdout.splitlines())


def state_has_reviews(state: dict) -> bool:
    """True when a v1 or v2 state has pending reviews or blockers."""
    if str(state.get("state_schema_version")) == "2.0" and isinstance(state.get("project"), dict) and isinstance(state.get("changes"), dict):
        project = state.get("project") or {}
        if project.get("pending_approvals") or project.get("blocked_items"):
            return True
        for lane in (state.get("changes") or {}).values():
            if isinstance(lane, dict) and (lane.get("pending_approvals") or lane.get("blocked_items")):
                return True
        return False
    return bool(state.get("pending_approvals") or state.get("blocked_items"))


def pending_review(project: Path) -> bool:
    state_path = project / "workflow-state.json"
    if not state_path.is_file():
        return False
    try:
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except Exception:
        return False
    return state_has_reviews(state)


def backup_state(project: Path) -> Path | None:
    state = project / "workflow-state.json"
    if not state.is_file():
        return None
    directory = project / "workflow" / "state-backups"
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    path.write_bytes(state.read_bytes())
    return path


def target_entries(manifest: dict) -> dict[str, dict]:
    return {entry.get("install", entry["path"]): entry
            for entry in manifest.get("files", []) if entry.get("vendor", True)}


def plan(project_root, target: Source) -> dict:
    project = Path(project_root)
    lock = load_lock(project)
    manifest = target.manifest()
    old_files = lock.get("files") or {}
    new_entries = target_entries(manifest)
    added = sorted(set(new_entries) - set(old_files))
    removed = sorted(set(old_files) - set(new_entries))
    changed = []
    for install, entry in sorted(new_entries.items()):
        if install not in old_files:
            continue
        target_sha = sha_bytes(target.read(entry["path"]), Path(entry["path"]).suffix)
        if target_sha != old_files[install]:
            changed.append(install)
    conflicts = sorted(p for p, expected in old_files.items()
                       if (project / p).is_file() and sha_file(project / p) != expected)
    migrations = list(manifest.get("migrations") or [])
    if lock.get("state_schema") != manifest.get("state_schema"):
        migrations.append("workflow.py migrate-state (state schema changed)")
    return {
        "from_version": lock.get("version", ""),
        "to_version": manifest.get("version", ""),
        "added": added,
        "changed": changed,
        "removed": removed,
        "conflicts": conflicts,
        "migrations": migrations,
        "block_files": [name for name, (template, _m) in AGENTS_TEMPLATES.items()
                        if (target.base / template).is_file()],
    }


def regenerate(project: Path) -> list[str]:
    failures: list[str] = []
    report = project / "scripts" / "stage-io-report.py"
    if report.is_file():
        result = subprocess.run([sys.executable, str(report), "--out", "process/STAGE-IO-OVERVIEW.md"],
                                cwd=project, capture_output=True, text=True)
        if result.returncode:
            failures.append("stage-io-report: " + (result.stdout + result.stderr).strip()[-300:])
    if ((project / "docs/architecture/baseline-manifest.json").is_file()
            and (project / "scripts/workflow.py").is_file()):
        result = subprocess.run([sys.executable, str(project / "scripts/workflow.py"), "sync-baseline-index"],
                                cwd=project, capture_output=True, text=True)
        if result.returncode:
            failures.append("baseline-index: " + (result.stdout + result.stderr).strip()[-300:])
    return failures


def run_checks(project: Path) -> list[str]:
    failures = []
    layout = project / "scripts" / "check-layout.py"
    if layout.is_file():
        result = subprocess.run([sys.executable, str(layout), "--mode", "project"],
                                cwd=project, capture_output=True, text=True)
        if result.returncode:
            failures.append("check-layout: " + (result.stdout + result.stderr).strip()[-400:])
    ci = project / "scripts" / "ci-check.sh"
    bash = shutil.which("bash")
    if ci.is_file() and bash:
        result = subprocess.run([bash, str(ci)], cwd=project, capture_output=True, text=True)
        if result.returncode:
            failures.append("ci-check: " + (result.stdout + result.stderr).strip()[-400:])
    return failures


def preflight_layout_errors(source: Source, project: Path) -> list[str] | None:
    """Run the target release's project layout rules before the project is touched."""
    rel = "scripts/check-layout.py"
    try:
        code = source.read(rel)
    except Exception:
        return None
    module = types.ModuleType("toolkit_preflight_layout")
    module.__file__ = str(project / rel)
    try:
        exec(compile(code, rel, "exec"), module.__dict__)
    except SystemExit as exc:
        if exc.code in (0, None):
            return None
        return [f"preflight checker exited with code {exc.code}"]
    except Exception as exc:
        return [f"preflight could not load {rel}: {exc}"]
    checker = getattr(module, "check_project_mode", None)
    if not callable(checker):
        return None
    module.ROOT = project
    try:
        return list(checker())
    except Exception as exc:
        return [f"preflight failed: {exc}"]


def apply(project_root, target: Source, ref: str = "", *, take_upstream: bool = False,
          keep_local: bool = False, run_migrations: bool = False) -> int:
    project = Path(project_root)
    lock = load_lock(project)
    state_path = project / "workflow-state.json"
    if state_path.is_file():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except Exception:
            print("SYNC_APPLY_ABORTED workflow-state.json is unreadable; run toolkit-sync.py repair first")
            return 2
        if state_has_reviews(state):
            print("SYNC_APPLY_ABORTED pending_approvals or blocked_items exist; resolve the review before upgrading")
            return 2
    if working_tree_dirty(project):
        print("SYNC_APPLY_ABORTED working tree is not clean; commit or stash before upgrading")
        return 2
    manifest = target.manifest()
    validate_source_manifest(target, manifest)
    preflight = preflight_layout_errors(target, project)
    if preflight:
        print("SYNC_APPLY_ABORTED layout check failed before upgrading; "
              "declare project-owned paths in project-extensions.json and rerun")
        for line in preflight:
            print(" - " + line)
        return 2
    new_entries = target_entries(manifest)
    old_files = lock.get("files") or {}
    conflicts = sorted(p for p, expected in old_files.items()
                       if (project / p).is_file() and sha_file(project / p) != expected)
    added_existing = []
    for install, entry in sorted(new_entries.items()):
        if install in old_files:
            continue
        path = project / install
        if path.is_file() and sha_file(path) != sha_bytes(target.read(entry["path"]),
                                                         Path(entry["path"]).suffix):
            added_existing.append(install)
    if (conflicts or added_existing) and not (take_upstream or keep_local):
        print("SYNC_APPLY_ABORTED locally modified vendored files:")
        for path in sorted(conflicts + added_existing):
            print(" - " + path)
        print("rerun with --take-upstream to replace them or --keep-local to record forks")
        return 2
    migration_commands = [item.get("command") for item in (manifest.get("migrations") or [])
                          if isinstance(item, dict) and item.get("command")]
    if lock.get("state_schema") != manifest.get("state_schema") and not migration_commands:
        migration_commands = ["python scripts/workflow.py migrate-state --reason toolkit-upgrade"]
    if migration_commands and not run_migrations:
        print("SYNC_APPLY_ABORTED state migrations required: " + "; ".join(migration_commands))
        return 2
    lock_fd = None
    try:
        lock_fd = os.open(project / UPGRADE_LOCK, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise ValueError(f"another upgrade is running ({UPGRADE_LOCK} exists)")
    try:
        old_lock_bytes = (project / LOCK_NAME).read_bytes()
        backup_state(project)
        forks = []
        files: dict[str, str] = {}
        for install, entry in sorted(new_entries.items()):
            if install in conflicts and keep_local:
                files[install] = sha_file(project / install)
                forks.append(install)
                continue
            data = target.read(entry["path"])
            destination = project / install
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
            files[install] = sha_bytes(data, Path(entry["path"]).suffix)
        for install in sorted(set(old_files) - set(new_entries)):
            path = project / install
            if not path.is_file():
                continue
            if keep_local and install in conflicts:
                forks.append(install)
                continue
            path.unlink()
        blocks = {}
        for name, (template, _markers) in AGENTS_TEMPLATES.items():
            if (target.base / template).is_file():
                blocks[name] = target.read(template).decode("utf-8")
        compose_agents(project, blocks)
        if (target.base / OPENSPEC_TEMPLATE).is_file():
            compose_openspec_config(project, target.read(OPENSPEC_TEMPLATE).decode("utf-8"))
        if (target.base / GITIGNORE_TEMPLATE).is_file():
            compose_gitignore(project, target.read(GITIGNORE_TEMPLATE).decode("utf-8"))
        migration_errors = []
        for command in migration_commands:
            result = subprocess.run(shlex.split(command), cwd=project, capture_output=True, text=True)
            if result.returncode:
                migration_errors.append(
                    f"migration failed: {command}: " + (result.stdout + result.stderr).strip()[-300:]
                )
        if migration_errors:
            (project / LOCK_NAME).write_bytes(old_lock_bytes)
            print("SYNC_APPLY_FAILED")
            for failure in migration_errors:
                print(" - " + failure)
            print("run toolkit-sync.py repair (restores vendored files from the locked ref) or revert the working tree")
            return 3
        upgrades = list(lock.get("upgrades") or [])
        upgrades.append({"at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                         "from_version": lock.get("version", ""),
                         "to_version": manifest.get("version", ""), "ref": ref or ""})
        write_lock(project, target, manifest, ref, target.git_commit(), files)
        lock_data = json.loads((project / LOCK_NAME).read_text(encoding="utf-8"))
        stale_forks = {path for path in (lock.get("forks") or [])
                       if (project / path).is_file() and sha_file(project / path) != files.get(path)}
        lock_data["forks"] = sorted(set(forks) | stale_forks)
        lock_data["upgrades"] = upgrades
        (project / LOCK_NAME).write_text(
            json.dumps(lock_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        failures = regenerate(project) + run_checks(project)
        if failures:
            (project / LOCK_NAME).write_bytes(old_lock_bytes)
            print("SYNC_APPLY_FAILED")
            for failure in failures:
                print(" - " + failure)
            print("run toolkit-sync.py repair (restores vendored files from the locked ref) or revert the working tree")
            return 3
        print(f"SYNC_APPLY_OK {manifest.get('version', '')}")
        return 0
    finally:
        if lock_fd is not None:
            os.close(lock_fd)
            try:
                (project / UPGRADE_LOCK).unlink()
            except FileNotFoundError:
                pass


def repair(project_root, backup: str | None = None) -> int:
    project = Path(project_root)
    lock = load_lock(project)
    source = None
    origin = origin_arg(lock.get("source", ""))
    try:
        source = open_source(origin, lock.get("ref") or None)
    except Exception as exc:
        try:
            source = open_source(origin, None)
            print(f"WARNING: locked ref unavailable ({exc}); using the source's current content")
        except Exception as fallback_exc:
            print(f"WARNING: toolkit source unavailable ({fallback_exc}); vendored files and managed blocks not restored")
    if source is not None:
        manifest = source.manifest()
        entries = target_entries(manifest)
        for relpath, expected in sorted((lock.get("files") or {}).items()):
            path = project / relpath
            if path.is_file() and sha_file(path) == expected:
                continue
            source_rel = entries.get(relpath, {}).get("path", relpath)
            data = source.read(source_rel)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        blocks = {}
        for name, (template, _markers) in AGENTS_TEMPLATES.items():
            if (source.base / template).is_file():
                blocks[name] = source.read(template).decode("utf-8")
        compose_agents(project, blocks)
        if (source.base / OPENSPEC_TEMPLATE).is_file():
            compose_openspec_config(project, source.read(OPENSPEC_TEMPLATE).decode("utf-8"))
        if (source.base / GITIGNORE_TEMPLATE).is_file():
            compose_gitignore(project, source.read(GITIGNORE_TEMPLATE).decode("utf-8"))
    regenerate(project)
    state_path = project / "workflow-state.json"
    restore: Path | None = Path(backup) if backup else None
    if restore is None:
        readable = False
        if state_path.is_file():
            try:
                json.loads(state_path.read_text(encoding="utf-8"))
                readable = True
            except Exception:
                readable = False
        if not readable:
            backups = sorted((project / "workflow/state-backups").glob("*.json"))
            restore = backups[-1] if backups else None
    if restore is not None:
        if not restore.is_file():
            raise ValueError(f"backup not found: {restore}")
        state_path.write_bytes(restore.read_bytes())
    errors = verify(project, require_lock=True)
    if errors:
        print("SYNC_REPAIR_INCOMPLETE")
        for error in errors:
            print(" - " + error)
        return 1
    print("SYNC_REPAIR_OK")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="install a toolkit release into a project repository")
    p_init.add_argument("--from", dest="source", required=True)
    p_init.add_argument("--ref", default="")
    p_init.add_argument("--project", default=".")

    p_verify = sub.add_parser("verify", help="verify a vendored installation")
    p_verify.add_argument("--project", default=".")
    p_verify.add_argument("--require-lock", action="store_true")

    p_plan = sub.add_parser("plan", help="show the upgrade diff (read-only)")
    p_plan.add_argument("--from", dest="source", default="")
    p_plan.add_argument("--ref", default="")
    p_plan.add_argument("--project", default=".")

    p_apply = sub.add_parser("apply", help="apply a toolkit upgrade")
    p_apply.add_argument("--from", dest="source", default="")
    p_apply.add_argument("--ref", default="")
    p_apply.add_argument("--project", default=".")
    p_apply.add_argument("--take-upstream", action="store_true")
    p_apply.add_argument("--keep-local", action="store_true")
    p_apply.add_argument("--run-migrations", action="store_true")

    p_repair = sub.add_parser("repair", help="recompose managed blocks and restore state")
    p_repair.add_argument("--project", default=".")
    p_repair.add_argument("--backup", default="")

    args = parser.parse_args(argv)
    if args.command == "init":
        try:
            source = open_source(args.source, args.ref)
            lock = init(Path(args.project), source, args.ref, source.git_commit())
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        print(f"SYNC_INIT_OK {lock.name}")
        return 0
    if args.command == "plan":
        try:
            result = plan(Path(args.project), resolve_source(Path(args.project), args.source, args.ref))
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    if args.command == "apply":
        try:
            return apply(Path(args.project),
                         resolve_source(Path(args.project), args.source, args.ref), args.ref,
                         take_upstream=args.take_upstream, keep_local=args.keep_local,
                         run_migrations=args.run_migrations)
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
    if args.command == "repair":
        try:
            return repair(Path(args.project), args.backup or None)
        except Exception as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
    errors = verify(Path(args.project), require_lock=args.require_lock)
    if errors:
        print("SYNC_VERIFY_FAILED")
        for error in errors:
            print(" - " + error)
        return 1
    print("SYNC_VERIFY_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
