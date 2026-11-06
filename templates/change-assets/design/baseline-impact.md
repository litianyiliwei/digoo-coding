# 功能 Change 基线适用性与影响清单

- Change ID：`<change-id>`
- 状态：DRAFT / REVIEW / APPROVED / BLOCKED
- 建立阶段：05-feature-requirements
- 最后复核阶段：
- 当前基线版本：
- 关联 US / AC / BR / FLOW / UC：

## 1. 基线状态快照

| 基线域 | 当前版本 | 状态 | 审批人/生效日期 | 本 Change 是否涉及 |
|---|---|---|---|---|
| 产品 | | FROZEN / DRAFT / STALE | | YES / NO |
| 架构 | | FROZEN / DRAFT / STALE | | YES / NO |
| 数据与领域 | | FROZEN / DRAFT / STALE | | YES / NO |
| 公共 API | | FROZEN / DRAFT / STALE | | YES / NO |
| 前端工程 | | FROZEN / DRAFT / STALE | | YES / NO |
| 测试与质量 | | FROZEN / DRAFT / STALE | | YES / NO |

## 2. 固定读取项核验

| 基线文件 | 版本/更新时间 | 适用章节/ID | 读取状态 | 与本功能的约束/影响 |
|---|---|---|---|---|
| `docs/architecture/baseline-status.md` | | | READ / MISSING | |
| `docs/product/acceptance-policy.md` | | | READ / MISSING | |
| `docs/product/glossary.md` | | | READ / MISSING | |
| 相关产品需求/流程/用例/故事/业务规则 | | | READ / N/A / MISSING | |
| `docs/architecture/system-context.md` | | | READ / MISSING | |
| `docs/architecture/domain-boundaries.md` | | | READ / MISSING | |
| 相关 `openspec/specs/**` | | | READ / N/A / MISSING | |

## 3. 按影响读取项核验

| 影响面 | 必须读取的基线文件 | 相关章节/ID | 版本 | 约束摘要/设计影响 |
|---|---|---|---|---|
| 数据/实体/事务 | logical-erd / domain-boundaries / data-flows | | | |
| 服务/模块/集成/部署 | system-context / containers-and-deployment / technology-decisions / ADR / data-flows | | | |
| HTTP API/鉴权/外部集成 | api-conventions / security decisions | | | |
| 页面/路由/组件/状态 | frontend-conventions / design system | | | |
| NFR/质量/可观测性 | test-strategy / relevant ADR / deployment constraints | | | |
| 共享角色/业务规则/流程 | relevant product baseline / permission model | | | |

## 4. 复用与一致性映射

| 当前功能设计项 | 复用的基线能力/组件/实体/规则 | 来源文件与版本 | 处理方式 |
|---|---|---|---|
| | | | REUSE / EXTEND / REPLACE（REPLACE 必须审批） |

## 5. 变化归属判定

| 发现/变化 | 分类 | 判定依据（局部/跨功能/公共约束） | 权威落点 | 是否影响其他 Change |
|---|---|---|---|---|
| | CHANGE_ONLY / BASELINE_CHANGE_REQUIRED / BASELINE_UPDATE_AFTER_ACCEPTANCE / N/A | | | |

## 6. 基线冲突、缺口与候选修订

| ID | 冲突/缺口 | 影响域 | 候选方案/ADR | 受影响功能/Change | 责任人 | 审批状态 |
|---|---|---|---|---|---|---|
| | | | | | | PENDING / APPROVED / REJECTED |

## 7. 在途 Change 版本复核

| 在途 Change | 引用基线版本 | 当前基线版本 | 影响分析 | 结论 |
|---|---|---|---|---|
| | | | | NO_IMPACT / REBASE_REQUIRED / BLOCKED |

## 8. 结论与门禁

- 本 Change 基线分类：CHANGE_ONLY / BASELINE_CHANGE_REQUIRED / BASELINE_UPDATE_AFTER_ACCEPTANCE / N/A
- 总体结论：COMPATIBLE / BLOCKED_PENDING_BASELINE_CHANGE / APPROVED_BASELINE_AMENDMENT
- 是否允许进入详细设计：YES / NO
- 是否允许进入实现：YES / NO
- 必须先完成的基线修订：
- 审批人及证据：
- 下一次复核时机：13a 详细设计 / 14 实施发现 / 15 验收归档

> 规则：如果基线变更会影响当前功能的架构、数据模型、公共契约或测试门禁，必须先批准并更新基线，再冻结详细设计和实现计划。不得把 `PENDING` 当作批准。
