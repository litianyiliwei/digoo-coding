# Figma MCP 审计

- Change ID：`<change-id>`
- Figma 文件/页面：`<真实 Figma 链接或 fileKey>`
- 检查时间/版本：`<时间、revision 或导出版本>`
- 需求清单版本：`<page/block/interaction 清单路径>`
- 审核人/状态：`<姓名或角色 / DRAFT|APPROVED>`

## Figma 文件

- Figma 链接：`https://www.figma.com/...`（必须实际可访问）
- fileKey / node-id：`<fileKey 或 node-id>`
- 页面/画板范围：`<PAGE-xxx → frame/section 名称>`

## MCP 读取记录

| 工具/命令 | 目标文件/节点 | 实际返回 | 时间 | 状态 |
|---|---|---|---|---|
| `get_design_context` / `get_metadata` / `get_variable_defs` / `get_screenshot` | TODO | TODO | TODO | TODO |

## 节点映射

| PAGE ID | BLOCK ID | ELEM ID | Figma node/component | 变量/样式 | 状态覆盖 | 差异 |
|---|---|---|---|---|---|---|
| PAGE-001 | BLOCK-001 | ELEM-001 | TODO | TODO | loading/empty/error/success/disabled/permission | TODO |

## 区块覆盖

| PAGE ID | BLOCK ID | 区块职责 | Figma section/frame | 区块内元素 | 覆盖状态 | 差异/说明 |
|---|---|---|---|---|---|---|
| PAGE-001 | BLOCK-001 | TODO | TODO | ELEM-001, ELEM-002 | 待检查 | TODO |

## 差异与待确认

| 差异 ID | 清单要求 | Figma 实际情况 | 影响 | 选择/理由 | 审批人/状态 |
|---|---|---|---|---|---|
| UI-DIFF-001 | TODO | TODO | TODO | TODO | TODO |

> 无法读取的字段必须登记为“未检查”，不得虚构 MCP 结果；UI 变更在 MCP 不可用时应阻断，而不是用截图替代。
