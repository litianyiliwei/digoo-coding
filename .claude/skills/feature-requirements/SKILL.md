---
name: feature-requirements
description: 提案级需求分析。按 Change 生成用户故事与 AC，并细化为可测试的 OpenSpec 行为规格；不产出独立用例文件，场景写入 spec 的 Scenario。
---

# 提案级需求分析

## 何时使用
当流程进入“提案级需求分析”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
Change ID、已批准路线图、项目需求业务梳理（FLOW/NODE/DO/RD/BR/验收政策）、`BASELINE-BRIEF.md`/`change-sizing.md`/`role-permission-matrix.csv`/`decisions.md`/`assumptions.md`/`lessons.md`/`id-conventions.md`（常驻基线）、open-questions（只读）、冻结基线、相关 openspec/specs。

## 执行流程
1. 先运行 `openspec status --change <id>`、`openspec list --specs` 并读取相关规格全文；遵循当前 OpenSpec CLI/Schema 指引。
2. 从项目业务流程、RD 矩阵与 Change 范围推导**提案级用户故事与 AC**（`design/user-stories.md`，US/AC ID）；不得复制项目级历史故事清单，只保留与本 Change 相关的条目并保持稳定 ID。specs 是规范行为的唯一来源，场景写在 spec 的 Scenario 中；user-stories 只写 US、AC 与追踪 ID，不复制完整规格。
3. 每个用户场景必须写清触发、角色、前置条件、主流程、替代/异常流程、后置条件，并引用项目 FLOW/NODE/DO/BR ID；场景正文写入 `specs/<capability>/spec.md` 的 Scenario，不单独产出 `design/use-cases.md`，也不使用 UC ID 做追踪。
4. 每个 US 写可验证的 Given/When/Then；每个关键故事至少一个 AC，覆盖权限、空值、边界、异常、重复提交和并发（适用时）。涉及多端/原生/设备的 Change，场景还必须覆盖平台权限（拒绝/降级）、离线/弱网、推送/深链、多端差异、失败重试、幂等/并发；不适用写 N/A + 理由。
5. 完善 `proposal.md` 的 Why、What Changes、Capabilities、Impact；capability 路径使用 kebab-case 并复用既有路径。
6. 把外部可观察行为写入 `specs/<capability>/spec.md`，使用规范的 ADDED/MODIFIED/REMOVED/RENAMED Requirements 和 Scenario。
7. 把实现方法放进 `design.md`，任务只放进带复选框的 `tasks.md`。
8. 标注对应 US/AC/BR/FLOW/NODE/DO ID、权限、失败路径、边界条件。
9. 超出基线范围时先提出 ADR/基线变更；无行为变化的纯文档/重构 Change 按 OpenSpec 约定使用 `skip_specs: true`，不能伪造需求。
10. 完成后执行 `python scripts/check-requirements.py --change <change-id> --strict` 与 `openspec validate <change-id> --strict`，处理所有错误/警告。

## 输出
OpenSpec proposal、delta specs、design、tasks、`design/user-stories.md`、`design/baseline-impact.md`、`design/baseline-binding.json`、基线修订请求（条件适用）和待审批清单。

