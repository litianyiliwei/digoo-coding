# 前端工程规范

- Change ID：N/A（项目级架构基线）
- 状态：APPROVED v1.0.2（2026-11-11 基线修订：阶段 06 改为 Figma-only）
- 来源基线：产品基线 v0.6-DRAFT、ADR-002/006
- 关联需求/AC：FLOW-001~008、BR-005、NFR-001/004
- 生成日期/版本：2026-11-11 / v1.0.2

## 1. 技术栈与版本

- Web 管理后台：Vue 3 + TypeScript + Vite + Element Plus + Vue Router + Pinia。
- 移动端：uni-app（Vue 3 语法）+ TypeScript；目标端 H5 优先，小程序/App 按 Q-005 后续确认。
- GIS 地图：Web/H5 优先使用 MapLibre GL JS 或 Leaflet；uni-app 小程序使用平台原生 map 组件；底图可配置。
- 请求层：按服务前缀封装（platform/mes/iot/gis/ecommerce）；优先根据 OpenAPI 生成类型，禁止业务组件直接使用底层网络库。
- 测试：Vitest + Vue Test Utils；E2E 使用 Playwright（Web 与 uni-app H5）。
- 版本策略：主版本按选型锁定；次版本在阶段 08 锁定到 `package.json` 与 lockfile；升级需记录兼容性验证。

## 2. 仓库与目录结构

```text
apps/
  api/          Spring Boot 后端
  web/          Vue 3 管理后台
  mobile/       uni-app 移动端
packages/
  api-client/   OpenAPI 生成的类型与按服务请求封装
  gis-map/      地图组件、图层样式、坐标工具
  shared/       共享常量、校验规则、错误码映射
deploy/
  docker-compose.yml
  nginx/
docs/
```

- 每个应用独立构建与部署；共享代码只放 `packages/`，禁止跨应用相对路径引用。
- 页面、组件、状态、请求、类型分目录管理；禁止把页面逻辑塞进全局工具文件。

## 3. 路由与页面边界

- Web 使用 Vue Router；路由按角色与能力守卫，未授权跳转统一 403/登录页。
- 移动端使用 uni-app `pages.json`；角色外壳按 RA-013：作业端 3 标签、管理端 4 标签、单模块角色无标签栏、消费者无外壳。
- 页面只负责编排与展示；业务规则不写在页面里，统一调用领域 API。
- GIS 页面/区块（地块分布、任务落位、预警定位、产地展示）统一使用 `packages/gis-map`，通过 `gis-service` 获取 GeoJSON；不得在各页面重复实现地图逻辑。
- 页面必须声明：所需权限、数据范围、加载态、空态、错误态、无权限态、地图图层加载态。
- 页面间传参使用路由参数或状态管理；禁止通过全局变量隐式传递。

## 4. 组件边界

- 组件分为页面组件、业务组件、基础组件；基础组件不得依赖业务 Store。
- Props 向下、事件向上；跨层通信使用 Provide/Inject 或 Store，禁止修改父组件 props。
- 每个业务组件必须有明确的输入、输出与状态；禁止隐式读取全局状态。
- Element Plus 组件二次封装放在 `components/base`；业务组件放在 `components/business`。
- 组件命名使用 PascalCase；文件与目录使用 kebab-case。

## 5. 状态管理

- 本地 UI 状态使用组件 `ref/reactive`；跨页面共享状态使用 Pinia Store。
- 服务端数据通过统一查询 composable 获取与缓存；禁止在 Store 中重复维护服务端副本。
- Store 按领域拆分：auth、farm、production、inventory、environment、traceability、regulatory。
- Store 不直接拼 URL；所有请求经 `api-client`；错误码映射集中在 `shared/error-map`。
- 退出登录时清空 Store、缓存与本地令牌；权限变更后刷新用户能力。

## 6. API 客户端与类型

- `packages/api-client` 由各服务 OpenAPI 生成类型；生成脚本纳入 CI，契约变更后重新生成。
- 统一请求层按服务前缀路由：`/api/v1/platform`、`/api/v1/mes`、`/api/v1/iot`、`/api/v1/gis`、`/api/v1/ecommerce`（远期默认禁用）。
- 统一请求层负责：注入 JWT、`X-Request-Id`、`Idempotency-Key`、超时、错误映射、重试策略、登录失效跳转。
- 业务组件不得直接创建 axios/fetch 实例；特殊通道需登记并经架构评审。
- 请求与响应类型必须来自生成类型；禁止手写重复 DTO。
- GIS 图层请求使用 `gis-client`，返回 GeoJSON 类型；大图层分页/范围过滤，前端不得一次性拉取全部要素。
- 上传附件使用统一上传组件；限制类型、大小与进度提示。

