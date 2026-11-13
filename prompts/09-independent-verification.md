# Prompt：独立验证与验收证据

执行 `@independent-verifier`，Change：`<change-id>`。

你是独立验证者，不是 Builder。使用独立上下文核验已批准的 OpenSpec 规格、提案级 `design/user-stories.md` 中的 US/AC、`docs/product/acceptance-policy.md`、项目基线、设计契约和真实代码。源代码、测试代码、规格、设计和基线全部只读；只允许写验证报告与证据 JSON。不得修复问题或替 Builder 修改测试。

必须记录被测 Git commit/revision；如果没有 commit，记录工作区 diff 指纹，并在验证期间确认其未变化。逐条验证 AC，重新执行所有适用测试/构建/契约检查，记录命令、退出码和证据。Builder 报告仅作线索，不能代替独立执行。

方法与工具（强制）：
- 使用 Superpowers `verification-before-completion`：PASS 必须由真实命令、退出码和测试结果支撑；不得用 Builder 报告或“已看过”代替独立执行。
- 需要复现失败/定位原因时使用 `systematic-debugging`，只读排查，不修复代码、不修改测试。
- 不得使用 `requesting-code-review`/`receiving-code-review` 替代独立验证；Verifier 是审查者，不是被审查的 Builder。
- 必须独立运行 `openspec status --change <id>` 与 `openspec validate <id> --strict`，记录退出码；OpenSpec 校验失败即 FAIL/BLOCKED。

生成：
- `openspec/changes/<change-id>/design/evidence/independent-verification-report.md`
- `openspec/changes/<change-id>/design/evidence/independent-verification.json`

按 `templates/change-assets/design/independent-verification-report.md` 和 `templates/change-assets/design/independent-verification.schema.json`（若存在）填写。运行：
`python3 scripts/check-independent-verification.py --report <report-path> --evidence <json-path>`
并独立运行 `openspec status --change <id>` 与 `openspec validate <id> --strict`，记录命令、退出码和结果。

基线交互要求：验证时只读基线快照与 `design/baseline-binding.json`；发现约束未覆盖、证据缺失或实现偏离时判 BLOCKED/FAIL，不得修改代码、测试或冻结基线。
涉及 UI 时还必须独立运行 `python scripts/check-figma-layout.py --change <change-id> --base-url <url> --viewport 1440x900` 与 `python scripts/check-design-tokens.py --change <change-id> --tokens <token.css>`，并从独立重跑结果生成报告 `## UI 一致性验证` 与 JSON `layout_checks`（逐 PAGE 断言元素数、最大偏差、容差、缺失元素、判定与证据）。**人工视觉抽查只针对有差异、`UI-DERIVED` 或未纳入断言的 PAGE**，记录抽查 PAGE、原因与结论；无差异且机器 PASS 的 PAGE 不做逐页视觉复核。参考图/实现截图不再作为证据；缺失断言、元素缺失、几何/文本/字体超差或 token 不一致时判 BLOCKED/FAIL。默认离线消费导出包，仅在文件版本变化或页面有歧义时按页抽查真实 Figma（串行、避免限流），不得全量重复读取。**有 `differences` 记录但未 `deviation_approved` 时不得 PASS。**

只有所有适用 AC 均有通过证据、所有必需测试真实执行且退出码为 0、无阻断发现、revision 稳定时才可判定 PASS。任何 NOT_RUN / SKIPPED / PENDING 都不能算通过。FAIL 或 BLOCKED 时明确退回原因，不得进入阶段 10。不得归档 OpenSpec，不得更新基线，不得提交或发布代码。

## 强制交付物交接

- 输入：阶段 08 的代码差异、测试报告、审查结论、批准规格、AC、基线快照、设计和测试契约、`design/test-cases.csv`；涉及 UI 时 `design/figma-audit.md`（目标框架/转码说明、token 实际值/PAGE 规格/状态决策）、`design/figma-code/`（目标框架设计代码）、`design/figma-layout.csv`（断言映射）、`design/evidence/figma-layout-check.json` 与 `design/evidence/code-review.md` 的 `## UI fidelity` 数值证据；`docs/product/acceptance-policy.md`；`docs/product/open-questions.md`（只读；未决问题不得在验证中擅自关闭）。
- 输出：独立验证 Markdown 报告和 JSON 证据，必须位于当前 Change 的 `design/evidence/`；涉及 UI 时 JSON 的 `layout_checks` 必须覆盖每个 PAGE（Figma node、断言元素数、最大偏差/容差、缺失元素、判定、证据），报告必须含 `## UI 一致性验证`，并记录人工抽查 PAGE/原因（仅差异、`UI-DERIVED` 或未断言 PAGE）。
- 下游输入：阶段 10 只读取 PASS 的验证报告、AC 证据、测试退出码、发现项、`layout_checks` 和 revision。
- 交接：生成 `templates/workflow/step-handoff-report.md`；调用 `scripts/workflow.py transition` 生成 SHA-256 manifest 并推进状态。
- 状态：只有 `check-independent-verification.py` 退出码为 0，且阶段 evidence 的 gate check 记录该命令真实退出码 0，才允许完成阶段；涉及 UI 时 `layout_checks` 必须全部 PASS，且 `test_runs` 包含独立重跑的 `check-figma-layout.py` 退出码 0。
- 方法证据：阶段 evidence 的 checks 必须记录 `superpowers-verification-methods`（verification-before-completion / systematic-debugging 的实际使用与证据）和 `openspec-validate-independent`（status/validate 的命令、退出码与日志）。

- **阶段边界（强制）：** 阶段完成 ≠ 可进入下一阶段。产物写完、检查通过后运行 `python scripts/workflow.py request-review --step 09-independent-verification --summary "<送审摘要>"`（流程冻结为待评审），按交接模板展示报告后**立即结束回合**；用户明确回复“评审通过 09-independent-verification”前，禁止读取/执行下一阶段 Prompt/Skill、禁止创建下一阶段产物。批准后运行 `python scripts/workflow.py approve --step 09-independent-verification --approver "<用户>" --approved-at <YYYY-MM-DD> --evidence <审批记录>`，再执行 `transition`。不得自行填写 approver/approved_at，不得把产物完成或自检通过当作批准。
- 仅在门禁通过且审批完成后更新 `workflow-state.json`；不得自动跨越审批点。

## 独立基线约束验证（必须执行）

独立核验 Manifest、Constraint Registry 和 Change binding；逐条检查实际代码/配置/迁移/接口，不能直接采信 Builder 的 PASS。将约束 ID、独立检查结果和证据纳入报告，并运行 `python3 scripts/baseline-governance.py check-change --change-id <id> --phase implementation`。
