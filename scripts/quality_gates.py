#!/usr/bin/env python3
"""Shared helpers for the static-analysis quality gates.

The functions in this module are consumed by ``check-quality-gates.py``,
``run-quality-gates.py`` and ``check-static-analysis.py``. They validate the
project-level ``docs/architecture/quality-gates.json`` document and the
Change-scoped waiver file, and probe tools without ever installing them.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
from datetime import date
from pathlib import Path

GATES_REL = "docs/architecture/quality-gates.json"
WAIVERS_REL = "openspec/changes/{change_id}/design/static-waivers.json"

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DRIVE_OR_UNC_RE = re.compile(r"^([A-Za-z]:|//)")

NETWORK_PATTERNS = (
    (re.compile(r"^\s*npx\s+(?!--no-install)", re.IGNORECASE),
     "npx without --no-install may fetch packages from the network"),
    (re.compile(r"\bnpm\s+exec\b(?!--no)", re.IGNORECASE),
     "npm exec may fetch packages from the network"),
    (re.compile(r"\bpnpm\s+dlx\b", re.IGNORECASE),
     "pnpm dlx fetches packages from the network"),
    (re.compile(r"\buvx\b", re.IGNORECASE),
     "uvx fetches packages from the network"),
    (re.compile(r"\bpipx\s+run\b", re.IGNORECASE),
     "pipx run fetches packages from the network"),
    (re.compile(r"\bgo\s+run\b", re.IGNORECASE),
     "go run may download modules from the network"),
    (re.compile(r"\b(?:pip|pip3)\s+install\b", re.IGNORECASE),
     "pip install fetches packages from the network"),
    (re.compile(r"\b(?:npm|pnpm)\s+(?:install|i|ci)\b", re.IGNORECASE),
     "npm/pnpm install fetches packages from the network"),
    (re.compile(r"\b(?:yarn|yarnpkg)\s+(?:add|install)\b", re.IGNORECASE),
     "yarn add/install fetches packages from the network"),
    (re.compile(r"\bgo\s+get\b", re.IGNORECASE),
     "go get downloads modules from the network"),
    (re.compile(r"\bcargo\s+install\b", re.IGNORECASE),
     "cargo install fetches crates from the network"),
    (re.compile(r"\bdocker\s+pull\b", re.IGNORECASE),
     "docker pull fetches images from the network"),
    (re.compile(r"\bmvn\b[^\n]*?\bdependency:(?:get|go-offline|resolve)\b", re.IGNORECASE),
     "mvn dependency resolution may fetch from the network"),
    (re.compile(r"\bmvn\b[^\n]*?(?<!\S)(?:-U|--update-snapshots)(?=\s|$)", re.IGNORECASE),
     "mvn -U may fetch updates from the network"),
)

STATUSES = ("DRAFT", "FROZEN", "APPROVED")
SEVERITIES = ("error", "warning", "info")
TOOL_MODES = ("blocking", "advisory")

WAIVER_TEXT_KEYS = (
    "id", "stack", "tool", "file", "rule", "reason", "owner", "approved_by",
)
WAIVER_DATE_KEYS = ("approved_at", "expires_at")


def today_iso() -> str:
    """Return today's date as an ISO ``YYYY-MM-DD`` string."""
    return date.today().isoformat()


def sha256_file(path: Path) -> str:
    """Return the SHA-256 hex digest of the file's raw bytes."""
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_gates(root: Path) -> dict:
    """Load the quality gates document; raises on a missing or malformed file."""
    return json.loads((Path(root) / GATES_REL).read_text(encoding="utf-8"))


def load_waivers(root: Path, change_id: str) -> list[dict]:
    """Load Change-scoped waivers; a missing file means no waivers."""
    path = Path(root) / WAIVERS_REL.format(change_id=change_id)
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("waiver file must contain a JSON object")
    waivers = data.get("waivers")
    if not isinstance(waivers, list):
        raise ValueError("waiver file 'waivers' must be a list")
    return waivers


def find_network_command(command: str) -> str | None:
    """Return a reason when the command may fetch packages, else ``None``."""
    if not isinstance(command, str):
        return None
    for pattern, reason in NETWORK_PATTERNS:
        if pattern.search(command):
            return reason
    return None


