#!/usr/bin/env python3
"""Regression tests for the output-template matrix checker.

Each case builds a throwaway repository root (checker copied into its
scripts/ directory, matrix under process/), runs the checker as a
subprocess, and asserts the exit status and the diagnostic message.
"""
import csv, shutil, subprocess, sys, tempfile
from pathlib import Path

SCRIPT = Path(__file__).with_name("check-output-template-matrix.py")
HEADER = ["phase", "output_name", "template_level", "template_path",
          "required_traceability", "validator_or_gate", "notes", "applicability"]


def row(template_path: str, name: str = "case") -> dict:
    return {
        "phase": "Requirements business analysis",
        "output_name": name,
        "template_level": "L1",
        "template_path": template_path,
        "required_traceability": "BR → FLOW/NODE",
        "validator_or_gate": "human review",
        "notes": "fixture",
        "applicability": "always",
    }


def run_case(rows: list[dict], files: list[str]) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "scripts").mkdir()
        shutil.copy(SCRIPT, root / "scripts" / SCRIPT.name)
        (root / "process").mkdir()
        with (root / "process" / "OUTPUT-TEMPLATE-MATRIX.csv").open(
            "w", newline="", encoding="utf-8"
        ) as stream:
            writer = csv.DictWriter(stream, fieldnames=HEADER)
            writer.writeheader()
            writer.writerows(rows)
        for rel in files:
            path = root / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("# fixture\n", encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(root / "scripts" / SCRIPT.name)],
            capture_output=True, text=True,
        )


def main() -> int:
    failures: list[str] = []

    docs = run_case([row("docs/product/business-rules.md")], ["docs/product/business-rules.md"])
    if docs.returncode == 0 or "project-instance path is not a template" not in docs.stdout + docs.stderr:
        failures.append("docs path should be rejected as a template: " + (docs.stdout + docs.stderr))

    missing = run_case([row("templates/product/missing.md")], [])
    if missing.returncode == 0 or "does not exist" not in missing.stdout + missing.stderr:
        failures.append("missing template path should be rejected: " + (missing.stdout + missing.stderr))

    process_ref = run_case([row("process/INPUT-OUTPUT-POLICY.md")], ["process/INPUT-OUTPUT-POLICY.md"])
    if process_ref.returncode != 0:
        failures.append("process reference should be allowed: " + (process_ref.stdout + process_ref.stderr))

    valid_rows = [
        row("templates/product/x.md", "valid template"),
        row("OpenSpec built-in schema: proposal.md", "openspec builtin"),
    ]
    valid = run_case(valid_rows, ["templates/product/x.md"])
    if valid.returncode != 0:
        failures.append("valid templates should pass: " + (valid.stdout + valid.stderr))

    if failures:
        for failure in failures:
            print("FAIL:", failure)
        return 1
    print("Output-template matrix regression tests passed (4 cases).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