## 7. 表单与状态展示

- 表单校验使用 Element Plus Form 规则或共享校验器；前后端校验规则保持一致。
- 必填、长度、枚举、日期、数值范围必须有明确提示；提交前二次校验。
- 所有异步页面必须覆盖：loading、empty、error、success、disabled、no-permission。
- 错误展示映射 API 错误码：401 跳登录、403 显示无权限、409 提示冲突、422 定位字段、429 提示稍后重试、5xx 提示联系管理员。
- 危险操作（作废、删除、下发控制）必须二次确认并记录操作原因。
- 移动端弱网：请求超时提示、可重试、草稿本地暂存；提交使用幂等键防止重复。

## 8. 权限与数据范围

- 路由守卫校验登录与角色；按钮级权限使用统一指令或 `hasPermission`。
- 数据范围由后端返回，前端只用于展示与禁用，不作为安全边界。
- 消费者扫码页为匿名页面，不加载管理端 Store、不请求受保护接口。
- 监管端只读：隐藏写操作入口，后端仍必须强制校验。

## 9. 视觉与可访问性

- Element Plus 主题通过 CSS 变量定制；颜色、字号、间距使用设计令牌，不散落硬编码。
- 设计令牌以 Figma 变量/样式为准：06 通过 Figma MCP `get_variable_defs` 等读取，并把结果落盘到 `design/figma-audit.md`；07/08 以 Figma 评审稿为视觉权威，不再单独维护 `design/design-tokens.json`。
- 管理后台与移动端共享术语与状态颜色；状态色需同时有文字或图标，不只靠颜色。
- 表单控件有 label；错误提示与控件关联；键盘可操作；对比度满足可读性要求。
- 移动端触控目标不小于 44px；重要操作避免仅手势触发。
- Figma 设计与实现一致性在阶段 06/07 通过 Figma MCP 审计；不得用截图替代真实读取。

## 10. 日志、隐私与错误上报

- 前端日志不记录密码、JWT、完整手机号、身份证号与附件内容。
- 错误上报包含 `traceId`、页面、操作、错误码；不包含请求体敏感字段。
- 生产关闭调试日志；开发日志分级；不得把用户数据打印到控制台。

## 11. GIS 地图与图层

- 地图组件统一放在 `packages/gis-map`；Web/H5 使用 MapLibre GL JS 或 Leaflet，小程序使用原生 map 组件。
- 地块图层数据来自 `gis-service` 的 GeoJSON；图层包括地块边界、地块状态、任务落位、预警位置、产地位置。
- 地图必须覆盖：加载中、无地块、图层加载失败、无权限、要素过多降级；不得用静态截图替代真实图层。
- 坐标系统与底图来源由 Q-014 决定；一期支持手工绘制/导入 GeoJSON，示意精度需在界面上标注。
- 地图交互（点选地块、图层切换、范围过滤）必须在 06 的 `figma-audit.md` 中登记 PAGE ID 并映射 AC/EVT。
- GIS 坐标明细不写入前端日志；地图截图与导出遵守数据权限。

## 12. 电商远期页面（DEFERRED）

- 一期不实现商品、订单、支付、售后页面；前端不加载 `ecommerce-service` 客户端。
- 远期启用前必须完成产品基线修订、支付安全与隐私评估，并新增 PAGE/BLOCK/EVT 清单。
- 电商页面只消费 MES 溯源公开数据与自身服务 API，不得直接读取 MES 数据库。

## 13. 测试与质量门禁

- 每个业务组件至少一个 Vitest 组件测试；关键页面有 Playwright E2E。
- 表单校验、权限守卫、错误映射、空态/错误态必须有测试或人工验收证据。
- 前端 CI 必须通过：类型检查、Lint、单元测试、构建、E2E 冒烟。
- 覆盖率按风险定义；权限、库存、溯源、设备控制相关代码优先覆盖。
- 页面/组件/交互必须在 06 的 `figma-audit.md`（PAGE ID 与 PAGE→node/component/variable）登记，并映射 AC/TEST。
