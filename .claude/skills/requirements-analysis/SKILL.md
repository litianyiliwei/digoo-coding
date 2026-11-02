---
name: requirements-analysis
description: 需求发现与整理。将输入材料转成业务流程、用例、用户故事、业务规则与验收条件。
---

# 需求发现与整理

## 何时使用
当流程进入“需求发现与整理”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
客户访谈、业务材料、旧系统行为、目标、约束、角色和已知问题。

## 执行流程
1. 在宿主 Agent 支持且已安装时，先读取/调用 Superpowers `using-superpowers`，再读取/调用 `brainstorming`；遵循宿主环境的真实 Skill 调用方式，不假设 `@`、slash command 或 MCP 语法一定适用。若缺少技能，明确说明并按本 Skill 的澄清步骤执行，不得声称已调用。
2. 采用分阶段需求发现：先澄清目标/用户/痛点/成功标准，再逐步展开流程、规则、边界；关键未知项先提问，未确认前标为 PENDING。
3. 区分已确认事实、假设、冲突与待确认项；未知内容不得编造。
4. 梳理业务流程的触发条件、参与者、前置条件、主流程、替代/异常流程、后置条件。
5. 建立 `FLOW` → `UC` → `US` → `AC` 的稳定 ID 追踪。
6. 为用户故事写可验证的 Given/When/Then 验收条件，并覆盖权限、空值、边界、异常、重复提交和并发（适用时）。
7. 识别安全、隐私、性能、可用性、审计、数据保留、可访问性等非功能要求。
8. 不在需求阶段提前决定数据库表、类和框架细节。

## 输出
`docs/product/workflows.md`、`use-cases.md`、`user-stories.md`、`business-rules.md`、`open-questions.md`。

## 质量与安全边界
每条需求有来源和状态；每个关键故事至少有一个 AC；问题清单标注影响和需要谁决定。

## 与 OpenSpec / Superpowers 的边界
- 若 OpenSpec 已初始化，运行 `openspec list --specs` 并读取相关已批准规格；需求发现阶段不创建 Change。需求确认、拆分提案后，才通过 `openspec new change <change-id>` 开始 Change 生命周期。生成/修改 artifact 前按 CLI 当前版本执行 `openspec instructions <artifact> --change <change-id> --json`，完成后运行 `openspec validate <change-id> --strict`。
- 本阶段适用 Superpowers `brainstorming`，其作用是交互式澄清需求和比较方案；它不替代业务规格。只有实际发现并加载了技能才报告“已调用”，否则报告“不可用，采用显式等价流程”。
- pen.dev / Figma MCP 的输入必须基于实际可访问的链接、导出物和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/check-requirements.py [--strict]`；项目基线齐备时再运行 `scripts/check-required-files.sh`


## 实际工具调用要求

- **Superpowers：** `using-superpowers` 与 `brainstorming`（若实际可用）；先澄清目标、用户、痛点、范围和成功标准，信息不足先提问。必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时明确说明并执行等价步骤。
- **OpenSpec：** 仅运行 `openspec list --specs` 并阅读相关规格；本阶段不得创建 Change。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="requirements-analysis"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** 访谈/业务材料/旧系统资料；项目目标、用户、角色、约束；既有 docs/product/*（若存在）；既有 OpenSpec specs（只读）。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** docs/product/requirements-analysis.md；docs/product/workflows.md；docs/product/use-cases.md；docs/product/user-stories.md；docs/product/business-rules.md；docs/product/open-questions.md。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** 需求分析报告、流程、用例、故事、规则、未决问题。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。
