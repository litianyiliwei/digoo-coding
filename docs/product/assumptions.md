# 假设登记

- Change ID：N/A（项目级）
- Status: READY_FOR_REVIEW
- Source baseline: 用户请求、阶段 02 需求和未决问题
- Related requirements/AC: ASM-001–002 ↔ RA-001/NFR-001/FLOW-001/BR-001
- Generated date/version: 2026-11-16 / v0.2.0-draft

> 假设不是事实。每条假设必须有验证方式、到期/复核点和责任人；到期未验证不得继续作为需求或设计依据。

| ASM ID | 假设 | 为什么需要 | 验证方式/证据 | 到期/复核点 | Owner | Status |
|---|---|---|---|---|---|---|
| ASM-001 | 本次优化对象是项目 AI coding 流程工具包，不是独立农业业务应用 | 用户明确要求优化本仓库的 AI coding 流程 | 用户确认范围 | 2026-11-16 | 用户 | VALIDATED |
| ASM-002 | 12,000 字符是默认上下文目标，字符数为预算口径 | 作为可重复计算的阶段预算；试点继续验证适用性 | 用户确认 12,000 字符 | 后续试点复核 | 用户/流程负责人 | VALIDATED |

- 状态枚举：`OPEN`、`VALIDATED`、`INVALIDATED`、`EXPIRED`。
