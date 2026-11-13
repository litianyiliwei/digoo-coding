---
name: acceptance-audit
description: 人工验收、归档与基线回写。对照 AC 和证据验收；关闭阻断项后才归档与回写通用决策。
---

# 人工验收、归档与基线回写

## 何时使用
当流程进入“人工验收、归档与基线回写”时加载本 Skill。一次只处理一个明确阶段；不要提前执行后续阶段，也不要修改已批准内容。

## 输入

读取顺序：先读 `docs/product/BASELINE-BRIEF.md` 与当前 Change 产物；按命中的 ID 定向读取；完整基线/架构/ADR/完整 specs 仅在必要时按需读取并记录原因（见 `docs/INPUT-OUTPUT-POLICY.md`）。
阶段 09 的独立验证 PASS 报告与 JSON 证据（必须）；实现分支、AC、`design/user-stories.md`、`docs/product/acceptance-policy.md`、测试/构建报告、Figma/原型审计、OpenAPI、`design/baseline-impact.md`、当前 `baseline-status.md` 与已批准基线修订证据。

## 执行流程
1. 先核验 `design/evidence/independent-verification-report.md` 与 `.json` 存在且 Verdict=PASS，并确认验证 revision 与当前待验收 revision 一致；缺失/FAIL/BLOCKED 时拒绝验收。
2. 逐条记录 AC 的通过/失败/不适用及证据链接。
3. 核对页面/事件、API 契约、数据迁移、权限、日志和可观测性；涉及 UI 时逐 PAGE 对照 `figma-audit.md`（目标框架/转码说明、token 实际值/PAGE 规格/状态）与真实 Figma 文件。**验收以机器证据为主**：无差异、非 `UI-DERIVED` 且 `figma-layout-check.json` PASS 的 PAGE 可按机器证据批量签收（逐 PAGE 行照常填写，注明“机器证据签收”）；仅对存在差异、`UI-DERIVED` 或未纳入断言的 PAGE 打开运行中的系统界面与 Figma 评审稿并排核对。在 `acceptance.md` 的 `## UI acceptance` 逐 PAGE 签收（ACCEPTED / DEVIATION_APPROVED + Figma node + 运行系统入口 + 差异/审批 + 验收方式 + 评审人），缺证据不得归档。**不保存截图；截图不是验收证据；机器几何证据 `figma-layout-check.json` 必须为 PASS。**
4. 把发现分类为缺陷、需求变更或已批准偏差；需求变化另开/更新 Change。
5. 检查阻断项、遗留风险、上线/回滚及人工验收人。
6. 验收门禁通过后先处理已批准的基线回写：更新对应基线文档、域版本和状态登记，并复核在途 Change。
7. 再按当前 OpenSpec CLI 流程归档，将功能行为 delta 合并到主规格；OpenSpec archive 与项目设计基线回写是独立判断。不要对未完成任务使用自动确认参数绕过检查。

## 输出
`evidence/acceptance.md`、AC 验收矩阵、遗留风险、归档建议、基线回写项、更新后的基线版本登记（适用时）和在途 Change 复核清单。

## 质量与安全边界
每个 AC 有证据或明确阻断；未验收不得宣称完成；归档前先查看差异与验证结果。UI 验收不得用截图；无差异 PAGE 可依据机器证据批量签收，但差异/`UI-DERIVED` PAGE 必须并排核对并记录审批。

## 与 OpenSpec / Superpowers 的边界
- OpenSpec 保存 Change 的 proposal、行为 delta specs、design 和 tasks；本 Skill 不替代 OpenSpec 自身校验。
- Superpowers 用于研发方法论与执行纪律；只有确认真实安装且 Agent 可调用时才声称使用了某项技能。
- Figma MCP 的输入必须基于实际可访问的链接、节点和 MCP 返回结果。
- 不在本阶段自动提交、发布、归档或覆盖用户文件。

## 推荐检查
`scripts/verify-before-completion.sh <change-id>`


## 实际工具调用要求

- **Superpowers：** 使用 `verification-before-completion` 验证真实测试证据，必要时使用 `requesting-code-review`/`receiving-code-review`。阶段 evidence 必须写 `methods`（至少 1 个决策和真实证据路径）并运行 `python scripts/check-method-evidence.py --step 10-acceptance-audit --evidence <evidence.json>`。有 `design/interface-catalog.csv` 时，逐行核对 interface_id 的 owner、测试与真机/模拟器/替身/人工证据；缺失不得归档。必须按当前宿主 Agent 的真实机制检查、读取或调用技能。只在确实加载/执行后报告成功；不可用时用 `mode=equivalent` 并写 `reason`。
- **OpenSpec：** 运行 `openspec status --change <id>` 和 `openspec validate <id> --strict`；只有人工批准且所有门禁通过后才运行 `openspec archive <id>`，不使用 `-y` 绕过确认。命令必须真实执行并报告退出码/结果。CLI 不可用时标记为“未执行/阻断”，不得伪造校验结果。
- **项目 Skill：** 按宿主 Agent 的实际机制加载本 Skill；仅在 Prompt 中提到技能名不等于已调用技能。
- **状态更新：** 仅在产物写入指定路径且门禁通过后更新 `workflow-state.json`；遇到待审批或验证失败时记录阻断，不推进下一阶段。

