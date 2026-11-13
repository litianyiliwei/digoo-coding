#!/usr/bin/env python3
"""Regression tests for scripts/check-interface-catalog.py."""
from __future__ import annotations

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check-interface-catalog.py"
CATALOG_HEADER = [
    "interface_id", "interface_type", "source", "target", "protocol", "operation",
    "input_contract", "output_contract", "auth", "error_semantics", "timeout_ms",
    "retry_policy", "idempotency", "versioning", "test_ids", "owner", "notes",
]


def write_csv(path: Path, header: list[str], rows: list[list[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header)
        for row in rows:
            w.writerow(row)


def run(root: Path, change: str, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--change", change, "--root", str(root), *extra],
        capture_output=True, text=True,
    )


def build_fixture(root: Path) -> Path:
    change = root / "openspec" / "changes" / "demo-change"
    write_csv(
        change / "design" / "interface-catalog.csv",
        CATALOG_HEADER,
        [["IF-API-001", "HTTP_API", "前端", "后端", "HTTPS", "listThings", "{}", "{}", "token",
          "{code,message}", "5000", "0", "yes", "v1", "TEST-001", "后端负责人", ""]],
    )
    write_csv(change / "design" / "test-cases.csv", ["test_id", "interface_ids"], [["TEST-001", "IF-API-001"]])
    write_csv(
        change / "traceability.csv",
        ["source_type", "source_id", "target_type", "target_id", "relationship", "status", "evidence", "notes"],
        [["INTERFACE", "IF-API-001", "AC", "AC-001", "implements", "planned", "design.md", ""]],
    )
    (change / "api").mkdir(parents=True, exist_ok=True)
    (change / "api" / "openapi.yaml").write_text(
        "openapi: 3.1.0\ninfo:\n  title: demo\n  version: '1'\n"
        "x-api-scope: defined\npaths:\n  /things:\n    get:\n      operationId: listThings\n",
        encoding="utf-8",
    )
    (change / "design.md").write_text(
        "## 接口设计\n\n### 接口边界清单\n\n见 interface-catalog.csv。\n\n"
        "### 契约与错误语义\n\n### 接口追踪\n",
        encoding="utf-8",
    )
    return change


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        change = build_fixture(root)
        ok = run(root, "demo-change", "--strict")
        if ok.returncode != 0:
            failures.append("valid fixture should pass: " + ok.stdout + ok.stderr)

        # HTTP operation mismatch must fail.
        (change / "api" / "openapi.yaml").write_text(
            "openapi: 3.1.0\ninfo:\n  title: demo\n  version: '1'\n"
            "x-api-scope: defined\npaths:\n  /things:\n    get:\n      operationId: otherThing\n",
            encoding="utf-8",
        )
        bad = run(root, "demo-change", "--strict")
        if bad.returncode == 0 or "not found in OpenAPI" not in bad.stdout:
            failures.append("HTTP operation mismatch should fail: " + bad.stdout)

        # Restore OpenAPI, remove the test-case reference; interface coverage must fail.
        (change / "api" / "openapi.yaml").write_text(
            "openapi: 3.1.0\ninfo:\n  title: demo\n  version: '1'\n"
            "x-api-scope: defined\npaths:\n  /things:\n    get:\n      operationId: listThings\n",
            encoding="utf-8",
        )
        write_csv(
            change / "design" / "interface-catalog.csv",
            CATALOG_HEADER,
            [["IF-API-001", "HTTP_API", "前端", "后端", "HTTPS", "listThings", "{}", "{}", "token",
              "{code,message}", "5000", "0", "yes", "v1", "TEST-002", "后端负责人", ""]],
        )
        write_csv(change / "design" / "test-cases.csv", ["test_id", "interface_ids"], [["TEST-002", ""]])
        bad_test = run(root, "demo-change", "--strict")
        if bad_test.returncode == 0 or "no test-cases.csv row references" not in bad_test.stdout:
            failures.append("missing interface test coverage should fail: " + bad_test.stdout)

        # Native requirement must fail without a NATIVE_BRIDGE row.
        native = run(root, "demo-change", "--strict", "--require-native")
        if native.returncode == 0 or "no NATIVE_BRIDGE row" not in native.stdout:
            failures.append("--require-native should fail without a bridge row: " + native.stdout)

        # Add a native bridge row with test and traceability; --require-native must pass.
        write_csv(
            change / "design" / "interface-catalog.csv",
            CATALOG_HEADER,
            [
                ["IF-API-001", "HTTP_API", "前端", "后端", "HTTPS", "listThings", "{}", "{}", "token",
                 "{code,message}", "5000", "0", "yes", "v1", "TEST-002", "后端负责人", ""],
                ["IF-NATIVE-001", "NATIVE_BRIDGE", "uni-app(Android)", "Android 原生插件", "JS Bridge",
                 "getLocation", "{accuracy}", "{lat,lng,code}", "permission", "{code,message}",
                 "5000", "1", "yes", "plugin 1.x / app 1.x", "TEST-003", "移动端负责人", ""],
            ],
        )
        write_csv(change / "design" / "test-cases.csv", ["test_id", "interface_ids"],
                  [["TEST-002", "IF-API-001"], ["TEST-003", "IF-NATIVE-001"]])
        write_csv(
            change / "traceability.csv",
            ["source_type", "source_id", "target_type", "target_id", "relationship", "status", "evidence", "notes"],
            [["INTERFACE", "IF-API-001", "AC", "AC-001", "implements", "planned", "design.md", ""],
             ["INTERFACE", "IF-NATIVE-001", "AC", "AC-002", "implements", "planned", "design.md", ""]],
        )
        native_ok = run(root, "demo-change", "--strict", "--require-native")
        if native_ok.returncode != 0:
            failures.append("--require-native should pass with a bridge row: " + native_ok.stdout + native_ok.stderr)

        # A design that mentions third-party interfaces must have a THIRD_PARTY_API row.
        (change / "design.md").write_text(
            "## 接口设计\n\n### 接口边界清单\n\n依赖第三方天气 API，见 interface-catalog.csv。\n\n"
            "### 契约与错误语义\n\n### 接口追踪\n",
            encoding="utf-8",
        )
        third = run(root, "demo-change", "--strict")
        if third.returncode == 0 or "THIRD_PARTY_API" not in third.stdout:
            failures.append("third-party mention without catalog row should fail: " + third.stdout)

    if failures:
        for failure in failures:
            print("FAIL:", failure)
        return 1
    print("Interface catalog regression tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
