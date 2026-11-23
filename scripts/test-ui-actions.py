#!/usr/bin/env python3
"""Regression tests for the stage 07 UI action checker."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECKER = Path(__file__).with_name("check-ui-actions.py")
CHANGE = "demo-change"

ACTIONS_HEADER = (
    "page_id,element_id,figma_node_id,element_type,label,event,action_type,"
    "route,route_params,operation_id,handler,test_id,confirmation,approver,"
    "confirmed_at,notes\n"
)
ACTIONS_VALID = ACTIONS_HEADER + (
    "PAGE-001,PAGE-001-E06,3:17,button,登录,click,navigate,/dashboard,NONE,,"
    "handleLogin,TEST-001,N/A,,,登录成功后跳转首页\n"
    "PAGE-002,PAGE-002-E10,5:10,icon,帮助,click,api,,,help.getContent,"
    "showHelp,TEST-002,N/A,,,帮助图标调用内容接口\n"
)
LAYOUT_VALID = (
    "page_id,element_id,figma_node_id,dom_selector,notes\n"
    "PAGE-001,PAGE-001-E06,3:17,.login-button,登录按钮\n"
    "PAGE-001,PAGE-001-E05,3:12,.account-input,账号输入容器\n"
    "PAGE-002,PAGE-002-E10,5:10,.help-icon,帮助图标\n"
)
OPENAPI_VALID = """openapi: 3.0.0
info:
  title: Demo
  version: 1.0.0
paths:
  /help:
    get:
      operationId: help.getContent
"""
TEST_CASES_VALID = "test_id,title\nTEST-001,登录跳转\nTEST-002,帮助内容\n"
PAGE_ONE_CODE = """<template>
  <el-button data-node-id="3:17" @click="handleLogin">登录</el-button>
</template>
"""
PAGE_TWO_CODE = """<template>
  <el-icon data-node-id="5:10" @click="showHelp"><QuestionFilled /></el-icon>
</template>
"""
AUDIT_VALID = """# Figma Design Contract

