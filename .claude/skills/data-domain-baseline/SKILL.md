---
name: data-domain-baseline
description: 项目级数据与领域基线。确定稳定领域边界、逻辑 ERD、数据所有权和通用约束。
---

# 项目级数据与领域基线

## 何时使用
当流程进入“项目级数据与领域基线”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
业务规则、总体架构、核心领域概念、现存数据库（若有）。

## 执行流程
1. 识别核心概念、领域边界、实体/值对象、生命周期和数据所有权。
2. 绘制逻辑 ERD，标注主要关系、基数和跨领域引用。
3. 制定稳定的命名、ID、审计字段、时间、删除、并发版本和保留规范（按项目需要裁剪）。
4. 确定事务边界、唯一性/完整性规则、并发控制和一致性策略。
5. 将稳定约束与提案级字段细节区分；共享领域边界改变必须发起基线变更评审。

## 输出
逻辑 ERD、领域边界、数据所有权、事务/并发约定、未决数据设计项。

## 质量与安全边界
不得仅凭页面字段推断数据模型；每项关键数据规则有业务依据；不把逻辑 ERD伪装成最终物理 DDL。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- pen.dev / Figma MCP 的输入必须基于实际可访问的链接、导出物和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/check-required-files.sh`


## 实际工具调用要求

- **Superpowers：** `brainstorming` 用于澄清领域边界和一致性取舍。必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时明确说明并执行等价步骤。
- **OpenSpec：** 读取相关规格和现有数据约定；本阶段不创建功能 Change，也不把功能级物理表设计提前固化。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="data-domain-baseline"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** 已批准产品基线；docs/architecture/* 架构基线；现有数据库/领域资料（若存在）。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** docs/architecture/logical-erd.md；docs/architecture/domain-boundaries.md（必要时修订）；docs/architecture/data-flows.md（必要时修订）。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** 逻辑实体、关系、数据所有权、领域不变量、数据流。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。
