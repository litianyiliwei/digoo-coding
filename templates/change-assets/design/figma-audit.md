# Figma 设计契约与 UI 评审（单文件）

- Change ID：`<change-id>`
- Figma 文件/页面：`<真实 Figma 链接>`
- fileKey：`<fileKey>`
- 文件版本/快照时间：`<版本号、lastModified 或导出版本 / 时间>`
- 设计来源状态：DRAFT
- UI 评审状态：DRAFT
- 机器契约：`figma-code/`（每 PAGE 一个**目标框架对齐**的设计代码：Vue 栈为 `.vue` + 该端组件库（Web 为 Element Plus，移动端为 uni-app 组件库），React 栈为 `.tsx`/`.jsx`）与 `figma-layout.csv`（精简几何/文本/字体断言表）
- 资产目录：`figma-assets/`（仅图片/SVG 资产与 `README.md`；**不保存参考截图**）

> 本文件是 06 的唯一 UI 契约，也是 07/08/09/10 的唯一界面输入。
> 真实 Figma 评审稿是视觉/结构/组件/变量的最终权威；本文件必须记录**实际值**与**每页规格**，不能只写变量名。
> 机器判据是 `figma-layout.csv` 的预期几何/文本/字体与运行态 DOM 的数值断言（`scripts/check-figma-layout.py`），以及 `scripts/check-design-tokens.py` 的 token 实际值比对；**截图不是门禁证据**。实现以 `figma-code/` 的目标框架设计代码为准。
> 06 一次性导出节点几何、token 与实际资产，并按总体技术选型转码；07/08 默认离线消费，仅在文件版本变化或页面有歧义时重新读取 Figma。
> 无 UI 时：在“设计来源与选择”写入 `- 设计来源状态：N/A` 与 `- 无 UI 理由：<原因>`；无需填写 Figma/令牌/节点章节。

## 设计来源与选择

- 设计来源状态：APPROVED
- 设计来源选择：Figma MCP AI 自动设计（人工 Figma 设计仅在用户明确选择时）

| 项 | 内容 |
|---|---|
| 设计来源选择 | Figma MCP AI 自动设计 / 人工 Figma 设计 |
| 选择人/日期 | `<姓名或角色 / YYYY-MM-DD>` |
| PAGE 清单 | `<PAGE-001…PAGE-00N>`，由本阶段冻结；07–10 不得新增或重命名 |
| 文件版本 | `<Figma 版本/commit 或 lastModified>` |
| 说明 | 本文件记录 token 实际值、每页规格与资产；未定义的页面/状态必须显式记为差异 |

## 设计令牌（实际值）

> 从 Figma 变量/样式实际读取；变量名不能替代实际值。颜色必须有 hex，间距/圆角/字号必须有单位。

| 变量 | 类型 | 实际值 | CSS 变量 / Element Plus 映射 |
|---|---|---|---|
| `color/bg` | COLOR | `#f4f7f1` | `--color-bg` |
| `color/surface` | COLOR | `#ffffff` | `--color-surface` |
| `color/brand` | COLOR | `#2f6b3f` | `--color-brand` |
| `color/text` | COLOR | `#1f2a24` | `--color-text` |
| `color/text-secondary` | COLOR | `#5f6f64` | `--color-text-secondary` |
| `color/border` | COLOR | `#dce5d7` | `--color-border` |
| `color/brand-text-light` | COLOR | `#e8f1e3` | `--color-brand-text-light` |
| `color/brand-text-muted` | COLOR | `#d8e8d4` | `--color-brand-text-muted` |
| `space/page` | NUMBER | `22px` | `--space-page` |
| `radius/card` | NUMBER | `10px` | `--radius-card` |
| `radius/control` | NUMBER | `8px` | `--radius-control` |
| `shadow/card` | EFFECT | `<实际值>` | `--shadow-card` |

## 文字样式（实际值）

| 样式 | 字体 | 字重 | 字号 | 行高 | 字距 |
|---|---|---|---|---|---|
| `Type/12 Regular` | Noto Sans SC | 400 | 12px | 100% | 0 |
| `Type/13 Regular` | Noto Sans SC | 400 | 13px | 100% | 0 |
| `Type/14 Regular` | Noto Sans SC | 400 | 14px | 100% | 0 |
| `Type/14 Medium` | Noto Sans SC | 500 | 14px | 100% | 0 |
| `Type/18 Regular` | Noto Sans SC | 400 | 18px | 100% | 0 |
| `Type/24 Bold` | Noto Sans SC | 700 | 24px | 100% | 0 |
| `Type/44 Bold` | Noto Sans SC | 700 | 44px | 100% | 0 |

