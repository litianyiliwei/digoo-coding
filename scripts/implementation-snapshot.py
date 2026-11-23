#!/usr/bin/env python3
"""Capture the stage-08 implementation base snapshot for a Change.

Usage:
  python scripts/implementation-snapshot.py <change-id>
  python scripts/implementation-snapshot.py <change-id> --force --reason <text>

Writes ``openspec/changes/<change-id>/design/evidence/implementation-base.json``
with the current ``git rev-parse HEAD``, a SHA-256 for every counted workspace
file (tracked and untracked, after the shared ``gate_common`` exclusions), and a
fingerprint over the canonical file map.

The file is script-generated evidence: re-run only through ``--force`` with a
non-empty ``--reason`` (recorded as ``override_reason``); never hand-edit it.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))
import gate_common as gm  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]

SCHEMA_VERSION = "1.0"
EVIDENCE_REL = "openspec/changes/{change_id}/design/evidence/implementation-base.json"


def _root(root: Path | None = None) -> Path:
    return Path(root) if root is not None else Path(ROOT)


def _rel(path: Path, root: Path | None = None) -> str:
    try:
        return path.relative_to(_root(root)).as_posix()
    except ValueError:
        return path.as_posix()


def evidence_path(change_id: str, root: Path | None = None) -> Path:
    """Return the evidence target path for ``change_id``."""
    return _root(root) / EVIDENCE_REL.format(change_id=change_id)


def _validate_change_id(change_id: str) -> str:
    value = (change_id or "").strip()
    if not value or "/" in value or "\\" in value or ".." in value:
        raise RuntimeError(
            f"invalid change-id {change_id!r}; expected a single directory name "
            "without path separators"
        )
    return value


def git_head(root: Path | None = None) -> str:
    """Return ``git rev-parse HEAD``; raise RuntimeError with git stderr on failure."""
    base = _root(root)
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(base),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except OSError as exc:
        raise RuntimeError(f"git rev-parse HEAD failed in {base}: {exc}") from exc
    if proc.returncode != 0:
        detail = proc.stderr.strip() or proc.stdout.strip() or "unknown git error"
        raise RuntimeError(f"git rev-parse HEAD failed in {base}: {detail}")
    head = proc.stdout.strip()
    if not head:
        raise RuntimeError(f"git rev-parse HEAD returned no commit in {base}")
    return head


def capture(change_id: str, root: Path | None = None) -> dict:
    """Build the evidence document without touching disk."""
    base = _root(root)
    change_id = _validate_change_id(change_id)
    head = git_head(base)
    files = gm.enumerate_files(base, change_id)
    return {
        "schema_version": SCHEMA_VERSION,
        "change_id": change_id,
        "captured_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "head": head,
        "files": files,
        "fingerprint": gm.fingerprint(files),
    }


def write_snapshot(
    change_id: str,
    root: Path | None = None,
    force: bool = False,
    reason: str = "",
) -> tuple[Path, dict]:
    """Write the evidence file and return ``(path, document)``.

    Refuses an existing snapshot unless ``force`` is set; ``force`` additionally
    requires a non-empty ``reason`` that lands as ``override_reason`` in the file.
    """
    base = _root(root)
    change_id = _validate_change_id(change_id)
    target = evidence_path(change_id, base)
    reason = (reason or "").strip()

    if force and not reason:
        raise RuntimeError(
            f"--force requires a non-empty --reason (target {_rel(target, base)})"
        )
    if target.exists() and not force:
        raise RuntimeError(
            f"refusing to overwrite existing snapshot {_rel(target, base)}; "
            "re-run with --force --reason <text>"
        )

    doc = capture(change_id, base)
    if force and target.exists():
        doc["override_reason"] = reason

    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return target, doc


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        prog="implementation-snapshot.py",
        description="Capture the stage-08 implementation base snapshot.",
    )
    parser.add_argument("change_id", metavar="change-id")
    parser.add_argument("--force", action="store_true", help="overwrite an existing snapshot")
    parser.add_argument("--reason", default="", help="required with --force; recorded as override_reason")
    args = parser.parse_args(argv)

    try:
        target, doc = write_snapshot(
            args.change_id, force=args.force, reason=args.reason
        )
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"Wrote {_rel(target)} ({len(doc['files'])} file(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
