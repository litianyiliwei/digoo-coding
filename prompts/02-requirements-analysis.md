# Prompt：需求业务梳理

```text
执行 `@requirements-analysis`。

输入材料：<materials>
项目目标/用户/角色：<goals-and-roles>
既有 product 文档：<existing-product-docs>

输出项目级需求业务梳理：docs/product/requirements-analysis.md、workflows.md、data-objects.csv、rd-matrix.csv、business-rules.md、glossary.md、acceptance-policy.md、open-questions.md。

要求：
1. 业务流程必须完整、不得遗漏：覆盖全部业务域的主流程、替代流程、异常流程和后置条件；每个流程拆到可执行节点，节点 ID 用 NODE-<流程号>-<序号>。
2. 每个节点必须登记执行角色、输入数据对象、输出/写入数据对象、前置条件、处理动作、异常/分支、下一节点、关联业务规则。
3. 建立业务数据对象目录（DO-xxx）并输出 RD 矩阵（rd-matrix.csv）：逐行登记需求/规则 → 流程节点 → 角色 → 数据对象 → 访问类型；每个节点至少一条 RD 记录（或 N/A + 理由）。
4. 本阶段不输出用户故事、用例或 AC：US/AC 留到阶段 05 提案级需求分析，由每个 Change 生成；用例场景写入提案级 spec 的 Scenario，不单独产出 `use-cases` 文件。
5. 完成后运行 `python scripts/check-requirements.py --strict`，失败不得推进；按阶段结束审计核对流程节点与 RD 矩阵覆盖。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
```

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：本阶段为项目级，写 `N/A`。
- 加载 Skill：在支持 Agent Skill 的环境中使用 `@requirements-analysis`，或先显式加载同名 Skill。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`；不能只把 Skill 名字当普通文本。若无法加载仓库 Skill，明确报告并按 Prompt 执行。
- **Superpowers：** 使用 `using-superpowers` 与 `brainstorming`（若实际可用）；先澄清目标、用户、痛点、范围和成功标准。先检查技能是否真实安装/可发现，不可用时说明并执行等价步骤，禁止声称调用了未安装技能。
- **OpenSpec：** 仅运行 `openspec list --specs` 并阅读相关规格；本阶段不得创建 Change。命令须真实执行并报告退出码/结果；CLI 不存在或失败时标记为阻断/未执行。
- **状态与门禁：** 读取/更新 `workflow-state.json`。仅当本阶段产物写入指定路径且脚本检查通过后，才将阶段记为完成。遇到待审批、缺输入或验证失败必须暂停。
- **输出报告：** 列出实际读取文件、实际调用的 Skill/CLI/脚本、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件，除非 Prompt 明确授权且门禁已通过。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="requirements-analysis"` 的记录。

- 输入核验：访谈/业务材料/旧系统资料；项目目标、用户、角色、约束；既有 docs/product/*；既有 OpenSpec specs（只读）。逐项报告文件是否存在、版本和批准状态；不满足时暂停。
- 必须输出：docs/product/requirements-analysis.md；docs/product/workflows.md（含节点表）；docs/product/data-objects.csv；docs/product/rd-matrix.csv；docs/product/business-rules.md；docs/product/glossary.md；docs/product/acceptance-policy.md；docs/product/open-questions.md；docs/product/BASELINE-BRIEF.md；docs/product/role-permission-matrix.csv；docs/product/change-sizing.md；docs/product/decisions.md；docs/product/assumptions.md；docs/product/lessons.md；docs/product/id-conventions.md；docs/product/BASELINE-INDEX.md（运行 scripts/gen-baseline-index.py --write 生成）。按模板写入仓库，不要只在聊天中展示。
- 下一步输入：业务流程与节点级角色/数据对象、业务数据对象目录、RD 矩阵、业务规则、术语与验收政策、未决问题；常驻基线简报、角色权限矩阵、Change 切片规则、决策/假设登记、ID 约定与基线索引。在报告中明确这些文件如何被下游（阶段 03 项目总体架构设计）消费。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- **阶段边界（强制）：** 阶段完成 ≠ 可进入下一阶段。产物写完、检查通过后运行 `python scripts/workflow.py request-review --step 02-requirements-analysis --summary "<送审摘要>"`（流程冻结为待评审），按交接模板展示报告后**立即结束回合**；用户明确回复“评审通过 02-requirements-analysis”前，禁止读取/执行下一阶段 Prompt/Skill、禁止创建下一阶段产物。批准后运行 `python scripts/workflow.py approve --step 02-requirements-analysis --approver "<用户>" --approved-at <YYYY-MM-DD> --evidence <审批记录>`，再执行 `transition`。不得自行填写 approver/approved_at，不得把产物完成或自检通过当作批准。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。

## 阶段结束审计（必须执行）

- 逐流程核对节点完整性：主流程、替代流程、异常流程都有 NODE；每个节点有角色、输入/输出数据对象、前置条件、动作、分支、下一节点。
- 逐节点核对 RD 矩阵覆盖：每个 NODE 至少一条 RD 记录（或 N/A + 理由）；DO 引用不悬空。
- 运行 `python scripts/check-requirements.py --strict`，退出码必须为 0；审计结论写入交接报告。
