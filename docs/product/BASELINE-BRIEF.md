# 基线常驻简报（Agent 入口）

- Change ID：N/A（项目级）
- 状态：DRAFT
- 来源基线：docs/product/requirements-analysis.md、workflows.md、business-rules.md、glossary.md、acceptance-policy.md
- 关联需求/AC：FLOW/NODE/DO/BR/DEC/ASM ID
- 生成日期/版本：PENDING

> 本文件是阶段 02–05 的常驻上下文入口，必须控制在一页以内。详细内容按“读取顺序”按需加载，不得把整包基线塞入上下文。

## 1. 目标与非目标

- 产品目标：PENDING
- 业务范围：PENDING
- 明确不做（非目标）：PENDING
- 成功标准：PENDING

## 2. 角色与权限

| 角色 ID | 角色 | 核心能力 | 数据范围 | 访问级别 |
|---|---|---|---|---|
| ROLE-001 | PENDING | PENDING | PENDING | PENDING |

完整矩阵见 `role-permission-matrix.csv`；权限语义以 BR-005 为准。

## 3. 核心数据对象与不变量

| DO ID | 数据对象 | 一句话定义 | 关键不变量 |
|---|---|---|---|
| DO-001 | PENDING | PENDING | PENDING |

完整目录见 `data-objects.csv`。

## 4. 硬规则（MUST / PROHIBITED 摘要）

| BR ID | 规则摘要 | 等级 |
|---|---|---|
| BR-001 | PENDING | MUST |

完整规则、例外与执行方式见 `business-rules.md`。

## 5. 核心术语

| TERM ID | 术语 | 一句话定义 |
|---|---|---|
| TERM-001 | PENDING | PENDING |

完整术语与禁用词见 `glossary.md`。

## 6. Change 切片与完成定义

- 一个 Change 只做一个可独立验收的业务能力；优先纵向切片。
- 禁止在同一 Change 内顺手改公共契约/共享模型；需要时先走基线变更。
- 完成定义（DoD）见 `change-sizing.md`；所有 Change 必须逐项核对。

## 7. 阻塞问题与假设

| 类型 | ID | 内容 | 阻塞范围 | 负责人/到期 |
|---|---|---|---|---|
| Q | Q-001 | PENDING | PENDING | PENDING |
| ASM | ASM-001 | PENDING | PENDING | PENDING |

完整清单见 `open-questions.md`、`assumptions.md`。

## 8. 读取顺序与上下文预算

1. 本简报（≤1 页）。
2. `role-permission-matrix.csv` 与 `id-conventions.md`。
3. 本 Change 命中的 FLOW 节点表与相关 RD 行。
4. `decisions.md`、`assumptions.md`、`open-questions.md`。
5. 仅在需要时读取 `workflows.md` 全文、`data-objects.csv` 全量、`lessons.md`。
6. 架构/数据/公共契约基线按 `docs/BASELINE-FEATURE-INTERACTION.md` 的影响面读取。

## 9. 基线状态与版本

- 产品基线版本：PENDING
- 冻结状态：DRAFT
- 索引：`BASELINE-INDEX.md`（由 `scripts/gen-baseline-index.py` 生成）
- 变更方式：只通过基线修订流程；功能 Change 不直接改本文件
