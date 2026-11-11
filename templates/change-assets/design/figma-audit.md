# Figma MCP 读取快照与 UI 评审

- Change ID：`<change-id>`
- Figma 文件/页面：`<真实 Figma 链接或 fileKey>`
- 检查时间/版本：`<时间、revision 或导出版本>`
- UI 基线版本：Figma 评审稿 + `design/figma-audit.md`（页面集合由本阶段冻结）
- 审核人/状态：`<姓名或角色 / DRAFT|APPROVED>`

> 阶段 06（Figma-only）以已批准需求与 `frontend-conventions` 第 9 节为输入；真实 Figma 评审稿是视觉/结构与组件/变量的最终权威。
> 本文件是 Figma MCP 实际读取结果的落盘快照，也是 07/08/09/10 的界面输入。
> 后续阶段可重新读取真实 Figma 时以实时读取为准；不可访问时以本快照为稳定输入，不得臆造。
> 无 UI 时：在“设计来源与选择”写入 `- 设计来源状态：N/A` 与 `- 无 UI 理由：<原因>`；无需填写 Figma/MCP/节点映射章节。

## 设计来源与选择

- 设计来源状态：DRAFT
- 设计来源选择：Figma MCP AI 自动设计（人工 Figma 设计仅在用户明确选择时）

| 项 | 内容 |
|---|---|
| 设计来源选择 | Figma MCP AI 自动设计 / 人工 Figma 设计（二选一，默认前者） |
| 选择人/日期 | PENDING |
| PAGE 清单 | 由本阶段从已批准需求冻结的 PAGE-001… 清单；07–10 不得新增或重命名 |
| 设计状态 | DRAFT / BLOCKED / APPROVED |
| 说明 | 无论设计来源，都必须通过 Figma MCP 读取真实 Figma 文件/节点/组件/变量并完成 UI 评审；不得用截图或臆造替代 |

## 设计输入与风格参考

> 输入是已批准需求/AC 与产品流程；视觉规范来自 Figma MCP 读取的变量/样式与 frontend-conventions 第 9 节。不得用截图替代真实 Figma 设计。

| 输入 | 路径/链接 | 版本/批准 | 用途 |
|---|---|---|---|
| 需求与 AC | `proposal.md`、`specs/*/spec.md`、`design/user-stories.md` | 05 APPROVED | 页面集合、结构、文案、状态与交互基线 |
| Figma MCP | `<fileKey / node-id / 变量集合>` | 实际读取 | 真实 Figma 文件、节点、组件、变量与样式；下游界面输入来源 |
| 设计规范 | `docs/architecture/frontend-conventions.md` 第 9 节 | FROZEN v1.0.1 | 视觉、可访问性、组件与 token 使用规则 |

## Figma 文件

- Figma 链接：`https://www.figma.com/...`（必须实际可访问）
- fileKey / node-id：`<fileKey 或 node-id>`
- 页面/画板范围：`<PAGE-xxx → frame/section 名称>`

## MCP 读取记录

| 工具/命令 | 目标文件/节点 | 实际返回 | 时间 | 状态 |
|---|---|---|---|---|
| `use_figma` / `get_design_context` / `get_metadata` / `get_variable_defs` / `get_screenshot` | TODO | TODO | TODO | TODO |

## 节点映射

| PAGE ID | Figma node/component | 变量/样式 | 状态覆盖 | 差异 |
|---|---|---|---|---|
| PAGE-001 | TODO | TODO | default/loading/empty/error/success/disabled/no-permission | TODO |

## 页面覆盖

| PAGE ID | 页面职责 | Figma frame/section | 关键区块 | 覆盖状态 | 差异/说明 |
|---|---|---|---|---|---|
| PAGE-001 | TODO | TODO | TODO | 待检查 | TODO |

## 差异与待确认

| 差异 ID | 需求/AC 要求 | Figma 实际情况 | 影响 | 选择/理由 | 审批人/状态 |
|---|---|---|---|---|---|
| UI-DIFF-001 | TODO | TODO | TODO | TODO | TODO |

## UI 评审

- UI 评审状态：DRAFT（设计负责人评审 Figma 评审稿后改为 APPROVED）
- 评审人：PENDING
- 评审日期：PENDING
- 评审证据：workflow/evidence/06-figma-ui-review.md
- 评审范围：PAGE 覆盖、关键区块、状态变体、权限/导航行为、视觉与变量/样式一致性

> 无法读取的字段必须登记为“未检查”，不得虚构 MCP 结果；Figma MCP 不可用时阻断阶段 06，而不是用截图替代。
