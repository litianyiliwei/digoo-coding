# Change 基线约束绑定与验证记录

机器权威文件：`design/baseline-binding.json`。本文件用于人工审阅摘要，不替代 JSON，也不能单独作为通过证据。

## 使用规则

1. 创建 Change 后运行 `python3 scripts/baseline-governance.py init-binding --change-id <change-id>`，从当前冻结基线和 ACTIVE 约束目录生成 JSON 初稿。
2. 阶段 05 为每条约束填写 `applicability`（APPLICABLE / NOT_APPLICABLE）和理由；不得删除约束行。N/A 必须给出具体理由。
3. 对适用约束，在设计阶段填写 `decision`（COMPLIANT / EXCEPTION_APPROVED）、`design_evidence`；例外必须同时填写审批人、批准日期、范围、理由和证据路径。
4. 实现阶段补充 `implementation_verification`：PASS 或有理由的 NOT_APPLICABLE，并给出真实证据文件路径。PENDING、NOT_RUN、SKIPPED 不得算通过。
5. 验收阶段另行补充 `acceptance_verification`：必须基于验收/独立验证结果重新确认约束遵守情况；不能简单复制实现阶段的 PASS。每条适用约束需 PASS、方法和真实验收证据；N/A 需给理由。
6. 项目基线更新时，按域填写 `rebase_reviews`；总体版本变化还必须填写 `rebase_reviews.overall`。NO_IMPACT 要有当前版本、当前 fingerprint、审核人和证据；需要改变设计的情况必须对总体和受影响域完成重新设计并记录 REBASE_COMPLETED，再执行 `refresh-binding`。
7. `approval` 由有权负责人填写，审批人不得由 AI 自行虚构。脚本只验证审批记录结构与证据存在，不提供身份认证或电子签名。

## 检查命令

- 阶段 05：`python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase requirement`
- 详细设计：`python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase design`
- 实现交接：`python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase implementation`
- 验收归档：`python3 scripts/baseline-governance.py check-change --change-id <change-id> --phase acceptance`

约束目录中的规则以 `docs/architecture/constraint-registry.json` 为唯一机器可读清单。修改约束、约束状态或来源关系，都必须走项目基线修订流程，不能只改本 Change 的绑定文件。