## 验收时的基线回写规则（强制）

- 验收时逐项复核 `design/baseline-impact.md` 中的候选修订；只回写已批准、已实现、已验证且有跨功能复用价值的内容。
- 功能专属 API、页面、物理表字段/迁移、IO 和测试用例留在归档 Change；不得复制到全局基线。
- 需要回写时更新对应产品/架构/数据/公共契约/测试基线及 `docs/architecture/baseline-status.md` 的版本、审批人、生效日期、关联 Change/ADR；运行基线审计。
- OpenSpec archive 更新行为主规格，不等于所有 Change 都要修改项目设计基线。两类更新分别判断和记录。
- 基线更新后，列出受影响的在途 Change 并要求复核；禁止静默改变其既有基线快照。
- 详细规则见 `docs/BASELINE-FEATURE-INTERACTION.md`。

## 输入/输出/交接契约（强制）

执行本 Skill 前后，必须遵守 `docs/STEP-ARTIFACT-CONTRACTS.md`，并读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="acceptance-audit"` 的契约记录。不得仅凭本 Skill 的简要“输入/输出”段落推断交接完成。

- **本阶段输入：** 已实现代码与测试证据；已批准 AC/规格/追踪矩阵；openspec/changes/<change-id>/design/user-stories.md（提案级 US/AC）、design/test-cases.csv（TEST 覆盖），以及涉及 UI 时的 design/figma-audit.md（目标框架/转码说明、token 实际值/PAGE 规格/状态）、design/figma-code/（目标框架设计代码）、design/figma-layout.csv（断言映射）、design/evidence/figma-layout-check.json（08 实测）与 code-review.md 的 UI fidelity；docs/product/acceptance-policy.md、docs/product/open-questions.md（只读）；代码审查记录；`design/baseline-impact.md` 与当前 `baseline-status.md`；已批准的基线修订请求/ADR（如有）；运行中的验收环境入口（URL/路由）。逐项核验存在、版本、批准状态；缺失或未批准时停止并报告。**不使用截图。**
- **本阶段输出：** openspec/changes/<change-id>/design/evidence/acceptance.md（含 UI Change 的 `## UI acceptance` 逐 PAGE 签收：Figma node、运行系统入口、差异/审批、验收方式、评审人）；验收报告与批准记录；条件适用的项目基线文档/版本登记/在途 Change 复核；OpenSpec archive 结果及更新后的主规格（仅批准后）。按模板生成并落盘；如路径包含 `<change-id>`，必须替换为当前真实 Change ID。
- **下游交接：** 已验收并归档的能力规格、验收证据、后续 Change 依赖。明确指出下一阶段消费哪些文件/字段。
- **结束展示：** 使用 `templates/workflow/step-handoff-report.md`，展示输入核验、输出路径与摘要、追踪关系、自检命令/退出码、未执行项、待审批/阻断项和下一阶段输入。
- **状态纪律：** 仅在真实产物落盘、门禁通过且所需审批完成后更新 `workflow-state.json`；草案/待审产物不得记为已完成。


## 独立验证前置门禁（P0）

- 阶段 10 必须消费阶段 09 的独立验证报告和 JSON；Builder 自己的总结、单元测试结果或代码审查报告不能替代独立 Verifier。
- 验证报告必须是 PASS，且被测 revision 与当前验收代码一致；若代码在验证后变化，必须重新执行阶段 09。


## 验收阶段的机器基线门禁（强制）

- 验收时逐条核对 `baseline-binding.json` 中每条 ACTIVE 约束的最终验证状态和证据，并单独填写 `acceptance_verification`；不能简单复制 Builder 的 `implementation_verification`。例外仅在其批准范围内有效。
- 基线版本或指纹变化必须有受影响域的当前 rebase 评审；不得静默沿用旧快照。
- OpenSpec 归档/验收完成前执行 `python3 scripts/baseline-governance.py check-change --change-id <id> --phase acceptance`。

## 阶段边界与评审停等（强制）

- 开始前运行 `python scripts/workflow.py check-entry --step 10-acceptance-audit [--change-id <id>]`；退出码非 0 时立即停止并报告，不得绕过。
- 产物写完、检查通过只代表可送审：运行 `python scripts/workflow.py request-review --step 10-acceptance-audit --summary "<摘要>"`，按 `templates/workflow/step-handoff-report.md` 展示交接报告后**立即结束回合**；禁止在同一会话读取/执行下一阶段 Prompt/Skill 或创建下一阶段产物。
- 只有用户明确回复“评审通过 10-acceptance-audit”后，才可运行 `python scripts/workflow.py approve --step 10-acceptance-audit --approver "<用户>" --approved-at <YYYY-MM-DD> --evidence <审批记录>` 并执行 `transition`。不得自行填写 approver/approved_at，不得把自检通过当作批准。
- `pending_approvals` 非空时禁止推进；`workflow-state.json` 只能通过 `check-entry`/`request-review`/`approve`/`transition` 等命令管理，禁止直接编辑。
- Claude Code 的 PreToolUse hook 会拒绝写入当前阶段之后的阶段产物（共享产物除外）与直接编辑状态文件；待评审期间同样拒绝。遇到拒绝必须停止并说明，不得更换路径或禁用 hook 绕过。
