# API 契约规范

- Change ID：N/A（项目级架构基线）
- 状态：DRAFT v1.0（待基线审批）
- 来源基线：产品基线 v0.6-DRAFT、ADR-001/006
- 关联需求/AC：FLOW-001~008、BR-005、NFR-002
- 生成日期/版本：2026-11-10 / v1.0.0

## 1. 基本约定

- 协议：HTTPS + JSON；字符集 UTF-8；时间使用 ISO 8601 UTC。
- 版本：按服务划分基础路径：`/api/v1/platform`、`/api/v1/mes`、`/api/v1/iot`、`/api/v1/gis`、`/api/v1/ecommerce`（远期，默认 404/503）；破坏性变更发布 `/api/v2`，旧版本保留至少一个迭代并给出废弃公告。
- 服务归属：每个 API 必须属于且仅属于一个服务；跨服务聚合由前端或 BFF 组合，不在一个服务中直连他方数据库。
- OpenAPI 版本：3.1；每个 Change 的接口契约写入 `openspec/changes/<change-id>/api/openapi.yaml`。
- 资源命名使用复数名词；命令型动作使用动词子路径或 POST 命令，不使用动词式 RPC 风格混搭。
- operationId 命名：`<service><Domain><Action>`，lowerCamelCase，例如 `identityLogin`、`mesPlanCreate`、`mesTaskAssign`、`mesInventoryInbound`、`iotDeviceList`、`gisPlotLayer`、`mesTraceQuery`。operationId 全局唯一且稳定，改名视为破坏性变更。
- 每个 operationId 必须在 `design/api-io-mapping.csv` 映射到至少一个 IO，并在 `io-catalog.csv` 登记 IO 契约。

## 2. 认证与授权

- 认证方式：`Authorization: Bearer <JWT>`；JWT 由 `platform-service` 签发，其他服务用公钥本地校验；登录接口除外；消费者溯源查询为匿名只读。
- 服务间调用：使用服务 JWT（`aud` 指向目标服务、`scope` 限定接口），由 `platform-service` 签发；禁止服务间透传用户 JWT 或使用共享静态密钥。
- JWT 声明至少包含：`sub`（用户 ID 或服务 ID）、`roles`/`scope`、`dataScope`（农场/辖区）、`iat`、`exp`、`jti`。
- 授权模型：RBAC + 数据范围；每个接口在 OpenAPI 中声明所需角色/能力与数据范围。
- 匿名例外：`identityLogin`、`mesTraceQuery`、`mesTracePage`；匿名接口不得返回个人信息、经营数据与库存数据。
- `gis-service` 图层接口默认要求登录并按农场范围授权；如未来开放公开地图图层，必须单列匿名白名单与字段白名单。
- 权限失败语义：未认证 401；已认证但无权限 403；资源不存在 404；不得用 404 掩盖越权资源。
- 敏感操作二次校验：权限变更、设备控制、批次作废、电商订单/支付（远期）等需要最近 15 分钟内认证或二次确认。

## 3. 请求头与追踪

| 头 | 必填 | 说明 |
|---|---|---|
| `Authorization` | 受保护接口必填 | Bearer JWT |
| `X-Request-Id` | 可选 | 客户端生成；缺失时服务端生成 |
| `Idempotency-Key` | 命令型接口必填 | 出入库、任务提交、溯源码生成、设备控制 |
| `Accept-Language` | 可选 | 错误消息语言，默认 `zh-CN` |
| `Content-Type` | 有请求体时必填 | `application/json` 或 `multipart/form-data` |

- 每个请求生成或继承 `traceId`，写入响应、日志与审计；响应头返回 `X-Trace-Id`。

## 4. 响应结构

### 4.1 成功响应

```json
{
  "data": { "id": "..." },
  "traceId": "..."
}
```

列表响应：

```json
{
  "data": {
    "items": [],
    "page": 1,
    "size": 20,
    "total": 0
  },
  "traceId": "..."
}
```

### 4.2 错误响应

```json
{
  "code": "VALIDATION_422",
  "message": "参数校验失败",
  "details": [
    { "field": "name", "reason": "不能为空" }
  ],
  "traceId": "...",
  "timestamp": "2026-11-10T00:00:00Z"
}
```

错误码枚举：

| HTTP | code | 语义 |
|---|---|---|
| 400 | `BAD_REQUEST` | 请求格式错误 |
| 401 | `UNAUTHORIZED` | 未认证或令牌失效 |
| 403 | `FORBIDDEN` | 已认证但无权限 |
| 404 | `NOT_FOUND` | 资源不存在 |
| 409 | `CONFLICT` | 并发冲突、重复码、库存不足、重复提交 |
| 422 | `VALIDATION_FAILED` | 字段校验失败 |
| 429 | `RATE_LIMITED` | 触发限流 |
| 500 | `INTERNAL_ERROR` | 未预期错误 |
| 503 | `SERVICE_UNAVAILABLE` | 依赖不可用或维护中 |

