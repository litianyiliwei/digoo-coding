#!/usr/bin/env python3
"""Regression tests for the stage 06 requirements-coverage gate."""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

USER_STORIES = """# User Stories

- Target platforms: web

| US ID | User role | Story/value | Related FLOW/NODE/BR | AC IDs | Status | Source/approval |
|---|---|---|---|---|---|---|
| US-001 | operator | Sign in | FLOW-001 | AC-001 | APPROVED | product owner |

## Acceptance Criteria

### AC-001

- Given: a registered operator
- When: they sign in
- Then: the workspace opens
"""

AUDIT = """# UI Design Contract

## Design Source and Selection

- Design source status: APPROVED
- Design source: Design-to-HTML
- HTML provenance: AI-authored from requirements
- Target platforms: web
- PAGE list: PAGE-001
- Platform coverage: web: PAGE-001

## Design Inputs and Style References

| Item | Reference | Status |
|---|---|---|
| requirements and AC | design/user-stories.md | READ |
| design conventions | docs/architecture/frontend-conventions.md | READ |
| HTML design | design/ui-html/index.html | READ |

## Design Tokens (Actual Values)

| Variable | Type | Actual value | CSS mapping |
|---|---|---|---|
| --brand | COLOR | #0B5FFF | var(--brand) |
| --bg | COLOR | #FFFFFF | var(--bg) |
| --space | SPACING | 16px | var(--space) |

## Text Styles (Actual Values)

| Style | Font | Weight | Size | Line height | Letter spacing |
|---|---|---|---|---|---|
| Body | Noto Sans SC | 400 | 14px | 22px | 0 |
| Title | Noto Sans SC | 700 | 24px | 32px | 0 |
| Caption | Noto Sans SC | 400 | 12px | 18px | 0 |

## PAGEs and Nodes

| PAGE ID | Platform | Design source ref | Viewport/frame size | State |
|---|---|---|---|---|
| PAGE-001 Login (web) | web | `ui-html/web/PAGE-001.html` | 1440×900 | default |

## PAGE Key Specifications

### PAGE-001

- Frame: 1440×900

| Block | Element | X | Y | Width | Height |
|---|---|---|---|---|---|
| brand | PAGE-001-E01 | 0 | 0 | 600 | 900 |
| title | PAGE-001-E02 | 22 | 382 | 176 | 53 |
| form | PAGE-001-E03 | 22 | 460 | 320 | 200 |

## HTML Design Docs

- `design/ui-html/index.html`, `design/ui-html/web/PAGE-001.html`

## HTML Read Records

| Step/command | Target | Actual result | Time | Status |
|---|---|---|---|---|
| Headless render + DOM measure | `ui-html/web/PAGE-001.html` @ 1440×900 | geometry/text/font extracted for 2 assertion rows | 2026-11-25 | Success |

## Design Code

- Target framework: Vue 3 + TypeScript + Element Plus
- Design code extension: .vue
- Source: `figma-code/README.md`; transcribed from `ui-html/`.

## Assertion Scope

- `figma-layout.csv`; `check-figma-layout.py`

## State Coverage

| PAGE ID | State | Design has frame | Notes/decision |
|---|---|---|---|
| PAGE-001 | default | Yes | — |

## Requirements Coverage

| Requirement | Type | Platform | PAGE / Block | States | Coverage | Evidence / notes |
|---|---|---|---|---|---|---|
| AC-001 | AC | web | PAGE-001/PAGE-001-E01 | default | FULL | `ui-html/web/PAGE-001.html` |
| US-001 | US | web | PAGE-001 | default | FULL | derived from AC-001 |

## Asset List

- Assets: none

## Differences and Pending Confirmation

- None

## UI Review

- UI review status: APPROVED
- Reviewer: Design owner
- Review date: 2026-11-25
- Coverage review status: APPROVED
- Coverage reviewed by: Design owner / 2026-11-25
- Review evidence: `workflow/evidence/06-figma-ui-review.md`
"""

