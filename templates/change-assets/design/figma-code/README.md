# Figma 目标框架设计代码

- 来源：Figma MCP `get_design_context`（调用前已加载官方 `figma-design-to-code` Skill），每个 PAGE 一个文件（`PAGE-001.vue` … `PAGE-00N.vue`；React 栈为 `.tsx`/`.jsx`）。
- 目标框架：`<Vue 3 + TypeScript + Element Plus / React + ...>`，必须与 `docs/architecture/technology-decisions.md` 一致。
- 扩展名：`<.vue / .tsx / .jsx>`；技术选型变化时按新选型重转码，不得混用框架。
- 转码方式：`get_design_context` 返回的参考实现（通常为 React + Tailwind）已按目标框架替换为项目组件库与 token；保留真实文案、字号/字重、间距、圆角、层级与 `data-node-id`，只做静态高保真页面，不接业务 API。
- 替换登记：

| 来源（参考实现） | 目标（项目栈） | 说明 |
|---|---|---|
| `<Tailwind class / 原始标签>` | `<Element Plus 组件 / CSS 变量>` | `<几何或视觉用途>` |
| `<React 组件>` | `<Vue 组件 / composable>` | `<行为与状态>` |

- 转码偏差：`<无 / 差异 ID + 原因 + 审批人>`；结构性差异同步登记到 `figma-audit.md` 的 `## 差异与待确认`。
- `data-node-id="..."` 与 `figma-layout.csv` 的 `figma_node_id` 一一对应；`figma-layout.csv` 是运行态几何断言的子集，`figma-audit.md` 是 token/状态/评审摘要。
- 代码中的文字、字号、字重、间距、圆角和层级是 Figma 的真实值；实现时不得凭记忆改写。
- 代码中的临时 Figma 资产 URL（`https://www.figma.com/api/mcp/asset/...`）必须下载到 `figma-assets/` 并替换，不得作为运行时资源。
- 08 直接移植本目录代码为页面骨架，只补路由、API、状态、权限与业务逻辑；不得重写样式、布局或文案。确需视觉偏差时必须 `UI-DEVIATION` 审批。
- 06 一次性生成并落盘；07/08 默认离线消费，仅在 Figma 文件版本变化或页面有歧义时按页重读（串行、避免限流）。
- **UI 验证以机器证据为主**：无差异 PAGE 后续按 `figma-layout-check.json` 数值签收；仅差异/`UI-DERIVED` PAGE 人工复核。不保存截图。
