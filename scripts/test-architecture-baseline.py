#!/usr/bin/env python3
"""Regression tests for scripts/check-architecture-baseline.py."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check-architecture-baseline.py"


def write_fixture(root: Path) -> None:
    arch = root / "docs" / "architecture"
    arch.mkdir(parents=True, exist_ok=True)
    (arch / "technology-decisions.md").write_text(
        "# 技术选型\n\n## 1. 技术选型访谈记录\n\n- 后端：Java\n\n"
        "## 现有系统二开约束\n\n基于现有系统二开；代码地址：https://example/repo；分支：main；commit：abc123。\n\n"
        "## 第三方接口依赖清单\n\n| 接口 | 提供方 | 协议 | 鉴权 |\n|---|---|---|---|\n| 天气 | 气象平台 | HTTPS | API Key |\n",
        encoding="utf-8",
    )
    (arch / "api-conventions.md").write_text(
        "# API 契约规范\n\n## 第三方接口与集成约定\n\n- 天气 API：HTTPS、API Key、超时 3000ms。\n",
        encoding="utf-8",
    )
    (arch / "data-flows.md").write_text(
        "# 数据流\n\n| DF ID | 数据流 | 触发 | 同步/异步 |\n|---|---|---|---|\n| DF-001 | 第三方天气查询 | 定时任务 | 同步 |\n",
        encoding="utf-8",
    )
    (arch / "constraint-registry.json").write_text(
        json.dumps({"constraints": [
            {"id": "LEGACY-001", "status": "DRAFT"},
            {"id": "EXT-001", "status": "DRAFT"},
        ]}, ensure_ascii=False), encoding="utf-8",
    )


def run(root: Path, *extra: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CHECKER), "--root", str(root), *extra],
        capture_output=True, text=True,
    )


def main() -> int:
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        write_fixture(root)
        ok = run(root, "--strict")
        if ok.returncode != 0:
            failures.append("valid fixture should pass: " + ok.stdout + ok.stderr)

        registry = root / "docs" / "architecture" / "constraint-registry.json"
        registry.write_text(json.dumps({"constraints": [{"id": "EXT-001"}]}, ensure_ascii=False), encoding="utf-8")
        missing_legacy = run(root, "--strict")
        if missing_legacy.returncode == 0 or "LEGACY-*" not in missing_legacy.stdout:
            failures.append("missing LEGACY constraint should fail: " + missing_legacy.stdout)

        write_fixture(root)
        tech = root / "docs" / "architecture" / "technology-decisions.md"
        tech.write_text("# 技术选型\n\n## 1. 技术选型访谈记录\n\n- 后端：Java\n", encoding="utf-8")
        missing_section = run(root, "--strict")
        if missing_section.returncode == 0 or "现有系统二开约束" not in missing_section.stdout:
            failures.append("missing existing-system section should fail: " + missing_section.stdout)

        write_fixture(root)
        tech.write_text(
            "# 技术选型\n\n## 1. 技术选型访谈记录\n\n- 后端：Java\n\n"
            "## 现有系统二开约束\n\nN/A（新系统，无现有代码）\n\n"
            "## 第三方接口依赖清单\n\nNONE（本阶段无第三方接口）\n",
            encoding="utf-8",
        )
        (root / "docs" / "architecture" / "api-conventions.md").write_text("# API\n", encoding="utf-8")
        (root / "docs" / "architecture" / "data-flows.md").write_text("# 数据流\n", encoding="utf-8")
        registry.write_text(json.dumps({"constraints": []}, ensure_ascii=False), encoding="utf-8")
        none_ok = run(root, "--strict")
        if none_ok.returncode != 0:
            failures.append("explicit N/A / NONE should pass: " + none_ok.stdout)

    if failures:
        for failure in failures:
            print("FAIL:", failure)
        return 1
    print("Architecture baseline regression tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
