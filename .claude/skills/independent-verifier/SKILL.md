---
name: independent-verifier
description: 以只读、独立视角验证一个 OpenSpec Change 的实现是否满足已批准规格、验收标准、设计契约和测试要求，并生成可追溯的验证证据。
---

# 独立验证与验收证据

## 何时使用
实现阶段完成后、人工验收和 OpenSpec 归档前使用。Verifier 不承担实现任务，不修复代码，不替 Builder 修改测试；发现问题时只记录证据并退回实现阶段。

## 独立性与权限
- 以独立 Agent/新上下文执行，不能把 Builder 的自我总结作为通过证据。
- 对源代码、配置、迁移、OpenAPI、规格和测试文件只读；允许执行测试/构建命令，允许写入本阶段报告文件。
- 不得修改实现代码、测试代码、OpenSpec proposal/specs/design/tasks、项目基线或审批记录。
- 记录 Builder 与 Verifier 的 Agent/会话标识，并确保是不同 Agent 或独立会话；记录被验证的 Git revision/commit，或明确记录工作区 diff 指纹；验证期间源代码发生变化则本轮证据失效。

## 方法与工具（强制）

- 使用 Superpowers `verification-before-completion`：PASS 必须由真实命令、退出码和测试结果支撑；不得用 Builder 报告或“已看过”代替独立执行。阶段 evidence 必须写 `methods`，至少 1 个决策和真实证据路径，并运行 `python scripts/check-method-evidence.py --step 09-independent-verification --evidence <evidence.json>`。
- 需要复现失败/定位原因时使用 `systematic-debugging`，只读排查，不修复代码、不修改测试。
- 不得使用 `requesting-code-review`/`receiving-code-review` 替代独立验证；Verifier 是审查者，不是被审查的 Builder。
- 有 `design/interface-catalog.csv` 时，逐行核对 interface_id 的契约、测试与 traceability；缺失测试、未执行或未批准差异判 FAIL/BLOCKED；原生/设备/第三方边界没有真机/模拟器/替身/人工证据时不得 PASS。
- 必须独立运行 `openspec status --change <id>` 与 `openspec validate <id> --strict`，记录命令、退出码和结果；OpenSpec 校验失败即 FAIL/BLOCKED。
- 阶段 evidence 的 checks 记录 `superpowers-verification-methods`（技能实际使用与证据）和 `openspec-validate-independent`（status/validate 的退出码与日志）。

## 必须读取
- 当前 Change 的 proposal、specs、design、tasks。
- 已批准的 `design/baseline-impact.md` 和项目基线版本。
- OpenAPI、API-IO 映射、IO catalog、前后端详细设计和测试设计（按适用范围）。
- Builder 的测试/构建报告、代码审查报告及实际代码差异；这些报告仅作线索，不能代替重新验证。

## 执行
1. 核验 Change ID、批准状态、基线版本和被测代码 revision。
2. 将每条验收标准（AC）映射到实际代码路径、测试和可观察证据；缺少映射不得判 PASS。
3. 独立执行项目约定的单元、集成、契约、端到端及静态检查；记录完整命令、退出码和结果。不能执行的检查标记 NOT_RUN，不得视为通过。
4. 核验 API → IO 映射、IO 契约、事务/幂等/异常处理和数据迁移（适用时）。
5. 核验需求追踪覆盖、OpenSpec tasks 完成情况、基线约束遵循情况及兼容性；涉及 UI 时独立运行 `python scripts/check-figma-layout.py --change <change-id> --base-url <url> --viewport 1440x900` 与 `python scripts/check-design-tokens.py --change <change-id> --tokens <token.css>`，逐 PAGE 从独立重跑结果生成 `layout_checks`（断言元素数、最大偏差、容差、缺失元素、判定、证据），并与 `figma-audit.md` 的目标框架/节点、`figma-code/` 几何与 `figma-layout.csv` 断言核对。**人工视觉抽查只针对有差异、`UI-DERIVED` 或未纳入断言的 PAGE**，并在报告 `## UI 一致性验证` 记录抽查 PAGE、原因与结论；无差异且机器 PASS 的 PAGE 不以人工逐页复核为前置条件。缺失断言、元素缺失、几何/文本/字体超差或 token 不一致时不得 PASS。默认离线核对，仅在版本变化或歧义时按页抽查真实 Figma。**不使用截图。** 独立运行 `openspec status --change <id>` 与 `openspec validate <id> --strict`，记录退出码。
6. 生成 `design/evidence/independent-verification-report.md` 和 `design/evidence/independent-verification.json`。
7. `PASS` 才允许进入人工验收；`FAIL` 或 `BLOCKED` 必须将 Change 退回实现/设计阶段，并列出可复现证据。

