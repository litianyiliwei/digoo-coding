#!/usr/bin/env python3
"""Regression tests for the stage 02 reference-research checker."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CHECKER = Path(__file__).with_name("check-reference-research.py")

VALID = """# 参考产品与互联网调研

- Change ID：N/A（项目级）
- 状态：DRAFT
- 来源基线：用户访谈、参考产品资料、互联网公开信息
- 关联需求/AC：FLOW-001
- 调研日期：2026-11-13
- 调研执行人：业务分析

## 1. 研究范围与问题

| Q ID | 研究问题 | 为什么重要 | 对应的业务域/FLOW |
|---|---|---|---|
| RQ-001 | 同类产品如何组织种植档案？ | 决定数据对象边界 | FLOW-001 |
| RQ-002 | 同类产品如何处理离线记录？ | 决定同步与冲突策略 | FLOW-002 |
| RQ-003 | 监管溯源需要哪些字段？ | 决定合规数据模型 | FLOW-003 |

## 2. 参考产品清单

- 参考产品状态：PRESENT
- 无参考产品理由（状态为 NONE 时必填）：N/A

| 产品/方案 | 类型（同类/相邻/替代） | 获取方式（官网/文档/试用/截图/用户提供） | 链接 | 调研日期 | 备注 |
|---|---|---|---|---|---|
| 示例农事管理产品 | 同类 | 官网 | https://example.com/product | 2026-11-13 | 公开功能页 |

## 3. 研究记录

| 序号 | 调研问题 | 使用的工具/方式 | 查询词或来源 | URL | 访问日期 | 关键发现 |
|---|---|---|---|---|---|---|
| 1 | 种植档案组织方式 | WebSearch | 智慧农业 种植档案 | https://example.com/a | 2026-11-13 | 以地块为中心组织 |
| 2 | 离线记录与同步 | WebSearch | 农业 App 离线 | https://example.com/b | 2026-11-13 | 本地队列后同步 |
| 3 | 监管溯源字段 | WebFetch | 溯源平台公开说明 | https://example.com/c | 2026-11-13 | 需要批次与投入品记录 |

## 4. 对比与借鉴

| 对比项 | 参考产品做法 | 本项目候选做法 | 采纳/不采纳 | 理由 | 关联 FLOW/DO/BR |
|---|---|---|---|---|---|
| 档案组织 | 以地块为中心 | 以地块为中心 | 采纳 | 符合业务对象 | FLOW-001 |
| 离线策略 | 本地队列 | 本地队列 + 冲突提示 | 部分采纳 | 需要弱网可用 | FLOW-002 |

## 5. 结论与假设

- 可借鉴结论：地块中心档案与本地队列同步。
- 新增/更新假设（ASM-001）：农户允许先离线记录后同步。

## 6. 影响映射

| 研究结论 | 影响对象（FLOW/NODE/DO/BR/NFR） | 影响方式（新增/修改/无影响） | 处理状态 |
|---|---|---|---|
| 地块中心档案 | FLOW-001 | 修改 | 已登记 |
| 离线同步 | FLOW-002 | 新增 | 已登记 |

## 7. 未决问题

| Q ID | 问题 | 负责人 | 截止/阻塞条件 |
|---|---|---|---|
| Q-001 | 离线冲突的默认策略 | 业务负责人 | 阶段 05 前 |

## 8. 来源与审批

- 调研日期：2026-11-13
- 调研执行人：业务分析
- 来源可信度/限制：公开资料，需用户确认
- 产品/业务负责人：待评审
- 审批状态：DRAFT
"""


def run_checker(text: str) -> subprocess.CompletedProcess:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "docs/product").mkdir(parents=True, exist_ok=True)
        (root / "docs/product/reference-research.md").write_text(text, encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(CHECKER), "--root", str(root), "--strict"],
            capture_output=True,
            text=True,
        )


class ReferenceResearchTests(unittest.TestCase):
    def test_valid_research_passes(self):
        result = run_checker(VALID)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_requires_three_sources(self):
        text = VALID.replace("https://example.com/b", "https://example.com/a")
        result = run_checker(text)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("3 distinct source URLs", result.stdout)

    def test_requires_reference_product_status(self):
        text = VALID.replace("- 参考产品状态：PRESENT", "")
        result = run_checker(text)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("参考产品状态", result.stdout)

    def test_none_status_requires_reason(self):
        text = VALID.replace("- 参考产品状态：PRESENT", "- 参考产品状态：NONE")
        result = run_checker(text)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("无参考产品理由", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
