# Code Review Evidence

- Change ID: TODO
- Reviewer/tool: TODO
- Review date/commit: TODO
- Review conclusion: TODO（PASS / APPROVED / NO_BLOCKING_FINDINGS；FAIL/BLOCKED 不得转出阶段 08）
- Findings: TODO（none，或在下方逐条列出）

## Findings by severity

| Severity | File/line | Finding | Resolution/evidence | Status |
|---|---|---|---|---|
| TODO | TODO | TODO | TODO | Pending |

> 无发现项时删除上表数据行，并把 `- Findings:` 改为 `none`；状态只能使用 fixed/resolved/closed/accepted/risk-accepted/n/a/none。

## Spec compliance, security, data consistency, failure paths

TODO

## UI fidelity

> 涉及 UI 时必填；无 UI 时删除本节并写 `- UI fidelity: N/A（无 UI）`。
> 机器证据是 `evidence/figma-layout-check.json`（由 `scripts/check-figma-layout.py` 在 1440×900 视口实测），不使用截图。
> 路径相对 Change 的 `design/` 目录；`断言元素/最大偏差` 必须直接从 JSON 的 `element_count` / `max_delta_px` 抄录，不是人工估算。
> **UI 验证以机器证据为主**：无差异 PAGE 的 `审查方式` 写“机器证据”；只有存在差异或 `UI-DERIVED` 的 PAGE 才写“人工复核”，并在 `差异` 列给出原因与审批人。

| PAGE | Figma node | 断言元素/最大偏差 | 布局证据 | 差异 | 结论 | 审批人 | 审查方式 |
|---|---|---|---|---|---|---|---|
| PAGE-001 | `3:2` | `8 elements / 0.0px (tol 2px)` | `evidence/figma-layout-check.json#PAGE-001` | 无 | PASS | — | 机器证据 |

> 结论只允许 PASS / FIXED / APPROVED / DEVIATION_APPROVED / N/A；有差异时必须是 DEVIATION_APPROVED 并写明审批人，否则阻断阶段 08。