## PAGE 与节点

| PAGE ID | Figma node | 画板尺寸 | 状态 |
|---|---|---|---|
| PAGE-001 登录 | `3:2` | 1440×900 | default |
| PAGE-002 用户管理 | `5:2` | 1440×900 | default |
| PAGE-003 角色与权限 | `7:2` | 1440×900 | default |
| PAGE-004 审计日志 | `8:2` | 1440×900 | default |
| PAGE-005 通知中心 | `9:2` | 1440×900 | default |
| PAGE-006 系统配置 | `11:2` | 1440×900 | default |

## PAGE 关键规格

> 每页必须有区块级实际值（位置/尺寸/布局/padding/gap/边框/圆角/字体/填充），不能只写“顶栏、侧栏、列表”。
> 元素级文字/间距/字号/层级以 `figma-code/` 为参考；`figma-layout.csv` 是运行态断言子集；本表是区块摘要，不是唯一几何来源。
> 完整 `get_design_context` 快照可附录在本页规格之后，禁止另建分散文件。

### PAGE-001 登录

| 区块 | Figma node | 位置/尺寸 | 布局/间距 | 填充/边框/圆角 | 字体/文本 |
|---|---|---|---|---|---|
| 品牌区 | `3:3` | x=0,y=0,w=600,h=900 | 纵向 gap 22, padding 22 | 填充 `color/brand` | `Type/44 Bold`、`Type/18 Regular`、`Type/14 Regular` |
| 表单区 | `3:7` | x=600,y=0,w=840,h=900 | 居中, padding 64 | 填充 `color/bg` | — |
| 表单卡 | `3:8` | x=210,y=265,w=420,h=370 | 纵向 gap 18, padding 18 | `color/surface`, 1px `color/border`, 圆角 10 | `Type/24 Bold`、`Type/13 Regular` |
| 账号输入 | `3:12` | x=19,y=132,w=382,h=40 | 水平居中, 左右 padding 12 | `color/surface`, 1px `color/border`, 圆角 8 | `Type/13 Regular` |
| 密码输入 | `<node>` | `<x,y,w,h>` | `<布局>` | `<填充/边框/圆角>` | `<字体>` |
| 登录按钮 | `3:17` | x=19,y=280,w=66,h=39 | padding 18/10 | `color/brand`, 圆角 8 | `Type/14 Medium` |
| 底部说明 | `<node>` | `<x,y,w,h>` | `<布局>` | `<填充>` | `<字体/文本>` |

<!-- 其余 PAGE 按上表格式补充；设计代码中的文字/结构以 figma-code/ 为准；断言范围在 ## 断言范围 说明。 -->

## 设计代码

- 目标框架：`<Vue 3 + TypeScript + Element Plus / React + ...>`（必须与 `docs/architecture/technology-decisions.md` 一致）
- 设计代码扩展名：`<.vue / .tsx / .jsx>`
- 选型依据：`<ADR-002 / technology-decisions 版本与批准日期>`
- 转码方式：官方 `figma-design-to-code` Skill 加载记录；`get_design_context` 参考实现 → 目标框架组件/样式/token 的替换表；只做静态高保真页面，不接业务 API。
- `figma-code/README.md`：说明来源、目标框架/扩展名、组件与样式/token 替换、转码偏差、`data-node-id` 与 `figma-layout.csv` 的对应关系。
- `figma-code/PAGE-001.vue … PAGE-00N.vue`（React 栈为 `.tsx`/`.jsx`）：每 PAGE 一个目标框架设计代码，包含真实文案、字号/字重、间距、圆角、层级和 `data-node-id`。08 直接移植为页面骨架，只补路由/API/状态/权限/业务逻辑，不得重写样式、布局或文案。
- `figma-layout.csv`：精简断言表，列包含 `page_id,route,element_id,figma_node_id,x,y,width,height,dom_selector,assert_geometry,assert_text,tolerance_px,text_content,font_size,font_weight,notes`；坐标相对 PAGE 画板左上角。06 建立断言子集（`route`/`dom_selector` 可暂为 `PENDING`），07 必须填满。
- 门禁：`python scripts/check-figma-audit.py --change <change-id> --strict --require-framework` 校验目标框架、每 PAGE 设计代码存在、断言表几何/文本/选择器完整；08/09 运行 `python scripts/check-figma-layout.py --change <change-id> --base-url <url> --viewport 1440x900`，逐元素比较预期 `x/y/w/h`、文本与字体；`python scripts/check-design-tokens.py --change <change-id> --tokens <token.css>` 精确比对 token 实际值。
- **UI 验证以机器证据为主**：无差异 PAGE 在 08/09/10 直接使用 `figma-layout-check.json` 数值；仅差异/`UI-DERIVED` PAGE 需要人工复核与审批。不保存参考截图或像素截图。