## 5. 分页、排序与过滤

- 分页参数：`page`（从 1 开始）、`size`（默认 20，最大 100）；响应返回 `page/size/total`。
- 排序参数：`sort=field,asc|desc`；只允许白名单字段；默认按 `createdAt desc`。
- 过滤参数：显式命名，不使用通用 JSON 查询；复杂查询由后端提供专用接口。
- 无分页的大列表接口必须说明理由并经评审；导出接口单独定义上限与异步任务策略。

## 6. 幂等与并发

- `POST` 命令接口必须支持 `Idempotency-Key`；重复键返回首次结果，不重复写入。
- 幂等窗口至少 24 小时；键与请求指纹绑定；不同指纹复用同一键返回 409。
- 聚合更新使用乐观锁 `version`；版本冲突返回 409，客户端提示刷新后重试。
- 唯一约束冲突（账号、溯源码、批次-码绑定）返回 409，并在 `details` 中给出冲突字段。
- 非幂等外部调用（设备控制、短信）不自动重试；失败记录并通知人工处理。

## 7. 超时、重试与限流

- 客户端请求超时 10 秒；服务间调用超时 5 秒，设备控制 15 秒，GIS 图层查询 10 秒。
- `GET` 可安全重试 1 次；`POST/PUT/PATCH/DELETE` 不自动重试，依赖幂等键。
- 限流：登录按 IP + 账号；溯源查询与 GIS 图层按 IP；写接口按用户。超限返回 429，`Retry-After` 给出秒数。
- 熔断/降级：`iot-service` 不可用时，监测与控制接口返回 503 或只读缓存；`gis-service` 不可用时地图层降级为空态，不影响 MES 生产、库存、溯源主链路。

## 8. 文件上传

- `multipart/form-data`；单文件上限 20MB；允许图片与 PDF；扩展名与 MIME 双校验。
- 上传接口返回文件 ID 与访问 URL；访问 URL 使用短期签名或受控下载接口，不暴露真实磁盘路径。
- 附件元数据与业务记录同事务；文件写入失败回滚元数据。
- 病毒扫描可异步执行；扫描未完成的附件标记为待扫描，不进入公开溯源。

## 9. 兼容性与废弃

- 新增可选字段、增加枚举值（客户端需容忍未知值）视为兼容变更。
- 删除字段、改类型、改语义、改 operationId 视为破坏性变更，必须新版本或废弃周期。
- 废弃接口在 OpenAPI 标记 `deprecated: true`，响应头 `Deprecation` 与 `Sunset` 给出时间。
- 客户端必须忽略未知字段；服务端不得依赖客户端字段顺序。

## 10. 安全与隐私

- 不在 URL 查询参数中传递密码、令牌、身份证号等敏感信息。
- 日志脱敏：手机号、身份证号、密码、JWT、附件内容不写入日志。
- CORS 只允许配置的前端域名；管理端与消费者端分别配置。
- 响应头包含 `X-Content-Type-Options: nosniff`、`X-Frame-Options: DENY`、`Referrer-Policy`；HTTPS 启用 HSTS。
- 错误响应不返回堆栈、SQL、内部地址与依赖版本。

## 11. 服务路由与服务间契约

| 路径前缀 | 服务 | 一期 | 说明 |
|---|---|---|---|
| `/api/v1/platform/**` | `platform-service` | 启用 | 登录、用户、角色、审计、通知、配置 |
| `/api/v1/mes/**` | `mes-service` | 启用 | 计划、任务、作业、库存、批次、溯源、监管 |
| `/api/v1/iot/**` | `iot-service` | 启用 | 设备、遥测、预警、控制 |
| `/api/v1/gis/**` | `gis-service` | 启用 | 地块几何、图层、GeoJSON |
| `/api/v1/ecommerce/**` | `ecommerce-service` | 远期 | 默认 404/503；启用前需产品基线修订 |

- 服务之间只通过 HTTPS API 或领域事件交互；禁止跨服务直接读 schema、共享表或内部实现。
- 服务间 API 必须在 OpenAPI 中声明服务 JWT 的 `aud`/`scope`，并通过契约测试验证。
- 外部网关只做路由、TLS、限流与静态资源，不解析业务权限；各服务独立校验用户/服务 JWT。
- `ecommerce-service` 未启用时，Nginx 对其路径返回 404/503；不得将其数据写入 MES/GIS/IoT schema。

## 12. 契约检查

- 每个 Change 的 `openapi.yaml` 必须通过 `validate-openapi.sh`。
- 每个 operationId 必须映射到 IO，且每个 IO 有契约、超时、重试、错误与测试 ID。
- API 变更必须同步更新 `design/api-io-mapping.csv`、`design/io-catalog.csv` 与 `traceability.csv`。
- 契约检查通过不代表业务正确；业务语义仍由人工评审与 AC 验证。