- Design source status: APPROVED
- Design source selection: Figma MCP AI automatic design
"""


def run_checker(root: Path, *, strict: bool = True) -> subprocess.CompletedProcess:
    command = [sys.executable, str(CHECKER), "--change", CHANGE, "--root", str(root)]
    if strict:
        command.append("--strict")
    return subprocess.run(command, capture_output=True, text=True)


def write_change(
    root: Path,
    *,
    actions: str = ACTIONS_VALID,
    layout: str = LAYOUT_VALID,
    openapi: str = OPENAPI_VALID,
    page_one: str = PAGE_ONE_CODE,
    page_two: str = PAGE_TWO_CODE,
    audit: str = AUDIT_VALID,
    test_cases: str = TEST_CASES_VALID,
) -> Path:
    change = root / "openspec/changes" / CHANGE
    design = change / "design"
    design.mkdir(parents=True)
    if actions is not None:
        (design / "ui-actions.csv").write_text(actions, encoding="utf-8")
    if layout is not None:
        (design / "figma-layout.csv").write_text(layout, encoding="utf-8")
    if openapi is not None:
        (change / "api").mkdir()
        (change / "api/openapi.yaml").write_text(openapi, encoding="utf-8")
    if test_cases is not None:
        (design / "test-cases.csv").write_text(test_cases, encoding="utf-8")
    code = design / "figma-code"
    code.mkdir()
    if page_one is not None:
        (code / "PAGE-001.vue").write_text(page_one, encoding="utf-8")
    if page_two is not None:
        (code / "PAGE-002.vue").write_text(page_two, encoding="utf-8")
    if audit is not None:
        (design / "figma-audit.md").write_text(audit, encoding="utf-8")
    return change


class UiActionsTests(unittest.TestCase):
    def test_valid_mapping_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_change(Path(tmp))
            result = run_checker(Path(tmp))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("UI action check passed", result.stdout)

    def test_missing_action_type_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_change(Path(tmp), actions=ACTIONS_VALID.replace(",navigate,/dashboard", ",,/dashboard"))
            result = run_checker(Path(tmp))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("navigation/API mapping", result.stdout)

    def test_navigate_requires_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_change(Path(tmp), actions=ACTIONS_VALID.replace(",navigate,/dashboard", ",navigate,"))
            result = run_checker(Path(tmp))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("concrete route", result.stdout)

    def test_navigate_requires_params(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_change(Path(tmp), actions=ACTIONS_VALID.replace("navigate,/dashboard,NONE", "navigate,/dashboard,"))
            result = run_checker(Path(tmp))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("route_params", result.stdout)

    def test_api_operation_must_exist_in_openapi(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_change(Path(tmp), actions=ACTIONS_VALID.replace("help.getContent", "help.missing"))
            result = run_checker(Path(tmp))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not defined in api/openapi.yaml", result.stdout)

    def test_local_only_requires_user_confirmation(self):
        with tempfile.TemporaryDirectory() as tmp:
            row = (
                "PAGE-001,PAGE-001-E06,3:17,button,登录,click,local-only,,,,"
                "handleLogin,TEST-001,PENDING,,,仅本地刷新列表\n"
            )
            write_change(Path(tmp), actions=ACTIONS_HEADER + row)
            result = run_checker(Path(tmp))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("prompt the user to confirm", result.stdout)

    def test_local_only_confirmed_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            row = (
                "PAGE-001,PAGE-001-E06,3:17,button,登录,click,local-only,,,,"
                "handleLogin,TEST-001,CONFIRMED,产品负责人,2026-11-20,仅本地刷新列表\n"
            )
            layout = (
                "page_id,element_id,figma_node_id,dom_selector,notes\n"
                "PAGE-001,PAGE-001-E06,3:17,.login-button,登录按钮\n"
            )
            write_change(
                Path(tmp), actions=ACTIONS_HEADER + row, layout=layout, page_two=None
            )
            result = run_checker(Path(tmp))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_interactive_layout_element_must_be_inventoried(self):
        with tempfile.TemporaryDirectory() as tmp:
            layout = LAYOUT_VALID + "PAGE-003,PAGE-003-E03,7:9,.export-button,导出按钮\n"
            write_change(Path(tmp), layout=layout)
            result = run_checker(Path(tmp))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("looks interactive but has no ui-actions.csv row", result.stdout)

    def test_design_code_controls_must_be_inventoried(self):
        with tempfile.TemporaryDirectory() as tmp:
            code = """<template>
  <el-button data-node-id="3:17" @click="handleLogin">登录</el-button>
  <el-button data-node-id="3:18" @click="openDialog">忘记密码</el-button>
</template>
"""
            write_change(Path(tmp), page_one=code)
            result = run_checker(Path(tmp))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("interactive control(s)", result.stdout)

    def test_unknown_test_id_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_change(Path(tmp), actions=ACTIONS_VALID.replace("TEST-001", "TEST-999"))
            result = run_checker(Path(tmp))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("not registered in design/test-cases.csv", result.stdout)

    def test_no_ui_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_change(
                Path(tmp),
                actions=None,
                layout=None,
                openapi=None,
                page_one=None,
                page_two=None,
                test_cases=None,
                audit="- Design source status: N/A\n- Reason for no UI: backend-only Change\n",
            )
            result = run_checker(Path(tmp))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_no_ui_declaration_overrides_copied_templates(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_change(
                Path(tmp),
                audit="- Design source status: N/A\n- Reason for no UI: backend-only Change\n",
            )
            result = run_checker(Path(tmp))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("N/A", result.stdout)

    def test_ui_change_requires_ui_actions_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            write_change(Path(tmp), actions=None)
            result = run_checker(Path(tmp))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing ui-actions.csv", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
