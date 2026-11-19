#!/usr/bin/env python3
"""Verify static-analysis evidence against the quality gates and Change waivers.

The checker reloads ``docs/architecture/quality-gates.json`` and the
Change-scoped waiver file, then verifies the recorded evidence: gates hash
(drift), one result per blocking stack/tool, clean exits, existing logs, config
hashes, waiver validity, and optional independent identities.

Exit codes: 0 = PASS, 1 = evidence validation failure, 2 = usage/configuration.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from quality_gates import (
    GATES_REL,
    safe_relative_path,
    sha256_file,
    today_iso,
    validate_gates,
    validate_waivers,
)

ROOT = Path(__file__).resolve().parents[1]
CHANGE_ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
EVIDENCE_NAME = "static-analysis.json"
INDEPENDENT_EVIDENCE_NAME = "static-analysis-independent.json"
WAIVER_APPLIED_KEYS = ("id", "file", "rule", "approved_by", "expires_at")


class ConfigError(Exception):
    """A usage or configuration problem; maps to exit code 2."""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--change", required=True, help="OpenSpec Change id (kebab-case slug)")
    parser.add_argument("--root", default=str(ROOT), help="Project root (defaults to this repository)")
    parser.add_argument("--evidence", default=None,
                        help="Evidence path (absolute or root-relative); defaults per --expect-independent")
    parser.add_argument("--expect-independent", action="store_true",
                        help="Require independent evidence with distinct verifier and builder identities")
    parser.add_argument("--strict", action="store_true",
                        help="Also require a non-empty builder identity")
    return parser.parse_args(argv)


def validate_change_id(change_id: str) -> str:
    if not CHANGE_ID_RE.match(change_id):
        raise ConfigError(
            f"change id must match [a-z0-9]+(-[a-z0-9]+)*: {change_id!r}"
        )
    return change_id


def evidence_dir_rel(change_id: str) -> str:
    return f"openspec/changes/{change_id}/design/evidence"


def resolve_evidence(root: Path, change_id: str, evidence: str | None,
                     expect_independent: bool) -> Path:
    """Resolve the evidence path and require it inside the Change evidence dir."""
    directory = (root / evidence_dir_rel(change_id)).resolve()
    if evidence is None:
        target = directory / (
            INDEPENDENT_EVIDENCE_NAME if expect_independent else EVIDENCE_NAME
        )
        return target
    target = Path(evidence)
    if not target.is_absolute():
        target = root / target
    target = target.resolve()
    if not target.is_relative_to(directory):
        raise ConfigError(
            f"--evidence must resolve inside {evidence_dir_rel(change_id)}/: {evidence!r}"
        )
    return target


def load_gates_document(root: Path) -> dict:
    try:
        data = json.loads((root / GATES_REL).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ConfigError(f"cannot read {GATES_REL}: {exc}") from exc
    errors = validate_gates(data, root, require_materialized=True)
    if errors:
        raise ConfigError("\nERROR: ".join(errors))
    return data


def gate_index(gates: dict) -> tuple[set[tuple[str, str]], dict[tuple[str, str], list[str]], dict[str, str]]:
    """Return blocking tuples, configs per tuple, and root-relative stack roots."""
    blocking: set[tuple[str, str]] = set()
    configs: dict[tuple[str, str], list[str]] = {}
    stack_roots: dict[str, str] = {}
    for stack in gates.get("stacks", []):
        if not isinstance(stack, dict):
            continue
        stack_id = stack.get("id")
        stack_root = safe_relative_path(stack.get("root"))
        if isinstance(stack_id, str) and stack_root is not None:
            stack_roots[stack_id] = stack_root
        for tool in stack.get("tools", []):
            if not isinstance(tool, dict):
                continue
            tool_id = tool.get("id")
            if not isinstance(stack_id, str) or not isinstance(tool_id, str):
                continue
            key = (stack_id, tool_id)
            safe_configs: list[str] = []
            for config in tool.get("configs", []):
                safe_config = safe_relative_path(config)
                if safe_config is not None:
                    safe_configs.append(safe_config)
            configs[key] = safe_configs
            if tool.get("mode") == "blocking":
                blocking.add(key)
    return blocking, configs, stack_roots


def load_change_waivers(root: Path, gates: dict, change_id: str, errors: list[str]) -> list[dict]:
    """Reload the Change-scoped waiver file; malformed content becomes an error."""
    policy = gates.get("policy") if isinstance(gates, dict) else None
    template = policy.get("waiver_file") if isinstance(policy, dict) else None
    if not isinstance(template, str) or not template.strip():
        raise ConfigError("policy.waiver_file must be a non-empty string")
    waiver_rel = template.replace("<change-id>", change_id)
    safe_waiver = safe_relative_path(waiver_rel)
    if safe_waiver is None:
        raise ConfigError(
            f"policy.waiver_file must be a safe repository-relative path: {template!r}"
        )
    path = root / safe_waiver
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        errors.append(f"cannot read waiver file {safe_waiver}: {exc}")
        return []
    if not isinstance(data, dict) or not isinstance(data.get("waivers"), list):
        errors.append(f"waiver file {safe_waiver} must contain a 'waivers' list")
        return []
    return data["waivers"]


def check_required_keys(evidence, change_id: str) -> list[str]:
    if not isinstance(evidence, dict):
        return ["evidence must contain a JSON object"]
    errors: list[str] = []
    if evidence.get("schema_version") != "1.0":
        errors.append('evidence.schema_version must be "1.0"')
    if evidence.get("change_id") != change_id:
        errors.append(
            f"evidence.change_id {evidence.get('change_id')!r} does not match --change {change_id!r}"
        )
    revision = evidence.get("source_revision")
    if not isinstance(revision, str) or not revision.strip():
        errors.append("evidence.source_revision must be a non-empty string")
    if evidence.get("verdict") != "PASS":
        errors.append(f"evidence.verdict must be PASS, found {evidence.get('verdict')!r}")
    results = evidence.get("results")
    if not isinstance(results, list) or not results:
        errors.append("evidence.results must be a non-empty list")
    gates_file = evidence.get("gates_file")
    if not isinstance(gates_file, dict):
        errors.append("evidence.gates_file must be an object")
    else:
        if gates_file.get("path") != GATES_REL:
            errors.append(
                f"evidence.gates_file.path must be {GATES_REL}, found {gates_file.get('path')!r}"
            )
        if not isinstance(gates_file.get("sha256"), str) or not gates_file.get("sha256").strip():
            errors.append("evidence.gates_file.sha256 must be a non-empty string")
    return errors


def check_blocking_results(evidence: dict, gates: dict, root: Path, errors: list[str]) -> None:
    blocking, gate_configs, stack_roots = gate_index(gates)
    root_resolved = Path(root).resolve()
    collected: dict[tuple[str, str], list[dict]] = {key: [] for key in blocking}

    for index, result in enumerate(evidence.get("results", [])):
        label = f"evidence.results[{index}]"
        if not isinstance(result, dict):
            errors.append(f"{label} must be an object")
            continue
        key = (result.get("stack_id"), result.get("tool"))
        if key not in gate_configs:
            errors.append(f"{label} records an unknown stack/tool tuple: {key!r}")
            continue
        if key not in blocking:
            continue  # advisory results are recorded but ignored
        collected[key].append(result)
        verify_blocking_result(label, result, key, gate_configs[key], stack_roots, root_resolved, errors)

    for key in sorted(collected):
        count = len(collected[key])
        if count != 1:
            errors.append(
                f"blocking gate {key!r} must have exactly one result, found {count}"
            )


def verify_blocking_result(label: str, result: dict, key: tuple[str, str],
                            expected_configs: list[str], stack_roots: dict[str, str],
                            root_resolved: Path, errors: list[str]) -> None:
    gate = f"blocking gate {key!r}"
    if result.get("exit_code") != 0:
        errors.append(f"{gate}: exit_code must be 0, found {result.get('exit_code')!r}")
    if result.get("timed_out"):
        errors.append(f"{gate}: timed_out must be false")
    if result.get("blocked_reason"):
        errors.append(f"{gate}: blocked_reason must be absent")

    safe_log = safe_relative_path(result.get("log"))
    if safe_log is None:
        errors.append(f"{label}: log must be a safe repository-relative path: {result.get('log')!r}")
    else:
        log_path = (root_resolved / safe_log).resolve()
        if not log_path.is_relative_to(root_resolved):
            errors.append(f"{gate}: log escapes the project root: {safe_log}")
        elif not log_path.is_file():
            errors.append(f"{gate}: log file is missing: {safe_log}")

    recorded = result.get("configs")
    if not isinstance(recorded, list):
        errors.append(f"{label}.configs must be a list")
        return

    recorded_paths: list[str] = []
    recorded_digests: dict[str, str] = {}
    for config_index, config in enumerate(recorded):
        if not isinstance(config, dict):
            errors.append(f"{label}.configs[{config_index}] must be an object")
            continue
        safe_config = safe_relative_path(config.get("path"))
        if safe_config is None:
            errors.append(
                f"{label}.configs[{config_index}].path must be a safe stack-relative path: "
                f"{config.get('path')!r}"
            )
            continue
        recorded_paths.append(safe_config)
        digest = config.get("sha256")
        if isinstance(digest, str) and digest.strip():
            recorded_digests[safe_config] = digest

    if set(recorded_paths) != set(expected_configs):
        errors.append(
            f"{gate}: recorded configs {sorted(set(recorded_paths))!r} do not match "
            f"gates configs {sorted(set(expected_configs))!r}"
        )
        return

    stack_root = stack_roots.get(key[0])
    if stack_root is None:
        return
    stack_root_path = root_resolved / stack_root
    for config_rel in expected_configs:
        recorded_digest = recorded_digests.get(config_rel)
        if recorded_digest is None:
            errors.append(f"{gate}: config {config_rel!r} has no recorded sha256")
            continue
        try:
            current_digest = sha256_file(stack_root_path / config_rel)
        except OSError as exc:
            errors.append(f"{gate}: cannot read config {config_rel!r}: {exc}")
            continue
        if current_digest != recorded_digest:
            errors.append(
                f"{gate}: config {config_rel!r} hash mismatch "
                f"(evidence {recorded_digest}, current {current_digest})"
            )


def check_waiver_policy(evidence: dict, gates: dict,
                        root: Path, change_id: str, errors: list[str]) -> None:
    disk_waivers = load_change_waivers(root, gates, change_id, errors)
    errors.extend(validate_waivers(disk_waivers, root, gates, today_iso()))

    policy = gates.get("policy") if isinstance(gates, dict) else None
    waiver_policy = policy.get("waiver") if isinstance(policy, dict) else None
    if isinstance(waiver_policy, dict):
        if waiver_policy.get("allowed") is False and disk_waivers:
            errors.append(
                "policy.waiver.allowed is false but the Change records waivers"
            )
        max_days = waiver_policy.get("max_days")
        for waiver in disk_waivers:
            if not isinstance(waiver, dict):
                continue
            approved_at = waiver.get("approved_at")
            expires_at = waiver.get("expires_at")
            if not (isinstance(approved_at, str) and isinstance(expires_at, str)):
                continue
            try:
                span_days = (date.fromisoformat(expires_at) - date.fromisoformat(approved_at)).days
            except ValueError:
                errors.append(
                    f"waiver {waiver.get('id')!r}: approved_at/expires_at are not valid dates"
                )
                continue
            if isinstance(max_days, int) and span_days > max_days:
                errors.append(
                    f"waiver {waiver.get('id')!r}: duration {span_days} days exceeds "
                    f"policy.waiver.max_days {max_days}"
                )

    applied = evidence.get("waivers_applied", [])
    if applied is None:
        applied = []
    if not isinstance(applied, list):
        errors.append("evidence.waivers_applied must be a list")
        return
    by_id = {
        waiver.get("id"): waiver
        for waiver in disk_waivers
        if isinstance(waiver, dict)
    }
    for index, entry in enumerate(applied):
        label = f"evidence.waivers_applied[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object")
            continue
        waiver_id = entry.get("id")
        current = by_id.get(waiver_id)
        if current is None:
            errors.append(f"{label}: waiver {waiver_id!r} no longer exists on disk")
            continue
        for key in WAIVER_APPLIED_KEYS:
            if entry.get(key) != current.get(key):
                errors.append(
                    f"{label} ({waiver_id}): {key} does not match the current waiver "
                    f"({entry.get(key)!r} != {current.get(key)!r})"
                )


def check_identities(evidence: dict, expect_independent: bool, strict: bool,
                     errors: list[str]) -> None:
    verifier = evidence.get("verifier_identity")
    builder = evidence.get("builder_identity")
    if strict and not (isinstance(builder, str) and builder.strip()):
        errors.append("--strict requires a non-empty builder_identity")
    if not expect_independent:
        return
    if evidence.get("independent") is not True:
        errors.append("--expect-independent requires evidence.independent to be true")
    if not (isinstance(verifier, str) and verifier.strip()):
        errors.append("--expect-independent requires a non-empty verifier_identity")
    if not (isinstance(builder, str) and builder.strip()):
        errors.append("--expect-independent requires a non-empty builder_identity")
    elif isinstance(verifier, str) and verifier.strip():
        if verifier.strip() == builder.strip():
            errors.append("--expect-independent requires verifier_identity != builder_identity")


def print_errors(errors: list[str]) -> int:
    for error in errors:
        print(f"ERROR: {error}")
    return 1


def run(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    change_id = validate_change_id(args.change)
    if not (root / "openspec" / "changes" / change_id).is_dir():
        raise ConfigError(f"Change directory is missing: openspec/changes/{change_id}")

    gates = load_gates_document(root)
    evidence_path = resolve_evidence(root, change_id, args.evidence, args.expect_independent)

    evidence_rel = evidence_path.relative_to(root).as_posix() if evidence_path.is_relative_to(root) else str(evidence_path)
    if not evidence_path.is_file():
        return print_errors([f"evidence file is missing: {evidence_rel}"])
    try:
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return print_errors([f"cannot read evidence {evidence_rel}: {exc}"])

    errors = check_required_keys(evidence, change_id)
    if errors:
        return print_errors(errors)

    current_hash = sha256_file(root / GATES_REL)
    recorded_hash = evidence["gates_file"]["sha256"]
    if recorded_hash != current_hash:
        return print_errors([
            f"{GATES_REL} drift detected: evidence records sha256 {recorded_hash} "
            f"but the current file is {current_hash}"
        ])

    check_blocking_results(evidence, gates, root, errors)
    check_waiver_policy(evidence, gates, root, change_id, errors)
    check_identities(evidence, args.expect_independent, args.strict, errors)
    if errors:
        return print_errors(errors)

    print("STATIC_ANALYSIS_CHECK_PASSED")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        return run(args)
    except ConfigError as exc:
        print(f"ERROR: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
