# Spec Delta

## ADDED Requirements

<!-- Change ID: workflow-context-bundles; Status: DRAFT; Source baseline: product v0.2.0, architecture v0.2.2 (FROZEN); Related requirements/AC: RA-001, NFR-001, FLOW-001, NODE-001-02–03, DO-002–003, RD-001/002/003/004, BR-001–004, DEC-002/004; Generated date/version: 2026-11-17 / v0.1.0 -->

### Requirement: 按阶段和影响条件渲染上下文包

系统 SHALL 根据有效阶段、当前 Change、已声明的影响标签和指定的稳定 ID/章节，渲染 Agent 实际可用的上下文文本。选择规则 SHALL 使用唯一权威的阶段/触发配置；输出 SHALL 保留默认必需输入，并仅在匹配触发条件时加入条件资料。未知阶段、未知标签、无效 ID 或仓库外路径 SHALL 以非零退出码失败，且不得静默退回到完整基线读取。

#### Scenario: 只装载默认项和命中的条件资料

- **GIVEN** 阶段配置、Change ID 和影响标签均有效
- **WHEN** 用户以 `--render --format json` 请求上下文包
- **THEN** 输出 JSON 的 `bundle_text` 按确定顺序包含必需输入和命中条件的资料，未命中的按需资料不进入 `bundle_text`
- **AND** `manifest.sources` 为每个来源记录仓库内路径、选择原因、匹配标签/触发器、选中的章节或 ID、SHA-256 和字符贡献

#### Scenario: 相同输入生成可复现内容

- **GIVEN** 阶段配置、Change 文件、标签和 ID/章节选择未改变
- **WHEN** 用户重复生成上下文包
- **THEN** `bundle_text`、来源顺序、内容哈希和计量结果保持一致
- **AND** 生成过程不创建新的正式常驻摘要或第二份权威资料

#### Scenario: 非法或越界输入被拒绝

- **GIVEN** 阶段、标签、ID/章节选择不存在，或某个解析后的输入路径指向仓库外
- **WHEN** 用户请求渲染
- **THEN** 命令返回非零退出码，指出无效项或越界来源
- **AND** 不输出可被误认为完整上下文的部分包

### Requirement: 以实际渲染内容执行上下文预算

系统 SHALL 对最终 `bundle_text` 做预算判断。字符数 SHALL 是将 CRLF 规范化为 LF 后的 Unicode 码点数；读取组数 SHALL 按唯一权威配置中实际选中的读取组计数。默认上限为 8 组和 12,000 字符。超限时 SHALL 失败关闭，报告实际数值和字符贡献最大的来源，不得静默截断或丢弃必需项。只有通过仓库内且匹配当前 Change、审批状态有效、授权额度覆盖本次输出的例外记录，才能放宽对应上限。

#### Scenario: 未超预算时返回完整包和指标

- **GIVEN** 选中的读取组不超过 8 组且渲染文本不超过 12,000 字符
- **WHEN** 用户请求渲染
- **THEN** 输出包含完整 `bundle_text`、`group_count`、`character_count` 和每个来源的贡献
- **AND** `character_count` 等于 CRLF 规范化后 `bundle_text` 的 Unicode 码点数

#### Scenario: 超预算且没有有效例外

- **GIVEN** 读取组数或字符数超过默认上限，且没有适用于本 Change 的有效批准例外
- **WHEN** 用户请求渲染
- **THEN** 命令返回非零退出码，输出状态为 `OVER_BUDGET`、实际值、目标值及贡献最大的来源
- **AND** `bundle_text` 为空，避免超预算内容被误用

#### Scenario: 超预算但存在有效例外

- **GIVEN** 例外记录明确绑定当前 Change，包含理由、审批人、日期、证据路径及字符/读取组上限，且已批准并能在仓库内验证
- **WHEN** 本次内容超过默认上限但没有超过例外授权值
- **THEN** 命令可输出完整包，并在 manifest 标记例外 ID、批准信息、依据及实际预算
- **AND** 缺失、过期、Change 不匹配或额度不足的例外仍按超预算失败

### Requirement: 按 TASK ID 生成不编造信息的执行卡

系统 SHALL 在传入有效 `--task-id` 时，从当前 Change 的任务、用户故事/AC、已批准设计和验证约定中提取该任务的目标、需求引用、允许修改范围、现有代码入口和适用检查命令。无法从权威文件解析的字段 SHALL 标为 `PENDING` 并列入 `missing_fields`；系统 MUST NOT 根据任务标题猜测代码路径、权限、行为或验证命令。

#### Scenario: 任务引用可闭合时生成执行卡

- **GIVEN** TASK ID 存在，且关联 AC、范围和适用检查可从当前 Change 产物解析
- **WHEN** 用户同时请求渲染上下文包和执行卡
- **THEN** `bundle_text` 包含该任务的目标、AC 引用、允许修改路径和验证命令
- **AND** manifest 记录执行卡字段的来源路径及引用 ID

#### Scenario: 任务资料不完整时明确列出缺项

- **GIVEN** TASK ID 存在，但一个或多个 AC、代码入口、允许修改路径或检查命令尚未在权威产物中定义
- **WHEN** 用户请求执行卡
- **THEN** 对应字段显示 `PENDING`，并列入 `missing_fields`
- **AND** 输出不得把缺少字段伪装成完整执行卡或补造内容

#### Scenario: TASK ID 不存在

- **GIVEN** TASK ID 未出现在当前 Change 的任务文件中
- **WHEN** 用户请求执行卡
- **THEN** 命令返回非零退出码并指出缺失的 TASK ID