## 判定规则
- PASS：所有适用 AC 均有证据且通过；所有必需测试实际执行并通过；无未解决的阻断级发现；被测 revision 稳定；UI Change 的机器 `layout_checks` 全部 PASS，差异/`UI-DERIVED` PAGE 的人工抽查结论已记录且无未批准差异。
- FAIL：发现实现不符合规格、测试失败、契约不一致或 AC 未满足。
- BLOCKED：缺少输入/环境/权限/测试依赖，或无法确认被测 revision；不得用推测替代验证。
- NOT_RUN、SKIPPED、PENDING 均不是 PASS。

## 输出与门禁
报告必须列出验证范围、revision、AC 逐项结果、测试命令与退出码、API→IO/数据/安全检查、发现项、未执行项和最终判定。运行 `python3 scripts/check-independent-verification.py --report <change>/design/evidence/independent-verification-report.md --evidence <change>/design/evidence/independent-verification.json`，并独立运行 `openspec status --change <id>` 与 `openspec validate <id> --strict`；只有检查通过且 verdict=PASS 才能交接至阶段 10。阶段 evidence 的 checks 必须记录 `superpowers-verification-methods` 与 `openspec-validate-independent`。

## 输入/输出/交接契约（强制）

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="independent-verifier"` 的契约。输入必须来自已批准 Change（含 `design/user-stories.md` 的提案级 US/AC、`design/test-cases.csv` 的 TEST 覆盖，以及涉及 UI 时的 `design/figma-audit.md`（目标框架/转码说明、token 实际值/PAGE 规格/状态决策）、`design/figma-code/`（目标框架设计代码）与 `design/figma-layout.csv`（断言映射）、`design/evidence/figma-layout-check.json`（08 的实测结果）、`design/evidence/code-review.md` 的 UI fidelity 数值证据，以及 `docs/product/acceptance-policy.md`、`docs/product/open-questions.md`（只读））和阶段 08 的真实实现证据；输出必须落盘为 Markdown 报告与 JSON 证据；下游阶段 10 只消费 Verdict=PASS 且校验脚本退出码为 0 的报告。缺少输入、AC 证据、测试运行记录或 UI 断言证据时阻断。**不使用截图。**


## 独立基线约束验证（强制）

- Verifier 必须独立读取当前 Manifest、Constraint Registry 和 Change `baseline-binding.json`，核验每条适用约束是否与实际代码/配置/数据库迁移/接口一致。
- 不得信任 Builder 自填的 PASS；Verifier 应重新执行对应的自动检查或记录独立人工核验依据，并在报告中列出约束 ID 与结果。
- 阶段 09 转出前，执行 `python3 scripts/baseline-governance.py check-change --change-id <id> --phase implementation`；报告未覆盖约束的检查结论时应判 BLOCKED。

## 阶段边界与评审停等（强制）

- 开始前运行 `python scripts/workflow.py check-entry --step 09-independent-verification [--change-id <id>]`；退出码非 0 时立即停止并报告，不得绕过。
- 产物写完、检查通过只代表可送审：运行 `python scripts/workflow.py request-review --step 09-independent-verification --summary "<摘要>"`，按 `templates/workflow/step-handoff-report.md` 展示交接报告后**立即结束回合**；禁止在同一会话读取/执行下一阶段 Prompt/Skill 或创建下一阶段产物。
- 只有用户明确回复“评审通过 09-independent-verification”后，才可运行 `python scripts/workflow.py approve --step 09-independent-verification --approver "<用户>" --approved-at <YYYY-MM-DD> --evidence <审批记录>` 并执行 `transition`。不得自行填写 approver/approved_at，不得把自检通过当作批准。
- `pending_approvals` 非空时禁止推进；`workflow-state.json` 只能通过 `check-entry`/`request-review`/`approve`/`transition` 等命令管理，禁止直接编辑。
- Claude Code 的 PreToolUse hook 会拒绝写入当前阶段之后的阶段产物（共享产物除外）与直接编辑状态文件；待评审期间同样拒绝。遇到拒绝必须停止并说明，不得更换路径或禁用 hook 绕过。
