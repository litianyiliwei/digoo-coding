#!/usr/bin/env python3
"""Run frozen static-analysis gates for a Change and write machine evidence.

The runner validates ``docs/architecture/quality-gates.json`` and the
Change-scoped waiver file, probes every tool without installing anything,
executes the commands in their stack roots with a per-tool timeout, captures
logs under the Change's evidence directory, and writes
``design/evidence/static-analysis.json`` atomically.

Exit codes: 0 = verdict PASS, 1 = FAIL or BLOCKED, 2 = usage/configuration.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import signal
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from quality_gates import (
    GATES_REL,
    WAIVERS_REL,
    load_gates,
    load_waivers,
    probe_tool,
    safe_relative_path,
    sha256_file,
    today_iso,
    validate_gates,
    validate_waivers,
)

ROOT = Path(__file__).resolve().parents[1]
CHANGE_ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DEFAULT_TIMEOUT_SECONDS = 600
DEFAULT_IDENTITY = "AGENT"
WAIVER_EVIDENCE_KEYS = ("id", "file", "rule", "approved_by", "expires_at")


class ConfigError(Exception):
    """A usage or configuration problem; maps to exit code 2."""


def now_iso() -> str:
    """Return the current UTC instant in ISO-8601 form."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("change_id", help="OpenSpec Change id (kebab-case slug)")
    parser.add_argument("--output", required=True,
                        help="Evidence path (absolute or root-relative), inside the Change evidence dir")
    parser.add_argument("--root", default=str(ROOT), help="Project root (defaults to this repository)")
    parser.add_argument("--identity", default=None,
                        help="Builder identity for 08, verifier identity for 09 (defaults to AGENT)")
    parser.add_argument("--builder-identity", default=None,
                        help="Builder identity recorded by the independent 09 run")
    parser.add_argument("--independent", action="store_true",
                        help="Mark the run independent (requires distinct --identity and --builder-identity)")
    parser.add_argument("--stack", default=None, help="Run only this stack id")
    parser.add_argument("--source-revision", default=None,
                        help="Source revision to record (defaults to git HEAD)")
    return parser.parse_args(argv)


def validate_change_id(change_id: str) -> str:
    if not CHANGE_ID_RE.match(change_id):
        raise ConfigError(
            f"change id must match [a-z0-9]+(-[a-z0-9]+)*: {change_id!r}"
        )
    return change_id


def load_valid_gates(root: Path) -> dict:
    try:
        gates = load_gates(root)
    except (OSError, ValueError) as exc:
        raise ConfigError(f"cannot read {GATES_REL}: {exc}") from exc
    errors = validate_gates(gates, root, require_materialized=True)
    if errors:
        raise ConfigError("\nERROR: ".join(errors))
    return gates


