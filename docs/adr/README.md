# Architecture Decision Records

- Change ID：N/A（项目级架构基线）
- 状态：FROZEN（v0.2.2；ARCH-STATUS-002 已批准）
- 来源基线：`docs/product/decisions.md`、Stage 03 architecture baseline
- 关联需求/AC：RA-001、NFR-001、FLOW-001、DO-001–005
- 生成日期/版本：2026-11-17 / v0.2.2

本仓库采用索引式 ADR；已批准决策正文放在 `docs/architecture/technology-decisions.md`，单独登记决策 ID、状态、权衡和确认人。需独立评审或演进时再拆分单文件 ADR。

| ADR ID | 决策 | 状态 | 日期 | 备注 |
|---|---|---|---|---|
| ADR-001 | 现有 AI coding 流程工具包范围和技术基线 | APPROVED | 2026-11-17 | 用户批准并冻结 v0.2.0 基线 |
| ADR-002 | 无业务运行期 API；列出 GitHub/Figma/公开资料工具时边界 | APPROVED | 2026-11-17 | 条件性外部依赖见 technology-decisions.md |
| ADR-003 | 本地文件状态、原子写和哈希交接 | APPROVED | 2026-11-17 | 受并发规模限制；本地单仓库适用 |

## 决策状态说明

- `PROPOSED`：方案已提出，待负责人审批。
- `APPROVED`：由负责人明确批准并生效。
- `DEFERRED`：暂缓，记录前置条件。
- `SUPERSEDED`：由后续 ADR 取代。