## 质量与安全边界
规格描述 WHAT，不夹带类名/框架等实现细节；每条 Requirement 至少有一个 Scenario；tasks 使用 `- [ ]`；提案级 US/AC 必须引用项目 FLOW/BR/DO 且能被 AC 验证；不产出用例文件，场景统一写在 spec 的 Scenario。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- Figma MCP 的输入必须基于实际可访问的链接、节点和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/check-requirements.py --change <change-id> --strict`；`scripts/check-change.sh <change-id>`


## 实际工具调用要求

- **Superpowers：** `brainstorming` 的 stage-scoped 模式检查方案、需求边界与多端场景完整性；结论写入 `design/user-stories.md`、spec 的 Scenario 或 `design.md`，不另写独立设计文档；不得开始编码。阶段 evidence 必须写 `methods`（至少 3 个问题、1 个备选、1 个决策）并运行 `python scripts/check-method-evidence.py --step 05-feature-requirements --evidence <evidence.json>`。必须按当前宿主 Agent 的真实机制检查、读取或调用技能；不可用时用 `mode=equivalent` 并写 `reason`。
- **OpenSpec：** 真实执行 `openspec status --change <id>`、`openspec instructions <artifact> --change <id> --json`、`openspec validate <id> --strict`。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 项目基线读取与适用性判定（强制）

- 开始需求细化前，先读取 `docs/architecture/baseline-status.md`、相关产品基线、`system-context.md`、`domain-boundaries.md` 及受影响域的架构/数据/API/前端/测试基线，并读取相关 `openspec/specs/**`。
- 必须按 `templates/change-assets/design/baseline-impact.md` 创建 `openspec/changes/<change-id>/design/baseline-impact.md`，记录基线域版本、实际读取文件/章节/ID、约束、复用项、冲突和归属分类。
- 在 `proposal.md` / `design.md` 说明基线影响。若架构、数据所有权、公共契约或全局质量门禁的变更是功能成立的前提，标记 `BLOCKED_PENDING_BASELINE_CHANGE`；先完成基线修订审批，不能先设计/编码后补手续。
- 单个功能的行为、API、页面、物理表迁移和局部 IO 留在 Change；只有跨功能共享规则/公共契约/核心领域模型/系统级约束才提出基线修订。
- 详细判定规则见 `docs/BASELINE-FEATURE-INTERACTION.md`。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="feature-requirements"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** 已批准路线图/当前 Change 范围；项目需求业务梳理（workflows/data-objects/rd-matrix/business-rules/glossary/acceptance-policy）与冻结基线；docs/product/BASELINE-BRIEF.md、change-sizing.md、role-permission-matrix.csv、decisions.md、assumptions.md、lessons.md、id-conventions.md（常驻基线）；docs/product/acceptance-policy.md（项目级验收口径；AC 与验收政策对齐）；关联 FLOW/NODE/DO/BR ID；现有 OpenSpec specs；docs/product/open-questions.md（只读）。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** openspec/changes/<change-id>/proposal.md；openspec/changes/<change-id>/specs/<capability>/spec.md（适用时）；openspec/changes/<change-id>/tasks.md（初步任务）；openspec/changes/<change-id>/design.md（有设计决策时）；openspec/changes/<change-id>/design/user-stories.md（US/AC）；openspec/changes/<change-id>/design/baseline-impact.md（每个 Change 强制）；openspec/changes/<change-id>/design/baseline-binding.json。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** 已批准的提案级 US/UC/AC、场景与业务规则、范围边界、需求追踪 ID、基线快照与约束绑定。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。


## 机器基线约束绑定（强制）

- 开始需求细化前必须通过 `python3 scripts/baseline-governance.py audit --require-frozen`。
- Change 辅助资产创建后，必须存在 `design/baseline-binding.json`；若使用 `new-change-assets.sh` 会自动从冻结注册表生成，亦可运行 `python3 scripts/baseline-governance.py init-binding --change-id <id>`。
- 不得删除/合并/改写机器生成的约束 ID；对每个 ACTIVE 约束填写 APPLICABLE 或 NOT_APPLICABLE 和具体理由。
- 阶段 05 人工审批绑定后运行 `python3 scripts/baseline-governance.py check-change --change-id <id> --phase requirement`；此门禁和 Markdown `baseline-impact.md` 同时通过才可交接。

## 阶段边界与评审停等（强制）

- 开始前运行 `python scripts/workflow.py check-entry --step 05-feature-requirements [--change-id <id>]`；退出码非 0 时立即停止并报告，不得绕过。
- 产物写完、检查通过只代表可送审：运行 `python scripts/workflow.py request-review --step 05-feature-requirements --summary "<摘要>"`，按 `templates/workflow/step-handoff-report.md` 展示交接报告后**立即结束回合**；禁止在同一会话读取/执行下一阶段 Prompt/Skill 或创建下一阶段产物。
- 只有用户明确回复“评审通过 05-feature-requirements”后，才可运行 `python scripts/workflow.py approve --step 05-feature-requirements --approver "<用户>" --approved-at <YYYY-MM-DD> --evidence <审批记录>` 并执行 `transition`。不得自行填写 approver/approved_at，不得把自检通过当作批准。
- `pending_approvals` 非空时禁止推进；`workflow-state.json` 只能通过 `check-entry`/`request-review`/`approve`/`transition` 等命令管理，禁止直接编辑。
- Claude Code 的 PreToolUse hook 会拒绝写入当前阶段之后的阶段产物（共享产物除外）与直接编辑状态文件；待评审期间同样拒绝。遇到拒绝必须停止并说明，不得更换路径或禁用 hook 绕过。
