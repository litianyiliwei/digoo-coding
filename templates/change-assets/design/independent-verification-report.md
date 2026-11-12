# 独立验证报告

- Change ID：
- 验证者（Agent/人员/独立会话 ID）：
- Builder（Agent/人员/会话 ID）：
- 验证时间：
- 判定：PASS / FAIL / BLOCKED
- 被测 Revision（commit 或 diff fingerprint）：
- 验证期间 Revision 是否保持不变：YES / NO
- 只读约束是否遵守：YES / NO

## 1. 验证范围与输入版本

| 输入 | 路径/版本 | 已读取 | 审批状态 |
|---|---|---|---|
| OpenSpec proposal/specs/design/tasks | | | |
| baseline-impact 与 baseline version | | | |
| OpenAPI / API-IO / IO catalog | | | |
| 前后端详细设计 / 测试设计 | | | |

## 2. 验收标准逐项验证

| AC ID | 预期行为 | 验证方法 | 证据路径/测试 | 结果 PASS/FAIL/NOT_RUN |
|---|---|---|---|---|

## 3. 测试与检查执行证据

| 命令 | 退出码 | 结果 | 日志/报告路径 |
|---|---:|---|---|

## 4. 契约与工程约束检查

- API → IO 映射：
- IO 契约/事务/幂等/异常：
- 数据迁移与兼容性：
- 权限/安全/隐私：
- 基线约束：
- OpenSpec tasks：

## UI 一致性验证（涉及 UI 时必须）

> 逐 PAGE 使用独立重跑的运行态几何断言 `evidence/figma-layout-check.json`；不使用截图。
> `layout_checks` 必须与本文表格一致；任 PAGE 缺失证据、超差或有未批准差异时 Verdict 不得 PASS。

| PAGE | Figma node | 断言元素数 | 最大偏差 | 缺失/差异 | 判定 |
|---|---|---|---|---|---|
| PAGE-001 | `3:2` | 8 | 0.0px / tol 2px | 无 | PASS/FAIL/NOT_RUN |

## 5. 发现项

| ID | 严重程度 | 描述 | 复现步骤/证据 | 责任阶段 |
|---|---|---|---|---|

## 6. 未执行项与限制

| 检查项 | 未执行原因 | 是否阻断 |
|---|---|---|

## 7. 最终判定

- Verdict：PASS / FAIL / BLOCKED
- 允许进入人工验收：YES / NO
- 退回阶段及修复要求：
- 验证者说明：
