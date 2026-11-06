# Prompt：项目总体架构设计

```text
执行 `@project-architecture-baseline`，Change：N/A。

需求业务梳理：<product-paths>
技术约束/环境：<constraints>
非功能要求：<nfr>

合并输出项目总体架构设计：系统上下文、领域边界、部署、数据流转、逻辑 ERD、技术选型决策、API/前端/测试公共契约，并在阶段结束审计中冻结项目基线。
技术要求：
1. 先做技术选型访谈，逐项询问并记录用户/技术负责人的确认人与日期；不得默认或自行假设。
2. 数据流转必须按 DF-xxx 完整登记：同步/异步、事务边界、失败与补偿，并引用 FLOW/NODE/DO/RD 条目。
3. 逻辑 ERD 必须覆盖 data-objects.csv 的业务数据对象与 rd-matrix.csv 的读写关系；区分逻辑模型与物理 DDL。
4. API/前端/测试公共契约只写跨功能复用规则；功能级 schema/页面/物理表留在 Change。
5. 阶段结束审计：运行 `bash scripts/check-required-files.sh --strict`，完成 baseline-status/manifest/registry，执行 `python scripts/baseline-governance.py refresh-hashes`、负责人 `freeze`，再执行 `python scripts/baseline-governance.py audit --require-frozen`；存在阻断项不得冻结。
6. 审计报告写入 docs/project/baseline-audit-report.md，区分已更新基线、Change 局部记录和待批准修订。
正式产物请遵循 `docs/TEMPLATE-POLICY.md` 与 `docs/OUTPUT-TEMPLATE-MATRIX.csv` 指定模板；不要删除模板字段，未知项写 PENDING 并说明原因。
```

## 运行前要填的变量

- 输入材料：替换 `<...>` 占位符为真实路径、链接或内容。
- Change ID：本阶段为项目级，写 `N/A`。
- 加载 Skill：在支持 Agent Skill 的环境中使用 `@project-architecture-baseline`，或先显式加载同名 Skill。

## 执行工具协议（必须遵守）

- **加载本项目 Skill：** 按当前 Agent 的真实机制加载 `.claude/skills/<skill-id>/SKILL.md`；不能只把 Skill 名字当普通文本。若无法加载仓库 Skill，明确报告并按 Prompt 执行。
- **Superpowers：** 使用 `brainstorming` 比较架构备选项、澄清领域边界与一致性取舍；先确认技能真实安装/可发现，不可用时说明并执行等价步骤。
- **OpenSpec：** 若 CLI 可用，运行 `openspec list --specs`、`openspec list --changes` 核对基线与现有规格关系；本阶段不创建功能 Change。命令须真实执行并报告退出码/结果。
- **pen.dev / Figma MCP：** 仅作为可访问的参考输入；不把不可读取内容当作已审查。
- **状态与门禁：** 读取/更新 `workflow-state.json`。仅当产物写入指定路径、脚本与冻结审计通过且所需审批完成后，才将阶段记为完成。
- **输出报告：** 列出实际读取文件、实际调用的 Skill/CLI/脚本、生成/修改文件、检查结果、未执行项和下一步。不得自动提交、发布、归档或覆盖既有文件。

## 强制交付物交接

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.md` 与 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="project-architecture-baseline"` 的记录。

- 输入核验：已批准的 requirements-analysis/workflows/data-objects/rd-matrix/business-rules/glossary/acceptance-policy；现有仓库结构/技术约束；非功能需求；技术选型偏好。逐项报告存在、版本和批准状态；不满足时暂停。
- 必须输出：docs/architecture/system-context.md；domain-boundaries.md；containers-and-deployment.md；data-flows.md；logical-erd.md；technology-decisions.md；api-conventions.md；frontend-conventions.md；test-strategy.md；docs/adr/README.md；baseline-status.md；baseline-manifest.json；constraint-registry.json；docs/project/baseline-audit-report.md。按模板写入仓库。
- 下一步输入：冻结的项目总体架构基线、数据流转、逻辑 ERD、公共契约/测试策略、ACTIVE 约束目录、审计报告与审批记录。在报告中明确阶段 09/10 如何消费。
- 阶段完成时，按 `templates/workflow/step-handoff-report.md` 展示交接报告；区分已生成、草案、建议、待确认和未执行。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。

## 阶段结束审计与冻结（必须执行）

- 运行 `bash scripts/check-required-files.sh --strict`，退出码必须为 0。
- 完成 Manifest/Registry 后依次执行：
  `python scripts/baseline-governance.py refresh-hashes`
  `python scripts/baseline-governance.py freeze --approved-by <负责人> --approved-at <ISO日期> --evidence <审批证据路径>`
  `python scripts/baseline-governance.py audit --require-frozen`
- Evidence 必须包含 `docs/architecture/baseline-manifest.json` 与 `docs/architecture/constraint-registry.json` 两个输出；未冻结、哈希不匹配或缺少产物时不得推进。
- 审计报告写入 `docs/project/baseline-audit-report.md`；存在阻断项时不得建议冻结。