def safe_relative_path(value) -> str | None:
    """Return a POSIX-normalized repository-relative path, or ``None`` if unsafe."""
    if not isinstance(value, str):
        return None
    normalized = value.replace("\\", "/")
    if not normalized:
        return None
    # Posix-absolute paths are not "absolute" under PureWindowsPath, and
    # Windows drive-relative/UNC prefixes need explicit rejection.
    if normalized.startswith("/"):
        return None
    if Path(normalized).is_absolute():
        return None
    if DRIVE_OR_UNC_RE.match(normalized):
        return None
    if any(part == ".." for part in normalized.split("/")):
        return None
    return normalized


def validate_gates(data: dict, root: Path, *, require_materialized: bool = False) -> list[str]:
    """Validate the gates document; returns human-readable error strings."""
    errors: list[str] = []
    if not isinstance(data, dict):
        return [f"{GATES_REL} must contain a JSON object"]

    if data.get("schema_version") != "1.0":
        errors.append('schema_version must be "1.0"')
    project = data.get("project")
    if not isinstance(project, str) or not project.strip():
        errors.append("project must be a non-empty string")
    if data.get("status") not in STATUSES:
        errors.append("status must be one of DRAFT, FROZEN, APPROVED")

    policy = data.get("policy")
    if not isinstance(policy, dict):
        errors.append("policy must be an object")
        policy = {}

    severities = policy.get("blocking_severities")
    if not isinstance(severities, list) or not severities:
        errors.append("policy.blocking_severities must be a non-empty list")
    else:
        for severity in severities:
            if severity not in SEVERITIES:
                errors.append(f"policy.blocking_severities has invalid value: {severity!r}")

    if not isinstance(policy.get("require_clean_exit"), bool):
        errors.append("policy.require_clean_exit must be a boolean")

    waiver_file = policy.get("waiver_file")
    if not isinstance(waiver_file, str) or not waiver_file.strip():
        errors.append("policy.waiver_file must be a non-empty string")

    waiver = policy.get("waiver")
    if not isinstance(waiver, dict):
        errors.append("policy.waiver must be an object")
        waiver = {}
    for key in ("allowed", "requires_approver"):
        if not isinstance(waiver.get(key), bool):
            errors.append(f"policy.waiver.{key} must be a boolean")
    max_days = waiver.get("max_days")
    if isinstance(max_days, bool) or not isinstance(max_days, int) or not 1 <= max_days <= 365:
        errors.append("policy.waiver.max_days must be an integer between 1 and 365")

    allow_network_install = policy.get("allow_network_install")
    if not isinstance(allow_network_install, bool):
        errors.append("policy.allow_network_install must be a boolean")
        allow_network_install = False

    timeout = policy.get("command_timeout_seconds", 600)
    if isinstance(timeout, bool) or not isinstance(timeout, int) or timeout <= 0:
        errors.append("policy.command_timeout_seconds must be a positive integer")

    stacks = data.get("stacks")
    if not isinstance(stacks, list) or not stacks:
        errors.append("stacks must be a non-empty list")
        stacks = []

    stack_ids: set[str] = set()
    blocking_found = False
    for index, stack in enumerate(stacks):
        label = f"stacks[{index}]"
        if not isinstance(stack, dict):
            errors.append(f"{label} must be an object")
            continue

        stack_id = stack.get("id")
        if not isinstance(stack_id, str) or not stack_id.strip():
            errors.append(f"{label}.id must be a non-empty slug")
        else:
            label = f"stack {stack_id!r}"
            if not SLUG_RE.match(stack_id):
                errors.append(f"{label}.id must match [a-z0-9]+(-[a-z0-9]+)*")
            elif stack_id in stack_ids:
                errors.append(f"{label}: duplicate stack id: {stack_id}")
            else:
                stack_ids.add(stack_id)

        language = stack.get("language")
        if not isinstance(language, str) or not language.strip():
            errors.append(f"{label}.language must be a non-empty string")

        stack_root = stack.get("root")
        safe_root = safe_relative_path(stack_root)
        if safe_root is None:
            errors.append(
                f"{label}.root must be a safe repository-relative path: {stack_root!r}"
            )

        tools = stack.get("tools")
        if not isinstance(tools, list) or not tools:
            errors.append(f"{label}.tools must be a non-empty list")
            tools = []

        tool_ids: set[str] = set()
        for tool_index, tool in enumerate(tools):
            tool_label = f"{label}.tools[{tool_index}]"
            if not isinstance(tool, dict):
                errors.append(f"{tool_label} must be an object")
                continue

            tool_id = tool.get("id")
            if not isinstance(tool_id, str) or not tool_id.strip():
                errors.append(f"{tool_label}.id must be a non-empty slug")
            else:
                tool_label = f"{label} tool {tool_id!r}"
                if not SLUG_RE.match(tool_id):
                    errors.append(f"{tool_label}.id must match [a-z0-9]+(-[a-z0-9]+)*")
                elif tool_id in tool_ids:
                    errors.append(f"{tool_label}: duplicate tool id: {tool_id}")
                else:
                    tool_ids.add(tool_id)

            mode = tool.get("mode")
            if mode not in TOOL_MODES:
                errors.append(f"{tool_label}.mode must be 'blocking' or 'advisory'")
            elif mode == "blocking":
                blocking_found = True

            command = tool.get("command")
            if not isinstance(command, str) or not command.strip():
                errors.append(f"{tool_label}.command must be a non-empty string")
            elif not allow_network_install:
                reason = find_network_command(command)
                if reason is not None:
                    errors.append(f"{tool_label}.command may fetch from the network: {reason}")

            configs = tool.get("configs")
            if not isinstance(configs, list) or not configs:
                errors.append(f"{tool_label}.configs must be a non-empty list")
            else:
                for config in configs:
                    if safe_relative_path(config) is None:
                        errors.append(
                            f"{tool_label}.configs must be safe stack-relative paths: {config!r}"
                        )

    if stacks and not blocking_found:
        errors.append('at least one tool must have mode "blocking"')

    if require_materialized:
        root_resolved = Path(root).resolve()
        for index, stack in enumerate(stacks):
            if not isinstance(stack, dict):
                continue
            safe_root = safe_relative_path(stack.get("root"))
            if safe_root is None:
                continue
            stack_label = f"stack {stack.get('id')!r}"
            stack_root = (root_resolved / safe_root).resolve()
            if not stack_root.is_relative_to(root_resolved):
                errors.append(f"{stack_label}: root escapes the project root: {safe_root}")
                continue
            if not stack_root.is_dir():
                errors.append(f"{stack_label}: root directory is missing: {safe_root}")
                continue
            tools = stack.get("tools")
            if not isinstance(tools, list):
                continue
            for tool in tools:
                if not isinstance(tool, dict):
                    continue
                configs = tool.get("configs")
                if not isinstance(configs, list):
                    continue
                for config in configs:
                    safe_config = safe_relative_path(config)
                    if safe_config is None:
                        continue
                    config_path = (stack_root / safe_config).resolve()
                    config_label = f"{stack_label} tool {tool.get('id')!r}"
                    if not config_path.is_relative_to(root_resolved):
                        errors.append(f"{config_label}: config escapes the project root: {safe_config}")
                    elif not config_path.is_file():
                        errors.append(f"{config_label}: config file is missing: {safe_config}")

    return errors


