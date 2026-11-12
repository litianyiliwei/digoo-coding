# 阶段交接报告

- 阶段 ID：
- Skill：
- Change ID（项目级填 N/A）：
- 执行时间：
- 状态：DRAFT / BLOCKED / READY_FOR_REVIEW / APPROVED

## 1. 实际读取的输入

| 文件/资源 | 存在 | 版本/更新时间 | 审批状态 | 与本阶段相关性 |
|---|---|---|---|---|
| | | | | |

## 2. 本阶段输出

| 输出文件 | 已创建/修改/未生成 | 核心内容摘要 | 下游用途 |
|---|---|---|---|
| | | | |

## 3. 追踪关系与覆盖情况

- 上游需求/故事/AC：
- 本阶段产物 ID：
- 下游消费关系：
- UI 一致性（涉及 UI）：`figma-code/` / `figma-layout.csv` 断言覆盖、`figma-layout-check.json` 最大偏差与差异结论（路径与结论；不使用截图）
- 未覆盖/不适用项及理由：

## 4. 自检与工具执行证据

| 命令/工具 | 实际执行 | 退出码/结果 | 证据/日志位置 |
|---|---|---|---|
| | | | |

## 5. 待确认、风险与阻断

- 待审批：
- 阻断项：
- 假设/冲突：
- 未执行项（含原因）：


## 6. 基线适用性与变更交接

- 当前基线版本/状态：
- 本阶段读取的基线域/文件/章节：
- 本 Change 的基线分类：CHANGE_ONLY / BASELINE_CHANGE_REQUIRED / BASELINE_UPDATE_AFTER_ACCEPTANCE / N/A
- 当前结论：COMPATIBLE / BLOCKED_PENDING_BASELINE_CHANGE / APPROVED_BASELINE_AMENDMENT
- 复核结论：NO_IMPACT / REBASE_REQUIRED / N/A
- BCR / ADR 路径与审批状态：
- 需要更新的基线文件及版本（无则写 N/A）：
- 受影响的在途 Change：

## 7. 下一阶段交接

- 下一阶段：
- 下一阶段必须读取：
- UI 证据（涉及 UI）：`design/figma-audit.md`、`design/figma-code/`、`design/figma-layout.csv`、`design/evidence/figma-layout-check.json`、`code-review.md` 的数值 UI fidelity / `layout_checks` / `UI acceptance`（不使用截图）
- 输入完整性：PASS / FAIL
- 是否允许推进：YES / NO
- 需要用户确认的问题：

> 只有真实产物存在、门禁通过且所需审批完成，才能将本阶段记入 `workflow-state.json.completed_steps`。
