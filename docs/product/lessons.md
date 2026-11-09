# 教训与反模式

- Change ID：N/A（项目级）
- 状态：BASELINE v1.0（2026-11-09 基线优化）
- 来源基线：阶段 02 复核、已验收 Change 的验收记录
- 关联需求/AC：LESSON ID ↔ 来源 Change/AC ID
- 生成日期/版本：2026-11-09

> 每个 Change 验收后追加；只记录可复用的失败模式和改进规则，不记录个人评价。

| LESSON ID | 触发场景 | 现象 | 根因 | 规则/改进 | 适用阶段 | 来源 Change | 日期 |
|---|---|---|---|---|---|---|---|
| LESSON-001 | 阶段 02 交接阶段 05 | 基线只有流程叙述，无 NODE 节点表、DO 目录与 RD 矩阵，提案级需求没有可引用的锚点 | 先写叙述、后补机器产物 | 阶段 02 先产出最小 NODE/DO/RD 集，再写叙述；`check-requirements.py` 未通过不得交接 | 02/05 | N/A（流程优化） | 2026-11-09 |
| LESSON-002 | 基线索引维护 | `requirements-analysis.md` 把历史 UC/US 列为 APPROVED 产物，与实际职责不符 | 手写索引且未随重构更新 | 索引由 `scripts/gen-baseline-index.py` 生成，禁止手改 | 02 | N/A（流程优化） | 2026-11-09 |
