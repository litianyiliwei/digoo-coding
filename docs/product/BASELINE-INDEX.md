# 基线索引（自动生成）

> 本文件由 `scripts/gen-baseline-index.py` 生成，禁止手改。运行 `python scripts/gen-baseline-index.py --write` 更新；`--check` 校验是否过期。

| 产物 | 路径 | 状态/规模 | 用途 |
|---|---|---|---|
| 基线常驻简报 | `docs/product/BASELINE-BRIEF.md` | DRAFT | 阶段 02–05 常驻入口 |
| 需求业务梳理 | `docs/product/requirements-analysis.md` | DRAFT | 目标、范围、角色、假设与决策索引 |
| 业务流程 | `docs/product/workflows.md` | DRAFT | 主流程、替代流程、异常流程节点表 |
| 业务数据对象 | `docs/product/data-objects.csv` | 0 个 DO | 业务概念目录，不是数据库表 |
| RD 矩阵 | `docs/product/rd-matrix.csv` | 0 条 RD | 节点→角色→DO→访问类型→验证意图 |
| 业务规则 | `docs/product/business-rules.md` | DRAFT | 全局与功能级规则，含等级/执行方式 |
| 术语表 | `docs/product/glossary.md` | DRAFT | 统一词汇与禁用词 |
| 未决问题 | `docs/product/open-questions.md` | DRAFT | 未决问题、责任人、阻塞条件 |
| 角色权限矩阵 | `docs/product/role-permission-matrix.csv` | 1 行 / ROLE 1 / CAP 1 | 提案级权限 AC 的锚点 |
| 切片与 DoD | `docs/product/change-sizing.md` | DRAFT | Change 预算、拆分信号与完成定义 |
| 决策日志 | `docs/product/decisions.md` | DRAFT | 防止重复争论已决问题 |
| 假设登记 | `docs/product/assumptions.md` | DRAFT | 假设、验证方式、到期点与责任人 |
| 教训/反模式 | `docs/product/lessons.md` | DRAFT | 验收后回写的可复用失败模式 |
| ID 约定 | `docs/product/id-conventions.md` | DRAFT | 项目级/Change 级 ID 与并行分配规则 |
| 验收政策 | `docs/product/acceptance-policy.md` | DRAFT | AC 格式、测试映射、阻断项与证据要求 |
| 基线状态 | `docs/architecture/baseline-status.md` | DRAFT | 各基线域版本、冻结状态与审批 |

## 当前缺口

- `data-objects.csv` 仅有表头。
- `rd-matrix.csv` 仅有表头。

## 生成规则

- 索引只汇总路径、状态与数量，不复制基线内容。
- 产物缺失时在状态列标注“缺失”；不得用空文件满足检查。
- 状态变化或新增产物后重新生成；`--check` 失败视为基线漂移。
