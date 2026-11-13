# Prompt：提案级需求分析

```text
执行 `@feature-requirements`，Change：<change-id>。

业务目标：<goal>
项目需求业务梳理：<product-paths>
常驻基线/角色矩阵/切片规则：<baseline-brief-and-sizing>
决策/假设/教训：<decisions-assumptions-lessons>
未决问题：<open-questions>
关联 FLOW/NODE/DO/BR/ROLE/CAP：<ids>

先读 `docs/product/BASELINE-BRIEF.md`（≤1 页）、`change-sizing.md`、`role-permission-matrix.csv`、`decisions.md`、`assumptions.md`、`lessons.md`；再查 `openspec status --change <change-id>`、`openspec list --specs` 并读取相关规格全文。按当前 OpenSpec schema 完成 proposal、spec delta、design、tasks；`design.md` 只写提案级初始决策（≤1 页），接口/前端/后端/测试细节留到阶段 07，不在这里提前展开；同时从项目业务流程、RD 矩阵和 Change 范围推导提案级 `design/user-stories.md`（US/AC），不得复制项目级历史故事清单。specs 是规范行为的唯一来源，场景写在 spec 的 Scenario 中；user-stories 只写 US、AC 与追踪 ID，不重复完整规格；不单独产出 `design/use-cases.md`，用例场景一律写入 spec 的 Scenario。权限相关 AC 必须引用 ROLE/CAP，数据类 AC 引用 DO。spec 仅写外部可观察行为；每个 Requirement 含至少一个 Scenario；涉及多端/原生/设备的 Change，AC/Scenario 还必须覆盖平台权限（拒绝/降级）、离线/弱网、推送/深链、多端差异、失败重试、幂等/并发；不适用写 N/A + 理由。tasks 使用 `- [ ]` 复选框。用 `change-sizing.md` 的预算检查范围，超过必须拆分或记录理由与验收人；完成后核对 DoD。阶段 evidence 必须写 `methods`（至少 3 个问题、1 个备选、1 个决策，结果落点写 `design/user-stories.md` 或 `design.md`），并运行 `python scripts/check-method-evidence.py --step 05-feature-requirements --evidence <evidence.json>`。列出基线影响和审批问题。完成后运行 `python scripts/check-requirements.py --change <change-id> --strict` 与 `openspec validate <change-id> --strict`。创建 Change 后运行 `bash scripts/new-change-assets.sh <change-id>`，确保生成 `design/baseline-impact.md`，再填充并评审；不得开始详细设计/编码直到提案需求与基线影响结论获批。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
基线交互要求：先核验 `docs/architecture/baseline-status.md`，读取相关产品/架构/数据/公共契约/测试基线及现行 OpenSpec specs。必须按 `templates/change-assets/design/baseline-impact.md` 创建 `openspec/changes/<change-id>/design/baseline-impact.md`，记录版本、约束 ID/章节、复用项、冲突和归属分类。若关键设计依赖尚未批准的基线变化，标记阻断，不进入详细设计/实现。填完后运行 `python scripts/check-baseline-impact.py <change-id>` 做结构检查；此时尚未审批的草案不得使用 `--strict`。
```

