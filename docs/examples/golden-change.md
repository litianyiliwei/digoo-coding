# 黄金样例 Change（通用参考）

- 用途：给 Agent 模仿“一份好的 Change 长什么样”，不替代 OpenSpec 模板。
- 状态：REFERENCE
- 关联：`templates/change-assets/design/baseline-impact.md`、`baseline-binding.json`、`docs/product/change-sizing.md`

> 样例刻意选一个与具体业务无关的能力（报表导出），只展示结构与追踪方式。实际 Change 以 OpenSpec schema 为准。

## 1. Change 概览

| 项 | 内容 |
|---|---|
| Change ID | `report-export` |
| 能力 | 按筛选条件导出报表 |
| 范围 | 新增导出入口、筛选参数、导出任务与结果下载 |
| 非目标 | 不做报表设计器、不做定时调度、不做新的权限模型 |
| 关联基线 | FLOW-001（示例）、BR-005（权限）、DO-001（报表数据） |
| 基线影响 | `CHANGE_ONLY`：无公共契约/共享模型变化 |

## 2. proposal.md 骨架

```markdown
## Why
用户需要在离线场景下获取报表数据，当前只能在线查看。

## What Changes
- 新增“导出报表”入口与筛选参数
- 生成导出任务并返回下载地址
- 复用现有 RBAC 与审计规则

## Capabilities
### New Capabilities
- `report-export`: 按筛选条件导出报表

## Impact
- 受影响代码：报表查询、导出任务、前端入口
- 受影响基线：BR-005（权限）、FLOW-001（示例）
- 非目标：报表设计器、定时调度
```

## 3. delta spec 骨架

```markdown
## ADDED Requirements

### Requirement: 按筛选条件导出报表
系统 SHALL 允许有权限的用户按时间范围与状态筛选报表并生成可下载文件。

#### Scenario: 正常导出
- **WHEN** 用户提交合法筛选条件
- **THEN** 系统创建导出任务并返回可下载结果

#### Scenario: 越权导出
- **WHEN** 用户没有该数据范围权限
- **THEN** 系统拒绝请求并返回统一错误模型
```

## 4. 提案级 US / AC

> 场景（原 UC）保留在 delta spec 的 Scenario 中；`design/user-stories.md` 只写 US 与 AC，避免重复规格。

`design/user-stories.md`

| US ID | 角色 | 故事/价值 | 关联 | AC |
|---|---|---|---|---|
| US-001 | ROLE-002 | 作为有权限用户，我希望导出筛选后的报表，以便离线分析 | FLOW-001;BR-005 | AC-001 |

```markdown
### AC-001
- Given：用户已登录且具备该数据范围权限
- When：提交合法筛选条件
- Then：系统创建导出任务并返回可下载结果
- 错误/边界：无权限返回统一错误；无数据返回空结果说明
```

## 5. tasks.md 骨架

```markdown
- [ ] 实现导出筛选参数与校验
- [ ] 实现导出任务与结果下载
- [ ] 补齐权限与空态 AC 的自动化测试
- [ ] 更新 baseline-binding 并完成 requirement 门禁
```

## 6. 原型与页面清单（06 阶段）

阶段 06（Figma-only）的唯一 UI 产物是 `design/figma-audit.md`：通过 Figma MCP 生成并回读真实 Figma 设计，用户在真实 Figma 稿上完成 UI 评审，并把 MCP 读取结果与 PAGE 映射落盘，作为后续界面的稳定输入。不再使用 pen.dev、prototype.pen 或 PAGE HTML。无 UI 时用 `--no-ui --reason "<原因>" --strict` 明确排除。

## 7. 详细设计（design.md 五节）

`design.md` 统一写 `## 设计决策`、`## 接口设计`、`## 前端详细设计`、`## 后端详细设计`、`## 测试设计` 五节；测试用例写入 `design/test-cases.csv`（TEST ID → AC/PAGE/BLOCK/API/IO）。有 API 时才生成 `api/openapi.yaml`、`design/api-io-mapping.csv`、`design/io-catalog.csv`，无 API 写 `x-api-scope: none`。页面/API/测试追踪合并进唯一的 `traceability.csv`。

## 8. 基线影响与绑定

`design/baseline-impact.md` 必须写明：

- 当前基线版本与各域状态；
- 固定读取项与按影响读取项；
- 适用约束 ID、复用项、冲突与归属；
- 结论：`COMPATIBLE` / `BLOCKED_PENDING_BASELINE_CHANGE` / `APPROVED_BASELINE_AMENDMENT`。

`design/baseline-binding.json` 必须覆盖全部 ACTIVE 约束，逐条填写 `APPLICABLE` / `NOT_APPLICABLE` 与理由。

## 9. 验收与回写

- 每条 AC 有测试或人工证据；阻断项清零。
- 人工验收通过后归档，并按 `lessons.md` 追加一条可复用教训（无则 N/A + 理由）。
- 只有跨功能复用价值的内容才回写基线；功能局部实现留在归档 Change。

## 10. 这个样例示范了什么

- 一个 Change 只做一件事，非目标写清楚。
- specs 的 Scenario 引用项目级 FLOW/BR/DO；每条 US 有 AC；AC 含错误/边界。
- 规格只写外部可观察行为，实现细节留给 design.md 五节。
- 原型/页面清单、详细设计、追踪矩阵各自只有一个权威载体，不重复造文件。
- 基线影响与绑定是提案的一部分，不是事后补手续。
