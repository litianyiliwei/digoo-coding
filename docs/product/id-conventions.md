# ID 命名与分配约定

- Change ID：N/A（项目级）
- Status: READY_FOR_REVIEW
- Source baseline: `docs/TEMPLATE-POLICY.md`、阶段模板和本阶段产物
- Related requirements/AC: RA/NFR/FLOW/NODE/DO/RD/BR/TERM/Q/DEC/ASM/ROLE/CAP/LESSON IDs
- Generated date/version: 2026-11-16 / v0.2.0-draft

## 1. 两层 ID

| 层级 | 前缀 | 示例 | 分配者 | 作用域 |
|---|---|---|---|---|
| 项目级 | RA/NFR/FLOW/NODE/DO/RD/BR/TERM/Q/DEC/ASM/CAP/LESSON/ROLE | RA-001、NFR-001、FLOW-001、NODE-001-01、DO-001 | 阶段 02/03 基线负责人 | 全项目 |
| Change 级 | US/AC/TEST/PAGE/BLOCK/ELEM/EVT/IO/TASK | US-001、AC-001、TEST-001 | 当前 Change | 该 Change 内唯一 |

## 2. 并行分配规则

- 项目级 ID 只在基线阶段分配；功能 Change 不得新建或复用项目级 ID。
- Change 级 ID 在该 Change 内唯一；跨 Change 引用必须带 Change 前缀，例如 `report-export:US-001`。
- 不得把 Change 级 ID 登记到 `docs/product/` 基线文档；需要提升时先走基线变更并分配项目级 ID。
- 不得复用已退役 ID；退役时在来源文档标记 `RETIRED` 并保留原行。
- 并行工作先按不同 ID 范围分配负责人；合并前检查重复项。

## 3. 引用闭合

- 每个引用必须指向真实存在的 ID；未知引用由 `check-requirements.py` 判定。
- 改名/重排不改变 ID；措辞修订保留原 ID 并记录版本。
- 新增 ID 前先搜索现有文档，避免语义重复；表格引用使用分号分隔多个 ID。
