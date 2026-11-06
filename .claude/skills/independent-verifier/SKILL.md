---
name: independent-verifier
description: 以只读、独立视角验证一个 OpenSpec Change 的实现是否满足已批准规格、验收标准、设计契约和测试要求，并生成可追溯的验证证据。
---

# 独立验证与验收证据

## 何时使用
实现阶段完成后、人工验收和 OpenSpec 归档前使用。Verifier 不承担实现任务，不修复代码，不替 Builder 修改测试；发现问题时只记录证据并退回实现阶段。

## 独立性与权限
- 以独立 Agent/新上下文执行，不能把 Builder 的自我总结作为通过证据。
- 对源代码、配置、迁移、OpenAPI、规格和测试文件只读；允许执行测试/构建命令，允许写入本阶段报告文件。
- 不得修改实现代码、测试代码、OpenSpec proposal/specs/design/tasks、项目基线或审批记录。
- 记录 Builder 与 Verifier 的 Agent/会话标识，并确保是不同 Agent 或独立会话；记录被验证的 Git revision/commit，或明确记录工作区 diff 指纹；验证期间源代码发生变化则本轮证据失效。

## 必须读取
- 当前 Change 的 proposal、specs、design、tasks。
- 已批准的 `design/baseline-impact.md` 和项目基线版本。
- OpenAPI、API-IO 映射、IO catalog、前后端详细设计和测试设计（按适用范围）。
- Builder 的测试/构建报告、代码审查报告及实际代码差异；这些报告仅作线索，不能代替重新验证。

## 执行
1. 核验 Change ID、批准状态、基线版本和被测代码 revision。
2. 将每条验收标准（AC）映射到实际代码路径、测试和可观察证据；缺少映射不得判 PASS。
3. 独立执行项目约定的单元、集成、契约、端到端及静态检查；记录完整命令、退出码和结果。不能执行的检查标记 NOT_RUN，不得视为通过。
4. 核验 API → IO 映射、IO 契约、事务/幂等/异常处理和数据迁移（适用时）。
5. 核验需求追踪覆盖、OpenSpec tasks 完成情况、基线约束遵循情况及兼容性。
6. 生成 `design/evidence/independent-verification-report.md` 和 `design/evidence/independent-verification.json`。
7. `PASS` 才允许进入人工验收；`FAIL` 或 `BLOCKED` 必须将 Change 退回实现/设计阶段，并列出可复现证据。

## 判定规则
- PASS：所有适用 AC 均有证据且通过；所有必需测试实际执行并通过；无未解决的阻断级发现；被测 revision 稳定。
- FAIL：发现实现不符合规格、测试失败、契约不一致或 AC 未满足。
- BLOCKED：缺少输入/环境/权限/测试依赖，或无法确认被测 revision；不得用推测替代验证。
- NOT_RUN、SKIPPED、PENDING 均不是 PASS。

## 输出与门禁
报告必须列出验证范围、revision、AC 逐项结果、测试命令与退出码、API→IO/数据/安全检查、发现项、未执行项和最终判定。运行 `python3 scripts/check-independent-verification.py --report <change>/design/evidence/independent-verification.md --evidence <change>/design/evidence/independent-verification.json`。只有检查通过且 verdict=PASS 才能交接至阶段 15。

## 输入/输出/交接契约（强制）

执行前读取 `docs/STEP-ARTIFACT-CONTRACTS.json` 中 `skill="independent-verifier"` 的契约。输入必须来自已批准 Change 和阶段 14 的真实实现证据；输出必须落盘为 Markdown 报告与 JSON 证据；下游阶段 15 只消费 Verdict=PASS 且校验脚本退出码为 0 的报告。缺少输入、AC 证据或测试运行记录时阻断。


## 独立基线约束验证（强制）

- Verifier 必须独立读取当前 Manifest、Constraint Registry 和 Change `baseline-binding.json`，核验每条适用约束是否与实际代码/配置/数据库迁移/接口一致。
- 不得信任 Builder 自填的 PASS；Verifier 应重新执行对应的自动检查或记录独立人工核验依据，并在报告中列出约束 ID 与结果。
- 阶段 14b 转出前，执行 `python3 scripts/baseline-governance.py check-change --change-id <id> --phase implementation`；报告未覆盖约束的检查结论时应判 BLOCKED。
