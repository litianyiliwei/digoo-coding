---
name: requirements-analysis
description: 需求业务梳理。输出完整业务流程（节点级角色与数据对象）、业务数据对象目录、RD 矩阵、业务规则与验收政策；用户故事与 AC 统一留到提案级，本阶段不产出用例。
---

# 需求业务梳理

## 何时使用
当流程进入“需求业务梳理”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入

读取顺序：先读 `docs/product/BASELINE-BRIEF.md` 与当前 Change 产物；按命中的 ID 定向读取；完整基线/架构/ADR/完整 specs 仅在必要时按需读取并记录原因（见 `docs/INPUT-OUTPUT-POLICY.md`）。
访谈、业务材料、旧系统资料、项目目标、用户与角色、约束、既有 docs/product/*、既有 OpenSpec specs（只读）。

## 执行流程
1. 在宿主 Agent 支持且已安装时，先读取/调用 Superpowers `using-superpowers`，再读取/调用 `brainstorming`；必须使用 `internet-research` 方法（WebSearch/WebFetch 或宿主等价联网工具）完成参考产品与市场调研。遵循宿主环境的真实 Skill 调用方式，不假设 `@`、slash command 或 MCP 语法一定适用。若缺少技能，明确说明并按本 Skill 的澄清步骤执行，不得声称已调用；无联网能力时标记 BLOCKED，不得用记忆替代。
2. 采用分阶段需求发现：先澄清目标/用户/痛点/成功标准，再逐步展开业务流程、业务规则、数据对象与边界；同时逐项询问业务异常/边界（天气/季节、设备离线、人工接管、审计/溯源、监管上报、多角色、历史数据迁移、数据所有权与保留）；关键未知项先提问，未确认前标为 PENDING，并写入 `open-questions.md`。
3. **业务流程必须完整、不得遗漏**：覆盖全部业务域（种植、畜牧、水产及监管/溯源等支撑域）的触发条件、前置条件、主流程、替代流程、异常流程、后置条件。每个流程拆到可执行节点，节点编号稳定为 `NODE-<流程号>-<序号>`（如 `NODE-004-01`）。
4. **每个节点必须登记**：执行角色、输入数据对象、输出/写入数据对象、前置条件、处理动作、异常/分支、下一节点、关联业务规则。纯人工节点与系统节点都要登记；不得用概括性步骤代替节点表。
5. 建立业务数据对象目录：`DO-xxx` 稳定 ID、名称、定义、关键属性、业务所有者、来源/消费节点。数据对象是业务概念，不是数据库表。
6. **输出 RD 矩阵**：逐行登记 R（需求/业务规则/流程节点）→ D（数据对象）的读写关系，包含所属 FLOW/NODE、角色、访问类型（读/写/读写/校验）和验收要求；每个节点至少有一条 RD 记录，或明确写 `N/A` + 理由。
7. 统一术语、角色、权限、跨流程状态和验收政策；只把全局复用的规则放入项目级业务规则，功能细节留到提案级。
8. **本阶段不输出用户故事、用例或 AC**：US/AC 在阶段 05「提案级需求分析」按 Change 生成；用例场景写入提案级 spec 的 Scenario，不单独产出 `use-cases` 文件。本阶段只保留流程、节点、数据对象、RD 矩阵、业务规则和验收政策。
9. **维护项目级常驻基线**：生成 `BASELINE-BRIEF.md`（≤1 页入口）、`role-permission-matrix.csv`、`change-sizing.md`、`decisions.md`、`assumptions.md`、`lessons.md`、`id-conventions.md`；运行 `scripts/gen-baseline-index.py --write` 生成 `BASELINE-INDEX.md`。
10. 检查流程/节点/数据对象/RD/规则 ID 唯一、引用闭合、节点全覆盖；未确认内容进入 open-questions，不擅自决策。
11. 不在需求阶段提前决定数据库表、类、框架或 API 细节。

## 输出
`docs/product/requirements-analysis.md`、`workflows.md`（含节点表）、`data-objects.csv`、`rd-matrix.csv`、`business-rules.md`、`glossary.md`、`acceptance-policy.md`、`open-questions.md`、`reference-research.md`、`BASELINE-BRIEF.md`、`role-permission-matrix.csv`、`change-sizing.md`、`decisions.md`、`assumptions.md`、`lessons.md`、`id-conventions.md`、`BASELINE-INDEX.md`（由脚本生成）。

## 质量与安全边界
每条需求有来源和状态；每个流程的每个节点都有角色与数据对象；RD 矩阵引用闭合且覆盖全部节点；未确认项有负责人与阻塞条件。

## 与 OpenSpec / Superpowers 的边界
- 若 OpenSpec 已初始化，运行 `openspec list --specs` 并读取相关已批准规格；本阶段不创建 Change。
- 本阶段适用 Superpowers `brainstorming`，其作用是交互式澄清需求和比较方案；它不替代业务规格。只有实际发现并加载了技能才报告“已调用”。
- Figma MCP 的输入必须基于实际可访问的链接、节点和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/check-requirements.py --strict`；`python scripts/check-reference-research.py --strict`

## 实际工具调用要求

- **Superpowers：** `using-superpowers` 与 `brainstorming` 的 stage-scoped 模式；先澄清目标、用户、痛点、范围和成功标准，并逐项询问业务异常/边界。必须使用 `internet-research` 方法（WebSearch/WebFetch 或宿主等价联网工具）完成参考产品与市场调研，结果写入 `docs/product/reference-research.md`；无联网能力时标记 BLOCKED，不得用记忆替代。结论写入 `requirements-analysis.md` 或 `open-questions.md`，不另写独立设计文档；阶段 evidence 必须写 `methods`（brainstorming 3/1/1，internet-research 3/2/1）并运行 `python scripts/check-method-evidence.py --step 02-requirements-analysis --evidence <evidence.json>`。必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时用 `mode=equivalent` 并写 `reason`（联网调研不可用不属于 equivalent，必须 BLOCKED）。
- **OpenSpec：** 仅运行 `openspec list --specs` 并阅读相关规格；本阶段不得创建 Change。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="requirements-analysis"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** 访谈/业务材料/旧系统资料；项目目标、用户、角色、约束；既有 docs/product/*（若存在）；既有 OpenSpec specs（只读）；用户提供的参考产品（名称/链接/截图/账号；无则 NONE + 理由）；互联网调研工具（WebSearch/WebFetch 或宿主等价能力）。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** docs/product/requirements-analysis.md；docs/product/workflows.md；docs/product/data-objects.csv；docs/product/rd-matrix.csv；docs/product/business-rules.md；docs/product/glossary.md；docs/product/acceptance-policy.md；docs/product/open-questions.md；docs/product/reference-research.md；docs/product/BASELINE-BRIEF.md；docs/product/role-permission-matrix.csv；docs/product/change-sizing.md；docs/product/decisions.md；docs/product/assumptions.md；docs/product/lessons.md；docs/product/id-conventions.md；docs/product/BASELINE-INDEX.md（脚本生成）。按模板生成并落盘。
- **下游交接：** 业务流程与节点级角色/数据对象、业务数据对象目录、RD 矩阵、业务规则、术语与验收政策、未决问题。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。

## 阶段结束审计（强制）

- 逐流程核对节点表：每个 FLOW 的主流程、替代流程、异常流程都有节点；每个节点都有角色、输入/输出数据对象、前置条件、动作、分支、下一节点。
- 逐节点核对 RD 矩阵：每个 NODE 至少有一条 RD 记录（或 N/A + 理由）；每个 DO 至少被一个节点使用；引用不得悬空。
- 核对业务规则、术语、验收政策与流程/节点一致；冲突转入 open-questions，不擅自选择。
- 运行 `python scripts/check-requirements.py --strict` 与 `python scripts/check-reference-research.py --strict`，失败不得推进。

## 阶段边界与评审停等（强制）

- 开始前运行 `python scripts/workflow.py check-entry --step 02-requirements-analysis [--change-id <id>]`；退出码非 0 时立即停止并报告，不得绕过。
- 产物写完、检查通过只代表可送审：运行 `python scripts/workflow.py request-review --step 02-requirements-analysis --summary "<摘要>"`，按 `templates/workflow/step-handoff-report.md` 展示交接报告后**立即结束回合**；禁止在同一会话读取/执行下一阶段 Prompt/Skill 或创建下一阶段产物。
- 只有用户明确回复“评审通过 02-requirements-analysis”后，才可运行 `python scripts/workflow.py approve --step 02-requirements-analysis --approver "<用户>" --approved-at <YYYY-MM-DD> --evidence <审批记录>` 并执行 `transition`。不得自行填写 approver/approved_at，不得把自检通过当作批准。
- `pending_approvals` 非空时禁止推进；`workflow-state.json` 只能通过 `check-entry`/`request-review`/`approve`/`transition` 等命令管理，禁止直接编辑。
- Claude Code 的 PreToolUse hook 会拒绝写入当前阶段之后的阶段产物（共享产物除外）与直接编辑状态文件；待评审期间同样拒绝。遇到拒绝必须停止并说明，不得更换路径或禁用 hook 绕过。