## 断言范围

> `figma-layout.csv` 是运行态断言的唯一子集；未纳入断言的元素由设计代码与人工验收覆盖。若有结构性差异（Figma 有、实现无，或布局不同），必须在 `## 差异与待确认` 登记，等待设计负责人批准。
> 每个 PAGE 至少 1 行断言；建议覆盖顶部/侧栏/主区/标题/主操作/表格卡等关键区块。

| PAGE | 断言覆盖 | 未断言/说明 |
|---|---|---|
| PAGE-001 | 品牌区、品牌标题、表单卡、表单标题、账号输入、按钮、底部说明 | 副标题/标签等由设计代码与人工验收覆盖 |
| PAGE-00N | `<...>` | `<...>` |

## 状态覆盖

> 每个 PAGE 必须列出适用的状态；“Figma 无帧”的状态必须写明 07 设计决策、审批人和参考依据，不能声称已还原。
> 非 default 状态不要求截图；08 用断言映射覆盖可见元素与状态差异，09 独立核验，10 对无差异 PAGE 按机器证据批量签收、对差异/`UI-DERIVED` PAGE 并排核对。

| PAGE ID | 状态 | Figma 是否有帧 | 说明/决策 |
|---|---|---|---|
| PAGE-001 | default | 是 | — |
| PAGE-001 | loading | 否 | 07 设计决策：`<按钮 loading 样式/依据>`；审批人 `<...>` |
| PAGE-001 | error | 否 | 07 设计决策：`<错误提示样式/依据>`；审批人 `<...>` |
| PAGE-002 | default/empty/no-permission | 是/否/否 | 逐个说明 |
| … | … | … | … |

## 资产清单

> 仅登记真实图片/SVG 资产（logo、图标、插图等），下载到 `figma-assets/`，不能保留 Figma 临时 URL。
> **不得登记参考截图**（`PAGE-*.default.png` 等）；视觉比对使用 `figma-code/` / `figma-layout.csv`。
> 有资产时同时写入 `figma-assets/README.md`（文件名、来源 node、sha256、尺寸）；无资产时删除上表并写 `- 资产：无`。

| 资产 | 来源 node | 文件 | 尺寸 | 用途 |
|---|---|---|---|---|
| `<logo>` | `<node>` | `figma-assets/asset-logo.svg` | `<w×h>` | `<...>` |

## MCP 读取记录

| 工具/命令 | 目标文件/节点 | 实际返回 | 时间 | 状态 |
|---|---|---|---|---|
| `get_variable_defs` | `<fileKey>` | token 实际值数量 | `<时间>` | 成功 |
| `get_metadata` | 6 个 PAGE | 设计代码中的页面结构与 x/y/w/h | `<时间>` | 成功 |
| `get_design_context` | `3:2`…`11:2`（按需） | 每页规格/样式/资产 | `<时间>` | 成功 |

## 差异与待确认

| 差异 ID | 需求/AC 要求 | Figma 实际情况 | 影响 | 选择/理由 | 审批人/状态 |
|---|---|---|---|---|---|
| UI-DIFF-001 | `<...>` | `<...>` | `<...>` | `<...>` | `<...>` |

## UI 评审

- UI 评审状态：DRAFT（设计负责人在真实 Figma 评审稿上评审后改为 APPROVED）
- 评审人：`<姓名或角色>`
- 评审日期：`<YYYY-MM-DD>`
- 评审证据：`workflow/evidence/06-figma-ui-review.md`
- 评审范围：PAGE 覆盖、关键区块、状态变体、权限/导航行为、token 实际值、`figma-code/` 的目标框架/页面结构与文案、`figma-layout.csv` 断言范围

> 无法读取的字段必须登记为“未检查”，不得虚构 MCP 结果；Figma MCP 不可用时阻断阶段 06，而不是用截图或文字臆造替代。
> 人工 UI 评审在真实 Figma 文件上完成；自动化视觉回归使用节点几何与运行态 DOM 的数值断言，不使用截图。
