# 项目基线审计报告

- 审计日期/版本：`<日期/commit>`
- 审计范围：`docs/product/`、`docs/architecture/`、`docs/adr/`
- 审计人：`<角色/姓名>`
- 建议状态：`BLOCKED | NEEDS_DECISION | READY_TO_FREEZE`

## 1. 必需产物清单

| 产物 | 路径 | 完整性 | 交叉一致性 | 结论/证据 |
|---|---|---|---|---|
| 需求业务梳理 | `docs/product/requirements-analysis.md`、`workflows.md`、`data-objects.csv`、`rd-matrix.csv`、`business-rules.md`、`glossary.md`、`acceptance-policy.md` | TODO | 节点↔RD↔DO↔BR 引用闭合 | TODO |
| 系统架构与数据流转 | `docs/architecture/system-context.md`、`domain-boundaries.md`、`containers-and-deployment.md`、`data-flows.md`、`logical-erd.md`、`technology-decisions.md` | TODO | 边界↔数据流↔ERD↔DO 一致 | TODO |
| 公共契约与 ADR | `docs/architecture/api-conventions.md`、`frontend-conventions.md`、`test-strategy.md`、`docs/adr/*` | TODO | 契约↔架构↔测试策略一致 | TODO |

## 2. 问题与风险

| ID | 严重级 | 问题/矛盾 | 影响的文档/规则 | 建议动作 | 负责人 | 阻断冻结 |
|---|---|---|---|---|---|---|
| BASELINE-GAP-001 | BLOCKER/HIGH/MEDIUM/LOW | TODO | TODO | TODO | TODO | Yes/No |

## 3. 冻结结论

- 可以冻结的基线范围：TODO
- 不允许功能提案擅自决定的事项：TODO
- 必须在功能 Change 中细化的事项：TODO
- 批准人/日期：TODO
- 下次审查触发条件：TODO
