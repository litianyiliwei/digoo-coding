# 项目基线状态与版本登记

- Change ID：N/A（项目级）
- 状态：FROZEN（BCR-Q003-RISK-TIER-POLICY 已批准并于 2026-11-17 重冻）
- 来源基线：Stage 02 已审批需求基线；Stage 03 架构草案
- 关联需求/AC：RA-001、NFR-001、FLOW-001、DO-001–005、BR-001–007
- 生成日期/版本：2026-11-17 / v0.3.0

- 项目名称：项目 AI coding 流程工具包
- 总体基线版本：`v0.3.0`
- 总体状态：FROZEN
- 最近生效日期：2026-11-17
- 产品/架构/技术负责人：用户/项目负责人（用户于 2026-11-17 确认）
- 基线仓库版本/Commit：main / `91aab8e0f909921082a5096c0d3ac14e735baf18`（工作区内容由基线 SHA-256 绑定；未自动提交）

> 机器权威来源：`baseline-manifest.json`；约束权威来源：`constraint-registry.json`。本文件仅为可读镜像。

## 1. 各基线域版本

| 基线域 | 权威文件 | 版本 | 状态 | 审批人 | 生效日期 | 最近关联 Change / ADR |
|---|---|---|---|---|---|---|
| 产品 | `docs/product/requirements-analysis.md`、workflows、DO、RD、business-rules、glossary、acceptance-policy | v0.3.0 | FROZEN | user | 2026-11-17 | BCR-Q003-RISK-TIER-POLICY |
| 架构 | system-context、domain-boundaries、containers、data-flows、technology-decisions、ADR index | v0.2.2 | FROZEN | user | 2026-11-17 | ADR-001–003 APPROVED |
| 数据与领域 | logical-erd、domain-boundaries、data-flows | v0.2.2 | FROZEN | user | 2026-11-17 | N/A |
| 公共 API/CLI | `docs/architecture/api-conventions.md` | v0.2.0 | FROZEN | user | 2026-11-17 | N/A |
| 前端工程 | `docs/architecture/frontend-conventions.md` | v0.2.0 | FROZEN | user | 2026-11-17 | N/A |
| 测试与质量 | `docs/architecture/test-strategy.md` | v0.3.0 | FROZEN | user | 2026-11-17 | BCR-Q003-RISK-TIER-POLICY |

## 2. 生效规则

FROZEN 域仅在负责人完成审阅、批准、证据登记和哈希检查后作为强制规范；DRAFT 域不代表已批准约束。基线修订需记录版本、理由、批准人、证据和受影响 Change。

## 3. 版本策略

- PATCH：不改规范语义的澄清/修正。
- MINOR：新增兼容规则、实体或公共约定。
- MAJOR：改变系统边界、数据所有权、公共契约或兼容性。

## 4. 当前待处理项

| ID | 影响域 | 摘要 | 状态 | 负责人 |
|---|---|---|---|---|
| Q-003 | 产品 / 测试与质量 | 风险判级矩阵及最低检查集 | RESOLVED; BCR-Q003-RISK-TIER-POLICY frozen in v0.3.0 | 用户 / 技术质量负责人 |
| ARCH-STATUS-001 | 架构 | 将文件状态与已冻结批准事实同步；不改变规范语义 | RESOLVED；v0.2.1 于 2026-11-17 获批 | 用户/项目负责人 |

## 5. 冻结批准记录

| 基线版本 | 审批范围 | 审批人 | 日期 | 证据/会议记录 |
|---|---|---|---|---|
| v0.2.0 | 流程工具包架构与 12 项约束 | user | 2026-11-17 | `workflow/evidence/approval-baseline-v0.2.0-2026-11-17.md` |
| v0.2.1 | ARCH-STATUS-001 状态元数据同步 | user | 2026-11-17 | `workflow/evidence/approval-baseline-amendment-ARCH-STATUS-001-2026-11-17.md` |
| v0.2.2 | ARCH-STATUS-002 生效日期及目录状态同步 | user | 2026-11-17 | `workflow/evidence/approval-baseline-amendment-ARCH-STATUS-002-2026-11-17.md` |
| v0.3.0 | BCR-Q003-RISK-TIER-POLICY：风险判级与验证矩阵（product + test_quality） | user | 2026-11-17 | `workflow/evidence/approval-BCR-Q003-RISK-TIER-POLICY-2026-11-17.md` |

## 6. 冻结操作

用户于 2026-11-17 批准并冻结 v0.2.0；ARCH-STATUS-001/002 已按基线修订流程完成。BCR-Q003-RISK-TIER-POLICY 经用户批准，product 与 test_quality 升级至 v0.3.0，哈希刷新并重冻。冻结后的修改须通过 open-amendment。