上下文：先运行 `python scripts/agent-context.py --stage <id> --change <change-id>` 获取精简输入；完整 `inputs` 仅用于审计，默认按精简/按需清单读取。阶段结束运行 `python scripts/check-output-context.py --stage <id> --strict` 检查摘要输出预算。

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：只在功能级阶段使用；项目级阶段可以写 `N/A`。
- 加载 Skill：在支持 Agent Skill 的 OpenCode 环境中使用 `@feature-requirements`，或先显式加载同名 Skill。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`（例如 OpenCode 支持时使用 `@<skill-id>`）；不能只把 Skill 名字当普通文本。若无法加载仓库 Skill，明确报告并按 Prompt 执行。
- **Superpowers：** 使用 `brainstorming` 的 stage-scoped 模式检查方案、需求边界与多端场景完整性；结论写入 `design/user-stories.md`、`spec` 的 Scenario 或 `design.md`，不另写独立设计文档；不在本阶段编码。阶段 evidence 必须写 `methods`（至少 3 个问题、1 个备选、1 个决策）并运行 `python scripts/check-method-evidence.py --step 05-feature-requirements --evidence <evidence.json>`。先检查技能是否真实安装/可发现，不可用时用 `mode=equivalent` 并写 `reason`。
- **OpenSpec：** 必须使用 OpenSpec CLI：`openspec status --change <id>`、`openspec list --specs`、按需 `openspec instructions <artifact> --change <id> --json`，完成后 `openspec validate <id> --strict`。命令须真实执行并报告退出码/结果；CLI 不存在或失败时标记为阻断/未执行，不得假装验证通过。
- **状态与门禁：** 读取/更新 `workflow-state.json`。仅当本阶段产物写入指定路径且脚本检查通过后，才将阶段记为完成。遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用的 Skill/CLI/脚本、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件，除非 Prompt 明确授权且门禁已通过。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="feature-requirements"` 的记录。

- 输入核验：已批准路线图/当前 Change 范围；项目需求业务梳理与冻结基线；常驻基线简报、角色权限矩阵、切片规则与 DoD、决策/假设/教训；关联 FLOW/NODE/DO/BR/ROLE/CAP；现有 OpenSpec specs；docs/product/open-questions.md（只读）；docs/product/acceptance-policy.md（项目级验收口径；AC 与验收政策对齐）。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须先执行 `bash scripts/new-change-assets.sh <change-id>` 创建辅助模板（若已存在则保留），再输出：openspec/changes/<change-id>/proposal.md；openspec/changes/<change-id>/specs/<capability>/spec.md（适用时）；openspec/changes/<change-id>/tasks.md（初步任务）；openspec/changes/<change-id>/design.md（有设计决策时）；openspec/changes/<change-id>/design/user-stories.md（US/AC）。按模板写入仓库，不要只在聊天中展示。
- 下一步输入：已批准的提案级 US/AC、场景与业务规则、范围边界、需求追踪 ID、基线绑定。在报告中明确这些文件如何被下游（阶段 06 原型、页面与交互清单）消费。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 基线交互：必须按 `docs/BASELINE-FEATURE-INTERACTION.md` 核验基线读取/变更归属；阶段 05 创建/更新 `design/baseline-impact.md`，后续阶段复核；未经批准不得修改冻结基线。
- **阶段边界（强制）：** 阶段完成 ≠ 可进入下一阶段。产物写完、检查通过后运行 `python scripts/workflow.py request-review --step 05-feature-requirements --summary "<送审摘要>"`（流程冻结为待评审），按交接模板展示报告后**立即结束回合**；用户明确回复“评审通过 05-feature-requirements”前，禁止读取/执行下一阶段 Prompt/Skill、禁止创建下一阶段产物。批准后运行 `python scripts/workflow.py approve --step 05-feature-requirements --approver "<用户>" --approved-at <YYYY-MM-DD> --evidence <审批记录>`，再执行 `transition`。不得自行填写 approver/approved_at，不得把产物完成或自检通过当作批准。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。


## 机器基线绑定（必须执行）

创建辅助文件后必须生成 `design/baseline-binding.json`（`bash scripts/new-change-assets.sh <id>` 会自动生成；也可执行 `python3 scripts/baseline-governance.py init-binding --change-id <id>`）。逐条处理当前全部 ACTIVE Constraint ID，不得删除约束项；每条必须标记 APPLICABLE 或 NOT_APPLICABLE 并说明理由。由负责人审批 JSON 中的 approval 字段及证据文件后，执行 `python3 scripts/baseline-governance.py check-change --change-id <id> --phase requirement`。此门禁通过前不得完成阶段 05。
