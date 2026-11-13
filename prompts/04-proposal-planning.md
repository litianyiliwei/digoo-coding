# Prompt：提案拆分、依赖排序与路线图

```text
执行 `@proposal-planning`。

批准的基线：<baseline>
需求业务梳理/RD 矩阵：<requirements-and-rd>
切片规则与教训：<change-sizing-and-lessons>
未决问题：<open-questions>
阶段 03 审计报告：<baseline-audit-report>
优先级/约束：<priorities>

按独立可验收业务能力划分 OpenSpec Change。为每项给出 change-id、价值、范围/非目标、关联 FLOW/NODE/DO/BR、预期验收方向、依赖、风险、数据迁移、兼容和排序理由；按 `docs/product/change-sizing.md` 标注每项的规模预算，超过预算必须拆分或记录理由与验收人；提案级 UC/US/AC 在阶段 05 细化。先读取 open-questions、decisions/assumptions、lessons 与阶段 03 审计报告，把未决问题、基线缺口和已知反模式带入候选 Change 的风险/依赖，不要擅自关闭。拆分时必须检查平台/原生/设备/第三方前置依赖：跨端方案、原生插件与 JS Bridge、设备/网关、地图/天气/支付/实名/溯源等第三方审批、数据迁移与离线同步；这些依赖不得藏在备注里。输出 Mermaid 依赖图；优先纵向切片，不按前后端技术层横向切分。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
基线交互要求：为每个候选 Change 标注适用的产品/架构/数据/公共 API/前端/测试基线版本、需复用约束和潜在基线修订。功能局部变化留在 Change；跨功能公共约束变化列为基线变更候选，不得默认为已批准。
```

上下文：先运行 `python scripts/agent-context.py --stage <id> --change <change-id>` 获取精简输入；完整 `inputs` 仅用于审计，默认按精简/按需清单读取。阶段结束运行 `python scripts/check-output-context.py --stage <id> --strict` 检查摘要输出预算。

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：只在功能级阶段使用；项目级阶段可以写 `N/A`。
- 加载 Skill：在支持 Agent Skill 的 OpenCode 环境中使用 `@proposal-planning`，或先显式加载同名 Skill。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`（例如 OpenCode 支持时使用 `@<skill-id>`）；不能只把 Skill 名字当普通文本。若无法加载仓库 Skill，明确报告并按 Prompt 执行。
- **Superpowers：** 使用 `brainstorming` 的 stage-scoped 模式对提案边界、备选拆分与平台/原生依赖进行澄清；结论写入 `proposal-roadmap.md`，不另写独立设计文档。阶段 evidence 必须写 `methods`，至少记录 2 个问题、2 个备选、1 个决策，并运行 `python scripts/check-method-evidence.py --step 04-proposal-planning --evidence <evidence.json>`。先检查技能是否真实安装/可发现；不可用时用 `mode=equivalent` 并写 `reason`。
- **OpenSpec：** 先运行 `openspec list --specs`、`openspec list --changes`；提案获批后才可逐个运行 `openspec new change <change-id>`。命令须真实执行并报告退出码/结果；CLI 不存在或失败时标记为阻断/未执行，不得假装验证通过。
- **状态与门禁：** 读取/更新 `workflow-state.json`。仅当本阶段产物写入指定路径且脚本检查通过后，才将阶段记为完成。遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用的 Skill/CLI/脚本、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件，除非 Prompt 明确授权且门禁已通过。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="proposal-planning"` 的记录。

- 输入核验：已冻结项目基线；产品需求/节点/RD/角色权限矩阵；`BASELINE-BRIEF.md`、`change-sizing.md`、`decisions.md`、`assumptions.md`、`lessons.md`；已知技术债与依赖。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：docs/product/proposal-roadmap.md；每个候选 Change 的范围/依赖/价值说明。按模板写入仓库，不要只在聊天中展示。
- 下一步输入：经批准的 Change 列表、优先级、依赖顺序。在报告中明确这些文件如何被下游消费。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 基线交互：必须按 `docs/BASELINE-FEATURE-INTERACTION.md` 核验基线读取/变更归属；阶段 05 创建/更新 `design/baseline-impact.md`，后续阶段复核；未经批准不得修改冻结基线。
- **阶段边界（强制）：** 阶段完成 ≠ 可进入下一阶段。产物写完、检查通过后运行 `python scripts/workflow.py request-review --step 04-proposal-planning --summary "<送审摘要>"`（流程冻结为待评审），按交接模板展示报告后**立即结束回合**；用户明确回复“评审通过 04-proposal-planning”前，禁止读取/执行下一阶段 Prompt/Skill、禁止创建下一阶段产物。批准后运行 `python scripts/workflow.py approve --step 04-proposal-planning --approver "<用户>" --approved-at <YYYY-MM-DD> --evidence <审批记录>`，再执行 `transition`。不得自行填写 approver/approved_at，不得把产物完成或自检通过当作批准。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。


## 机器基线约束（必须执行）

提案拆分前运行 `python3 scripts/baseline-governance.py audit --require-frozen`。读取 Constraint Registry，为每个候选 Change 标注可能适用的 Constraint ID、受影响域和基线变更候选；不得修改冻结基线，也不得将 DRAFT 规则作为已批准约束。
