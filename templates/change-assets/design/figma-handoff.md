# Figma 交接包（由脚本生成，禁止手改）

> 本文件是 `templates/change-assets/design/figma-handoff.md` 的格式模板。实际交付物由
> `python scripts/build-figma-handoff.py --change <change-id> --write` 生成到
> `openspec/changes/<change-id>/design/generated/figma-handoff.md`；`--check` 校验是否过期。
> 08 审计仍以 `page-inventory.csv` / `block-inventory.csv` / `interaction-map.csv` 为唯一权威。

- 生成来源：三份清单 + `design-spec.json`（SHA-256 见 generated/figma-handoff.json）
- Change ID：`<change-id>`
- 命名约定：页面 Frame = `PAGE-xxx`；区块 section = `BLOCK-xxx`；元素图层 = `ELEM-xxx`
- 状态词表：default / loading / empty / success / error / disabled / no-permission / boundary / duplicate-submit

## 硬约束与可优化范围

- 必须遵循：页面集合、区块顺序与边界、元素所属区块、状态覆盖、权限与导航行为、交互结果。
- 允许优化：间距节奏、排版层级、组件质量、图标语义化、空态/错误态/无权限态设计、可访问性、一致性与动效。
- 不得作为输入：原型截图、原型临时占位画法与试错图标、原型的彩色值（颜色由设计 token 绑定）。

## PAGE-001 页面名称

- 路由：`/login`；角色：`种植员;农场管理员`；清单状态：`default;loading`
- 画板：`375 × 812`；外壳：`bottom-tab / admin`（工作台、任务、监测、管理）
- 状态变体：default、loading、empty、success、error、disabled、no-permission、boundary、duplicate-submit

### 1. BLOCK-001 区块名称（block_type；职责说明）

- 布局：direction=vertical(must)、gap=8(should)、padding=[12,12,12,12](free)、height=44(should)
- 元素：
  - `ELEM-001` button「提交」｜size=160×44(should)｜fill=token:color.action.primary｜textStyle=token:type.body｜状态=default/disabled/loading
- 事件：
  - `EVT-001` 点击 → 提交登录；状态变化=提交中→成功/失败；错误=账号或密码错误