LAYOUT = """page_id,platform,viewport,route,element_id,figma_node_id,x,y,width,height,dom_selector,assert_geometry,assert_text,tolerance_px,text_content,font_size,font_weight,notes
PAGE-001,web,1440x900,/login,PAGE-001-E01,login-brand,0,0,600,900,.brand-panel,Y,N,2,,44px,700,brand panel
"""

HTML_PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><link rel="stylesheet" href="../tokens.css"></head>
<body><div class="brand-panel" data-node-id="login-brand"><h1 data-node-id="login-title">Sign in</h1></div></body></html>
"""

VUE_PAGE = """<template><div class="brand-panel" data-node-id="login-brand"><h1 data-node-id="login-title">Sign in</h1></div></template>
"""


def build_fixture(root: Path, audit: str | None = None) -> None:
    scripts = root / "scripts"
    scripts.mkdir(parents=True)
    for name in ("check-figma-audit.py", "gate_common.py"):
        shutil.copy(ROOT / "scripts" / name, scripts / name)
    design = root / "openspec/changes/demo/design"
    (design / "ui-html/web").mkdir(parents=True)
    (design / "figma-code").mkdir(parents=True)
    (design / "figma-audit.md").write_text(audit or AUDIT, encoding="utf-8")
    (design / "user-stories.md").write_text(USER_STORIES, encoding="utf-8")
    (design / "figma-layout.csv").write_text(LAYOUT, encoding="utf-8")
    (design / "ui-html/README.md").write_text("# UI design\n", encoding="utf-8")
    (design / "ui-html/index.html").write_text("<html><body><a href='web/PAGE-001.html'>PAGE-001</a></body></html>", encoding="utf-8")
    (design / "ui-html/tokens.css").write_text(":root{--brand:#0B5FFF;--bg:#FFFFFF;--space:16px;}\n", encoding="utf-8")
    (design / "ui-html/web/PAGE-001.html").write_text(HTML_PAGE, encoding="utf-8")
    (design / "figma-code/README.md").write_text("# Design code\n", encoding="utf-8")
    (design / "figma-code/PAGE-001.vue").write_text(VUE_PAGE, encoding="utf-8")
    evidence = root / "workflow/evidence"
    evidence.mkdir(parents=True)
    (evidence / "06-figma-ui-review.md").write_text("UI reviewed\n", encoding="utf-8")


def run(root: Path) -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, str(root / "scripts/check-figma-audit.py"),
         "--change", "demo", "--strict", "--require-framework"],
        capture_output=True, text=True,
    )
    return result.returncode, result.stdout + result.stderr


def main() -> int:
    failures = []
    root = Path(tempfile.mkdtemp())
    try:
        build_fixture(root)
        code, output = run(root)
        if code != 0:
            failures.append("valid fixture: expected pass, got exit %d: %s" % (code, output))
    finally:
        shutil.rmtree(root, ignore_errors=True)

    root = Path(tempfile.mkdtemp())
    try:
        audit = AUDIT.replace(
            "| AC-001 | AC | web | PAGE-001/PAGE-001-E01 | default | FULL | `ui-html/web/PAGE-001.html` |\n", ""
        )
        build_fixture(root, audit)
        code, output = run(root)
        if code == 0 or "AC-001 has no coverage row" not in output:
            failures.append("missing AC row: expected coverage failure")
    finally:
        shutil.rmtree(root, ignore_errors=True)

    root = Path(tempfile.mkdtemp())
    try:
        audit = AUDIT.replace(
            "| AC-001 | AC | web | PAGE-001/PAGE-001-E01 | default | FULL | `ui-html/web/PAGE-001.html` |",
            "| AC-001 | AC | app | PAGE-001/PAGE-001-E01 | default | FULL | `ui-html/web/PAGE-001.html` |",
        )
        build_fixture(root, audit)
        code, output = run(root)
        if code == 0 or "does not match PAGE PAGE-001 platform" not in output:
            failures.append("platform mismatch: expected coverage failure")
    finally:
        shutil.rmtree(root, ignore_errors=True)

    if failures:
        print("FIGMA_COVERAGE_FAILED")
        for failure in failures:
            print(" - " + failure)
        return 1
    print("FIGMA_COVERAGE_PASSED (3 cases)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
