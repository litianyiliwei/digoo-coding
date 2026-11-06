---
name: test-design
description: 测试设计。把每条验收标准映射到单元、契约、集成、E2E 或人工测试。
---

# 测试设计

## 何时使用
当流程进入“测试设计”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
AC、OpenAPI、前后端设计、领域/IO 风险与质量目标。

## 执行流程
1. 逐条将 AC 映射到用例；不能自动化的检查写明人工验证原因。
2. 按风险分配 unit、component、API contract、integration、E2E 和手工测试。
3. 覆盖正常、边界、权限、异常、幂等、并发、一致性、超时/重试（适用时）。
4. 给出前置条件、测试数据、步骤、预期结果、清理方式、外部依赖替身和自动化位置。
5. 测试断言要验证用户可观察行为或业务不变量，不可只断言方法被调用。

## 输出
`design/test-design.md`、测试追踪矩阵、测试数据和环境要求。

## 质量与安全边界
每条 AC 至少映射一个测试或标记 `N/A + 原因`；不得只有 happy path。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- pen.dev / Figma MCP 的输入必须基于实际可访问的链接、导出物和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/check-traceability.py --file openspec/changes/<change-id>/traceability.csv --strict`


## 实际工具调用要求

- **Superpowers：** `brainstorming` 用于补足边界场景；测试用例必须追踪到 AC/REQ。必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时明确说明并执行等价步骤。
- **OpenSpec：** 读取 Change 状态、规格和 OpenAPI；用 `openspec validate <id> --strict` 核对结构。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 测试与质量基线约束（强制）

- 测试设计必须读取 `docs/architecture/test-strategy.md`，沿用其测试分层、契约测试、环境、覆盖要求和质量门禁；功能特有的 TEST ID、测试数据和断言留在当前 Change。
- 若功能发现全局门禁缺失/不合理，先提出质量基线变更及影响分析；不得只在当前 Change 静默豁免全局强制规则。
- 在 `design/baseline-impact.md` 记录所采用的测试基线版本。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="test-design"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** openspec/changes/<change-id>/design/baseline-impact.md 与当前 docs/architecture/baseline-status.md；已批准功能规格/AC；OpenAPI；前后端详细设计；API→IO 映射与 IO 契约；项目级测试策略。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** openspec/changes/<change-id>/design/test-design.md；openspec/changes/<change-id>/traceability.csv。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** TEST ID、覆盖的 AC/API/IO、测试数据/环境/命令、预期结果。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。


## 机器基线约束（强制）

- 测试策略、质量门禁、测试层级和覆盖要求必须逐条映射至 `baseline-binding.json`；设计证据定位到 test-design/traceability/test matrix。
- 完成本阶段时执行 `python3 scripts/baseline-governance.py check-change --change-id <id> --phase design`。