def validate_waivers(waivers: list[dict], root: Path, gates: dict, today: str) -> list[str]:
    """Validate Change-scoped waivers against the gates document."""
    errors: list[str] = []
    if not isinstance(waivers, list):
        return ["waivers must be a list"]

    stack_tools: dict[str, set[str]] = {}
    stacks = gates.get("stacks") if isinstance(gates, dict) else None
    if isinstance(stacks, list):
        for stack in stacks:
            if not isinstance(stack, dict):
                continue
            stack_id = stack.get("id")
            if not isinstance(stack_id, str):
                continue
            tools = stack.get("tools")
            tool_ids: set[str] = set()
            if isinstance(tools, list):
                for tool in tools:
                    if isinstance(tool, dict) and isinstance(tool.get("id"), str):
                        tool_ids.add(tool["id"])
            stack_tools[stack_id] = tool_ids

    root_resolved = Path(root).resolve()
    for index, waiver in enumerate(waivers):
        if not isinstance(waiver, dict):
            errors.append(f"waivers[{index}] must be an object")
            continue

        waiver_id = waiver.get("id")
        label = waiver_id if isinstance(waiver_id, str) and waiver_id.strip() else f"waivers[{index}]"

        for key in WAIVER_TEXT_KEYS:
            value = waiver.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"waiver {label}: {key} must be a non-empty string")

        parsed_dates: dict[str, str] = {}
        for key in WAIVER_DATE_KEYS:
            value = waiver.get(key)
            if isinstance(value, str) and DATE_RE.match(value):
                parsed_dates[key] = value
            else:
                errors.append(f"waiver {label}: {key} must match YYYY-MM-DD")
        if len(parsed_dates) == len(WAIVER_DATE_KEYS):
            approved_at = parsed_dates["approved_at"]
            expires_at = parsed_dates["expires_at"]
            if approved_at > expires_at:
                errors.append(f"waiver {label}: approved_at must not be after expires_at")
            if expires_at < today:
                errors.append(f"waiver {label}: expired on {expires_at} (today is {today})")

        stack_id = waiver.get("stack")
        tool_id = waiver.get("tool")
        if isinstance(stack_id, str) and stack_id:
            if stack_id not in stack_tools:
                errors.append(f"waiver {label}: unknown stack: {stack_id}")
            elif isinstance(tool_id, str) and tool_id and tool_id not in stack_tools[stack_id]:
                errors.append(f"waiver {label}: unknown tool {tool_id!r} in stack {stack_id!r}")

        file_value = waiver.get("file")
        safe_file = safe_relative_path(file_value)
        if safe_file is None:
            if isinstance(file_value, str) and file_value.strip():
                errors.append(
                    f"waiver {label}: file must be a safe repository-relative path: {file_value!r}"
                )
        else:
            target = (root_resolved / safe_file).resolve()
            if not target.is_relative_to(root_resolved):
                errors.append(f"waiver {label}: file escapes the project root: {safe_file}")
            elif not target.is_file():
                errors.append(f"waiver {label}: file does not exist: {safe_file}")

    return errors


