# Proposal-Level User Stories and Acceptance Criteria

> Change ID: workflow-context-bundles
> Status: DRAFT (output of proposal-level requirements analysis in stage 05)
> Source: `docs/product/workflows.md` FLOW-001/NODE-001-02, `docs/product/requirements-analysis.md`, `proposal.md`, `specs/agent-context-bundles/spec.md`
> Boundary: specs are the sole source of normative behavior; this file retains scenarios, ACs, and tracking IDs without copying full specifications.
> Related IDs: RA-001, NFR-001, FLOW-001, NODE-001-02, DO-002, BR-001–004
> Generated date/version: 2026-11-17 / v0.1.0

| US ID | User role | Story/value | Related FLOW/NODE/BR | AC IDs | Status | Source/approval |
|---|---|---|---|---|---|---|
| US-001 | ROLE-002 构建 Agent | 作为构建 Agent，我希望拿到按当前阶段和 Change 裁剪、能证明来源且可复现的真实上下文文本，以减少无关输入并避免漏掉命中的约束。 | FLOW-001 / NODE-001-02 / BR-001–004 | AC-001、AC-002 | DRAFT | 用户明确要求优化节点输入输出与上下文；本 Change 待阶段 05 审核 |
| US-002 | ROLE-002 构建 Agent | 作为执行 Agent，我希望按 TASK ID 获得只包含已确认信息的执行卡，并看到缺项，以便按小任务实施而不猜测。 | FLOW-001 / NODE-001-03–04 / BR-002–004 | AC-003 | DRAFT | 用户明确要求提升 AI coding 效果；本 Change 待阶段 05 审核 |

## Acceptance Criteria

### AC-001：基于实际内容确定性裁剪

- Given：stage、Change、影响标签和可选 ID/章节有效，且权威输入来源可读
- When：请求渲染模式
- Then：只输出必需来源与命中条件的来源；manifest 为每个来源记录路径、选择原因、触发项、定位范围、SHA-256 和字符贡献；相同输入生成相同内容与来源顺序
- Coverage：未知 stage/tag/ID、路径越界、读取失败均按规范非零失败且不返回部分正文；角色权限不适用（纯本地只读 CLI，无用户数据授权决策，ROLE-002）；空选择按规范验证默认项而不静默输出空包；重复请求要求幂等；并发只读渲染无共享状态（N/A，理由：无持久写入）

### AC-002：按最终文本执行预算

- Given：实际选中来源和最终拼装文本已确定
- When：请求渲染
- Then：按 CRLF→LF 后 Unicode 码点计数，并按选中组去重计数；默认上限为 8 组和 12,000 字符；超限无有效批准例外时返回 OVER_BUDGET、指标和最大贡献来源，正文为空
- Coverage：0 字符/正好上限/超 1 字符、8/9 组边界均验证；有效例外必须 Change 绑定、额度覆盖且可追溯；例外撤销/无效/额度不足均失败关闭；重复执行结果稳定；并发读取不修改状态（N/A，纯本地只读）

### AC-003：TASK ID 执行卡不猜测

- Given：TASK ID 存在于当前 Change 的 tasks.md
- When：同时请求执行卡
- Then：从权威任务、关联 AC、已批准设计和验证约定提取字段；无法追溯的字段显示明确待补齐标记并进入 `missing_fields`；不存在的 TASK ID 非零失败
- Coverage：缺 AC、设计未批准、缺路径或命令分别保留待补齐状态；不生成推测路径或检查；无权限差异（ROLE-002）；任务 ID 空/重复输入按解析规则拒绝或确定处理；不涉及离线、推送、设备权限（N/A：本地开发 CLI，无网络或设备场景）

## Discovery decisions

- 问题 1：当前工具是否仅列清单还是确实输出送入 Agent 的内容？答：输出实际正文；落点：AC-001/spec。
- 问题 2：预算应统计原始文件还是拼装后内容？答：统计规范化后的最终正文，并独立计算读取组；落点：AC-002/spec。
- 问题 3：条件材料怎样避免重复配置漂移？答：阶段输入与触发规则须归入唯一权威配置；落点：design.md/spec。
- 问题 4：任务设计缺失时可否从 TASK 标题推断？答：不可以，必须显示待补齐状态；落点：AC-003/spec。
- Alternative：只扩充清单和估算，改动最少；拒绝，因为无法证明模型实际收到的正文及其字符预算；落点：design.md。
- Decision：增加 fail-closed 的真实渲染 JSON 模式，兼容现有清单/审计模式；落点：proposal.md、design.md、spec。
