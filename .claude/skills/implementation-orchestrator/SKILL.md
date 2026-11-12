---
name: implementation-orchestrator
description: 实现、TDD、验证与代码审查。使用已安装的 Superpowers 工作流实施小任务并以真实测试结果验收。
---

# 实现、TDD、验证与代码审查

## 何时使用
当流程进入“实现、TDD、验证与代码审查”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入
审批通过的 OpenSpec artifacts、详细设计、tasks、仓库规范、可用 Superpowers。

## 执行流程
1. 先读取 `openspec instructions apply --change <id>` 和项目开发说明；核对 Superpowers 实际安装的技能。
2. 根据复杂度按需执行 Superpowers 的 `brainstorming`、`using-git-worktrees`、`writing-plans`、`subagent-driven-development` 或 `executing-plans`。
3. 涉及 UI 时先读取 `figma-audit.md` 的目标框架/转码说明、token 实际值、PAGE 规格、状态决策，以及 `figma-code/`（06 已按总体技术选型转码的目标框架设计代码）与 `figma-layout.csv`（断言映射）；默认离线消费，仅在版本变化或页面歧义时按页批量重读 Figma。**实现直接以 `figma-code/` 为页面骨架**：将 `.vue`（或 React 栈 `.tsx`/`.jsx`）设计代码移植到应用目录，只补路由、API 调用、状态、权限与业务逻辑，不得重写样式、布局或文案；确需改动时按 `UI-DEVIATION` 记录原因、影响、审批人并同步更新断言。先建立全局 CSS 变量/目标组件库主题/字体栈，页面样式必须引用 token，禁止散落硬编码颜色/字号；实现必须满足 `figma-layout.csv` 中的 `dom_selector`（选择器优先使用稳定的 `data-test` / `data-figma-node` 属性）。**不使用截图作为 UI 证据。**
4. 对行为变化使用 `test-driven-development` 的 RED-GREEN-REFACTOR：先写失败测试并观察失败，再做最小实现。
5. 按小任务实现并更新 OpenSpec tasks 复选框；每个任务运行相关测试。
6. 每个 PAGE 运行 `python scripts/check-figma-layout.py --change <change-id> --base-url <url> --viewport 1440x900`，产物 `design/evidence/figma-layout-check.json`；运行 `python scripts/check-design-tokens.py --change <change-id> --tokens <token.css>`。**UI 验证以机器证据为主**：在 `code-review.md` 的 `## UI fidelity` 逐 PAGE 直接从 JSON 抄录 Figma node、断言元素数/最大偏差、布局证据、结论与审批人；只有存在差异或 `UI-DERIVED` 的 PAGE 需要补充人工说明与审批，无差异 PAGE 不做逐页视觉复核。运行 `check-code-review.py --strict`。任一元素缺失、几何超差、文本/字体不符或 token 不一致即 FAIL。
7. 失败时使用 `systematic-debugging`，优先定位根因，不进行无证据的随机修改。
8. 阶段性使用 `requesting-code-review`；收到评论后按 `receiving-code-review` 核实并处理。
9. 结束前使用 `verification-before-completion`，运行真实测试/构建/契约检查，并报告命令、退出码和未执行项。
10. 不要声称使用了未安装的 Superpowers 技能；不要擅改 specs/OpenAPI。如规格确需变化，暂停并更新 Change。

## 输出
代码变更、测试、更新后的 tasks、代码审查报告和验证证据。

## 质量与安全边界
不以代码生成代替测试；不把未运行的检查报告为通过；禁止未审批的契约/需求变更。UI Change 以 06 目标框架设计代码为还原基线：08 只补业务逻辑，不得重写样式/布局/文案；视觉偏差必须有 `UI-DEVIATION` 审批，否则阻断。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- Figma MCP 的输入必须基于实际可访问的链接、节点和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/test-all.sh <project-dir>; scripts/verify-before-completion.sh; python scripts/check-figma-layout.py --change <change-id> --base-url <url> --viewport 1440x900; python scripts/check-design-tokens.py --change <change-id> --tokens <token.css>; python scripts/check-code-review.py --change <change-id> --strict`

## 实际工具调用要求

- **Superpowers：** 检查并按宿主机制加载 `using-superpowers`、`writing-plans`、`test-driven-development`；故障时 `systematic-debugging`；审查用 `requesting-code-review`/`receiving-code-review`；完成前 `verification-before-completion`。必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时明确说明并执行等价步骤。
- **OpenSpec：** 先执行 `openspec instructions apply --change <id> --json` 和 `openspec status --change <id>`；完成后 `openspec validate <id> --strict`，不擅改规格。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 实施期间的基线纪律（强制）

- 开发前再次核验 `design/baseline-impact.md`、`docs/architecture/baseline-status.md` 和批准的基线版本；代码、迁移、配置必须遵循已批准约束。
- 实施中发现基线不适用、冲突或缺失时，先在当前 Change 记录证据并暂停受影响任务；不得直接编辑冻结基线或以代码绕过规则。
- 创建/更新基线变更请求和 ADR，待对应负责人批准后更新基线版本；然后刷新当前 Change 的 baseline snapshot、详细设计、任务和验证。独立且不受影响的任务可经负责人确认后继续。
- 功能局部行为/端点/表迁移/IO/实现细节继续留在 Change，不得因开发完成就自动提升到全局基线。
- 详细规则见 `docs/BASELINE-FEATURE-INTERACTION.md`。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="implementation-orchestrator"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** 已批准的 design/baseline-impact.md 与当前 baseline-status.md；已批准 tasks.md/design.md；design.md（含前端/后端/测试设计节）、design/test-cases.csv、OpenAPI、IO 契约与 traceability.csv；涉及 UI 时 `design/figma-audit.md`（目标框架/转码说明、token 实际值、PAGE 规格、状态决策）、`design/figma-code/`（目标框架设计代码）与 `design/figma-layout.csv`（断言映射）及项目 token 文件；`docs/architecture/technology-decisions.md`（目标框架一致性）；项目级工程规范/测试策略；docs/product/open-questions.md（只读）。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。
- **本阶段输出：** 实际源代码/迁移/配置；条件适用的基线变更请求/ADR 草案（未经批准不更新冻结基线）；自动化测试代码与运行结果；openspec/changes/<change-id>/design/evidence/code-review.md（涉及 UI 时含 `## UI fidelity` 数值表，数值直接取自 `figma-layout-check.json`；仅差异/`UI-DERIVED` PAGE 需人工说明与审批）；`design/evidence/figma-layout-check.json`；实现/验证证据。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** 代码差异、测试报告、审查结论、未解决问题、`figma-layout-check.json` 与 token 检查结果。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。


## 独立验证交接（新增强制要求）

Builder 完成后不直接进入人工验收。必须交接给独立 Skill `@independent-verifier`（阶段 `09-independent-verification`），使用独立 Agent/上下文只读验证代码、规格、AC、IO 契约并重新执行测试。Builder 不得自行生成 PASS 结论替代 Verifier。


## 实现阶段的机器基线门禁（强制）

- 编码前必须通过 `python3 scripts/baseline-governance.py check-change --change-id <id> --phase design`。
- 实现完成后，为每条 APPLICABLE 约束记录 `implementation_verification.status=PASS`、验证方法和仓库内真实证据路径；纯设计约束需显式记录 NOT_APPLICABLE 与理由。
- 阶段 08 转出前执行 `python3 scripts/baseline-governance.py check-change --change-id <id> --phase implementation`。缺证据、NOT_RUN、PENDING 均阻断。