def probe_tool(stack_root: Path, command: str) -> tuple[bool, str]:
    """Probe the command's first token without running or installing anything.

    Returns ``(ok, detail)``; ``detail`` is the resolved executable on success
    and a reason naming the missing tool/package on failure.
    """
    try:
        tokens = shlex.split(command)
    except ValueError as exc:
        return False, f"cannot parse command: {exc}"
    if not tokens:
        return False, "command is empty"

    token = tokens[0]
    executable = _probe_first_token(Path(stack_root), token)
    if executable is None:
        return False, f"tool not found: {token}"

    if Path(token).stem.lower() == "npx":
        package = _npx_package(tokens)
        if package is not None and not _node_package_available(Path(stack_root), package):
            return False, f"npx package not installed locally: {package}"

    return True, executable


def _probe_first_token(stack_root: Path, token: str) -> str | None:
    path = Path(token)
    if path.is_absolute():
        return str(path) if path.is_file() else None
    if "/" in token or "\\" in token:
        candidate = stack_root / token
        if candidate.is_file():
            return str(candidate)
    return shutil.which(token)


def _npx_package(tokens: list[str]) -> str | None:
    for index, token in enumerate(tokens):
        if token != "--no-install":
            continue
        for candidate in tokens[index + 1:]:
            if candidate == "--" or candidate.startswith("-"):
                continue
            return candidate
    return None


def _node_package_available(stack_root: Path, package: str) -> bool:
    binary = package.rsplit("/", 1)[-1]
    if not binary:
        return False
    bin_dir = stack_root / "node_modules" / ".bin"
    names = [binary]
    if os.name == "nt":
        names.extend(binary + extension for extension in (".cmd", ".exe", ".bat", ".ps1"))
    if any((bin_dir / name).is_file() for name in names):
        return True
    return shutil.which(binary) is not None
