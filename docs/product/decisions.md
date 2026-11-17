# 决策日志

- Change ID：N/A（项目级）
- Status: FROZEN (product baseline v0.3.0)
- Source baseline: 用户阶段审批和当前流程工具检查
- Related requirements/AC: DEC-001–005 ↔ BR-001/003/006/007/FLOW-001/NODE-001-02/04/07
- Generated date/version: 2026-11-17 / v0.3.0

> 只登记已作出的决策；未决问题留在 `open-questions.md`。本阶段提出的其他参数仍等待评审。

| DEC ID | 决策 | 理由/权衡 | 来源（Q/会议/ADR） | 影响 ID | 决定日期 | 决策人 | 状态 |
|---|---|---|---|---|---|---|---|
| DEC-001 | 包结构检查只做结构/契约/语法校验；回归测试通过独立命令运行 | 避免 bootstrap 门禁意外运行完整回归集，减少启动耗时并明确职责 | 阶段 01 用户评审；`workflow/evidence/approval-01-project-bootstrap-2026-11-16.md` | FLOW-001/NODE-001-04/BR-006 | 2026-11-16 | 用户 | APPROVED |
| DEC-002 | 默认上下文预算为最多 8 个读取组、12,000 字符 | 以任务相关性压缩常驻输入；超限按理由审批 | 用户澄清 | NFR-001/BR-001 | 2026-11-16 | 用户 | APPROVED |
| DEC-003 | 低风险变更可采用定向检查，但审批和必要硬门禁保留 | 减少不相关检查而不降低不可豁免的安全与治理约束 | 用户澄清 | BR-003/BR-006/FLOW-001/NODE-001-07 | 2026-11-16 | 用户 | APPROVED |
| DEC-004 | 优先以减少默认上下文和重复产物衡量流程优化效果 | 这是用户明确选择的首要成效指标；交付时长与正确率作为护栏观察 | 用户澄清 | RA-001/NFR-001/BR-001/BR-002 | 2026-11-16 | 用户 | APPROVED |
| DEC-005 | 采用已批准的 LOW/STANDARD/HIGH 风险判级及检查矩阵；HIGH 信号优先，不确定时升级；档位不得豁免用户审批、状态完整性、冻结基线审批、适用安全/权限检查或必要独立验证；规则基线先行，自动选择器后续实现 | 解决 Q-003 并解除策略定义与自动化实现之间的循环依赖；`workflow-context-bundles` 判为 HIGH 并运行全仓回归 | BCR-Q003-RISK-TIER-POLICY；用户批准 | Q-003/BR-003/BR-006/BR-007/FLOW-001 | 2026-11-17 | 用户 | APPROVED |

- 状态枚举：`APPROVED`、`SUPERSEDED`、`RETIRED`。
- 决策变更时必须新增 DEC 行并标记旧行 `SUPERSEDED`，不得改写历史。