def load_valid_waivers(root: Path, change_id: str, gates: dict) -> list[dict]:
    """Load and validate the Change-scoped waiver file when it exists."""
    policy = gates.get("policy") if isinstance(gates, dict) else None
    waiver_template = policy.get("waiver_file") if isinstance(policy, dict) else None
    if not isinstance(waiver_template, str) or not waiver_template.strip():
        raise ConfigError("policy.waiver_file must be a non-empty string")
    waiver_rel = waiver_template.replace("<change-id>", change_id)
    safe_waiver = safe_relative_path(waiver_rel)
    if safe_waiver is None:
        raise ConfigError(
            f"policy.waiver_file must be a safe repository-relative path: {waiver_template!r}"
        )
    if not (root / safe_waiver).is_file():
        return []

    if safe_waiver == WAIVERS_REL.format(change_id=change_id):
        try:
            waivers = load_waivers(root, change_id)
        except (OSError, ValueError) as exc:
            raise ConfigError(f"cannot read waiver file {safe_waiver}: {exc}") from exc
    else:
        try:
            data = json.loads((root / safe_waiver).read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise ConfigError(f"cannot read waiver file {safe_waiver}: {exc}") from exc
        if not isinstance(data, dict) or not isinstance(data.get("waivers"), list):
            raise ConfigError(f"waiver file {safe_waiver} must contain a 'waivers' list")
        waivers = data["waivers"]

    errors = validate_waivers(waivers, root, gates, today_iso())
    if errors:
        raise ConfigError("\nERROR: ".join(errors))
    return waivers


def resolve_output(root: Path, change_id: str, output: str) -> tuple[Path, Path]:
    """Return ``(target, evidence_dir)`` after the containment check."""
    evidence_dir = (
        root / "openspec" / "changes" / change_id / "design" / "evidence"
    ).resolve()
    target = Path(output)
    if not target.is_absolute():
        target = root / target
    target = target.resolve()
    if not target.is_relative_to(evidence_dir):
        raise ConfigError(
            "--output must resolve inside "
            f"openspec/changes/{change_id}/design/evidence/: {output!r}"
        )
    return target, evidence_dir


def resolve_source_revision(root: Path, revision: str | None) -> str:
    if revision is not None:
        revision = revision.strip()
        if not revision:
            raise ConfigError("--source-revision must be a non-empty string")
        return revision
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(root),
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise ConfigError(f"cannot run git rev-parse HEAD: {exc}") from exc
    revision = result.stdout.strip()
    if result.returncode != 0 or not revision:
        raise ConfigError(
            f"git rev-parse HEAD produced no revision in {root} "
            f"(exit {result.returncode}): {result.stderr.strip()}"
        )
    return revision


def resolve_identities(args: argparse.Namespace) -> tuple[bool, str, str]:
    """Return ``(independent, verifier_identity, builder_identity)``."""
    identity = args.identity.strip() if isinstance(args.identity, str) else None
    builder = args.builder_identity.strip() if isinstance(args.builder_identity, str) else None
    if identity == "":
        raise ConfigError("--identity must be a non-empty string")
    if builder == "":
        raise ConfigError("--builder-identity must be a non-empty string")

    if args.independent:
        if not identity:
            raise ConfigError("--independent requires an explicit --identity (the verifier)")
        if not builder:
            raise ConfigError(
                "--independent requires an explicit --builder-identity (the 08 builder)"
            )
        if identity == builder:
            raise ConfigError("--independent requires distinct --identity and --builder-identity")
        return True, identity, builder

    return False, "", builder or identity or DEFAULT_IDENTITY


def select_stacks(gates: dict, stack_filter: str | None) -> list[dict]:
    stacks = [stack for stack in gates.get("stacks", []) if isinstance(stack, dict)]
    if stack_filter is None:
        return stacks
    selected = [stack for stack in stacks if stack.get("id") == stack_filter]
    if not selected:
        raise ConfigError(f"--stack selects an unknown stack: {stack_filter!r}")
    return selected


def log_basename(stack: dict, used: set[str], tool_id: str) -> str:
    """Build a unique, filesystem-safe log name containing the stack root."""
    stack_rel = safe_relative_path(stack.get("root")) or str(stack.get("id", "root"))
    base = stack_rel.replace("/", "-").replace("\\", "-").strip("-")
    if not base or base == ".":
        base = "root"
    candidate = f"{base}-{tool_id}"
    name = candidate
    suffix = 2
    while name in used:
        name = f"{candidate}-{suffix}"
        suffix += 1
    used.add(name)
    return f"{name}.log"


def hash_configs(stack_root: Path, tool: dict) -> list[dict]:
    configs: list[dict] = []
    for config in tool.get("configs", []):
        safe_config = safe_relative_path(config)
        if safe_config is None:
            raise ConfigError(f"unsafe tool config path: {config!r}")
        try:
            digest = sha256_file(stack_root / safe_config)
        except OSError as exc:
            raise ConfigError(f"cannot read config file {safe_config}: {exc}") from exc
        configs.append({"path": safe_config, "sha256": digest})
    return configs


def write_log(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    except OSError as exc:
        raise ConfigError(f"cannot write log file {path}: {exc}") from exc


def append_log(log_handle, text: str) -> None:
    """Append one raw-bytes log line; the log is the artifact, so never decode."""
    log_handle.write(text.encode("utf-8", "replace") + b"\n")
    log_handle.flush()


def terminate_process_tree(process: subprocess.Popen) -> None:
    """Kill the gate command and its children before waiting again.

    On Windows, killing only the wrapper leaves grandchildren holding inherited
    handles; on POSIX the child runs in its own session so the whole group dies.
    """
    if os.name == "nt":
        try:
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
                timeout=10,
            )
        except (OSError, subprocess.SubprocessError):
            pass
    else:
        try:
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            return
        except OSError:
            pass
    try:
        process.kill()
    except OSError:
        pass


def run_tool(
    root: Path,
    evidence_dir: Path,
    stack: dict,
    tool: dict,
    timeout_seconds: int,
    used_log_names: set[str],
) -> dict:
    """Probe and run one tool, returning its evidence record."""
    stack_id = str(stack.get("id"))
    stack_rel = safe_relative_path(stack.get("root"))
    if stack_rel is None:
        raise ConfigError(f"stack {stack_id!r} has an unsafe root")
    stack_root = root / stack_rel
    tool_id = str(tool.get("id"))
    command = str(tool.get("command"))
    mode = str(tool.get("mode"))
    configs = hash_configs(stack_root, tool)
    log_name = log_basename(stack, used_log_names, tool_id)
    log_path = evidence_dir / "static-analysis-logs" / log_name
    log_rel = log_path.relative_to(root).as_posix()

    blocked_reason: str | None = None
    timed_out = False
    exit_code: int | None = None

    probe_ok, probe_detail = probe_tool(stack_root, command)
    if not probe_ok:
        blocked_reason = probe_detail
        write_log(
            log_path,
            [
                f"command: {command}",
                f"cwd: {stack_rel}",
                f"mode: {mode}",
                f"probe: {probe_detail}",
                f"exit_code: {exit_code}",
                "timed_out: false",
                f"blocked_reason: {blocked_reason}",
                "--- output ---",
                "(probe failed; command not executed)",
            ],
        )
    else:
        try:
            tokens = shlex.split(command)
        except ValueError as exc:  # defensive: probe already parsed the command
            raise ConfigError(f"cannot parse command for tool {tool_id!r}: {exc}") from exc
        log_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            log_handle = log_path.open("wb")
        except OSError as exc:
            raise ConfigError(f"cannot write log file {log_path}: {exc}") from exc
        try:
            # The tool writes straight into the log file: inherited pipes can
            # never leave a killed child's output unread or block our wait.
            log_handle.write(
                (
                    f"command: {command}\n"
                    f"cwd: {stack_rel}\n"
                    f"mode: {mode}\n"
                    f"probe: {probe_detail}\n"
                    "--- output ---\n"
                ).encode("utf-8", "replace")
            )
            log_handle.flush()
            spawn_kwargs: dict = {
                "cwd": str(stack_root),
                "stdout": log_handle,
                "stderr": subprocess.STDOUT,
            }
            if os.name != "nt":
                spawn_kwargs["start_new_session"] = True
            try:
                process = subprocess.Popen(tokens, **spawn_kwargs)
            except (OSError, ValueError) as exc:
                blocked_reason = f"failed to execute {tokens[0]!r}: {exc}"
                append_log(log_handle, "(execution failed)")
            else:
                try:
                    exit_code = process.wait(timeout=timeout_seconds)
                except subprocess.TimeoutExpired:
                    timed_out = True
                    exit_code = None
                    terminate_process_tree(process)
                    try:
                        process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        pass
                    append_log(
                        log_handle,
                        f"timed_out: true (process tree killed after {timeout_seconds}s)",
                    )
                except OSError as exc:
                    blocked_reason = f"failed to execute {tokens[0]!r}: {exc}"
            append_log(log_handle, f"exit_code: {exit_code}")
            append_log(log_handle, f"timed_out: {'true' if timed_out else 'false'}")
        finally:
            log_handle.close()

    result: dict = {
        "stack_id": stack_id,
        "tool": tool_id,
        "mode": mode,
        "command": command,
        "cwd": stack_rel,
        "exit_code": exit_code,
        "timed_out": timed_out,
        "log": log_rel,
        "configs": configs,
    }
    if blocked_reason:
        result["blocked_reason"] = blocked_reason
    return result


def compute_verdict(results: list[dict]) -> str:
    blocking = [item for item in results if item.get("mode") == "blocking"]
    if any(item.get("blocked_reason") for item in blocking):
        return "BLOCKED"
    if any(
        item.get("timed_out") or item.get("exit_code") not in (0, None)
        for item in blocking
    ):
        return "FAIL"
    return "PASS"


def write_json_atomic(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(
        prefix=".static-analysis-", suffix=".tmp", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_name, path)
    except BaseException:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def run(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    change_id = validate_change_id(args.change_id)
    change_dir = root / "openspec" / "changes" / change_id
    if not change_dir.is_dir():
        raise ConfigError(f"Change directory is missing: openspec/changes/{change_id}")

    gates = load_valid_gates(root)
    waivers = load_valid_waivers(root, change_id, gates)
    target, evidence_dir = resolve_output(root, change_id, args.output)
    source_revision = resolve_source_revision(root, args.source_revision)
    independent, verifier_identity, builder_identity = resolve_identities(args)
    stacks = select_stacks(gates, args.stack)

    policy = gates.get("policy", {})
    timeout_seconds = policy.get("command_timeout_seconds", DEFAULT_TIMEOUT_SECONDS)

    run_at = now_iso()
    results: list[dict] = []
    executed_stack_ids: set[str] = set()
    used_log_names: set[str] = set()
    for stack in stacks:
        executed_stack_ids.add(str(stack.get("id")))
        for tool in stack.get("tools", []):
            if not isinstance(tool, dict):
                continue
            results.append(
                run_tool(
                    root, evidence_dir, stack, tool, timeout_seconds, used_log_names
                )
            )

    waivers_applied = [
        {key: waiver.get(key) for key in WAIVER_EVIDENCE_KEYS}
        for waiver in waivers
        if isinstance(waiver, dict) and waiver.get("stack") in executed_stack_ids
    ]
    verdict = compute_verdict(results)

    evidence = {
        "schema_version": "1.0",
        "change_id": change_id,
        "source_revision": source_revision,
        "run_at": run_at,
        "gates_file": {"path": GATES_REL, "sha256": sha256_file(root / GATES_REL)},
        "independent": independent,
        "verifier_identity": verifier_identity,
        "builder_identity": builder_identity,
        "results": results,
        "waivers_applied": waivers_applied,
        "verdict": verdict,
    }
    try:
        write_json_atomic(target, evidence)
    except OSError as exc:
        raise ConfigError(f"cannot write evidence file {target}: {exc}") from exc

    if verdict == "PASS":
        print("STATIC_ANALYSIS_RUN_PASSED")
        return 0
    print(f"STATIC_ANALYSIS_RUN_{verdict}")
    return 1


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        return run(args)
    except ConfigError as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
