# 输入/输出上下文政策

> 状态：APPROVED（2026-11-13，用户确认“优化输入，再基于精简输入优化输出”）
> 适用范围：02–10 阶段；项目级与 Change 级
> 机器权威：`docs/STEP-ARTIFACT-CONTRACTS.json` 的 `input_policy` 与 `output_policy`

## 1. 为什么收敛

此前阶段 05–10 的 `inputs` 把完整产品基线、完整架构基线、ADRs、完整 specs 和当前 Change 产物混在一起；虽然多数条目写了“按需读取”，但没有默认读取顺序、文件预算和触发条件。实际执行时容易出现两种问题：

- 一次性把 `docs/product/*`、`docs/architecture/*` 全量塞入上下文，挤掉当前 Change 的关键契约；
- 或者只读少量文件却声称“已按输入核验”，遗漏真正影响设计的章节。

现在把“审计用完整输入集”和“默认精简读取集”分开：`inputs` 仍是完整契约集（用于交接/溯源），`input_policy.stage_profiles` 定义每个阶段默认读什么、何时读更多。

## 2. 输入分层

| 层级 | 内容 | 读取规则 |
|---|---|---|
| 0 常驻 | `docs/product/BASELINE-BRIEF.md`（≤1 页）、`baseline-status.md` | 每阶段先读；不重复读完整基线 |
| 1 当前 Change | `proposal.md`、`specs/<capability>/spec.md`、`user-stories.md`、`tasks.md`、`design.md`、`baseline-impact.md`、`baseline-binding.json` | Change 阶段必读 |
| 2 定向 | 本 Change 命中的 `FLOW/NODE/DO/RD/BR/ROLE/CAP/PAGE/API/IO/INTERFACE` 行或章节；设计域命中的架构章节 | 按 ID 读相关行/节，不读整份文件 |
| 3 按需 | 完整 `docs/product/*`、完整 `docs/architecture/*`、`docs/adr/*`、`reference-research.md`、完整 specs | 只有 0–2 层无法回答时才读；交接报告记录触发原因 |

## 3. 默认预算

- 默认精简集 **≤8 个读取组**、约 **≤16000 字符**（每组尽量只指向一个文件/章节；组内多文件按 ID 定向）（契约中的 `max_lean_files` / `max_lean_chars`）。
- 超过预算时：先拆分 Change、缩小范围，或在交接报告第 1 节记录“为什么必须多读哪些文件”。
- 不允许把整包基线、整包架构文档或全部 ADR 作为默认上下文。

## 4. 每阶段怎么读

运行：

```bash
python scripts/agent-context.py --stage 07 --change <change-id>
```

输出分为：

- `精简输入（默认读取）`：按顺序读，先读 BASELINE-BRIEF 与当前 Change 产物；
- `按需输入（触发后读取）`：只在对应设计域命中/决策冲突时读；
- `完整契约输入（审计用，默认不读）`：加 `--full` 才显示，用于交接审计而不是默认上下文。

各阶段的精简/按需清单以 `docs/STEP-ARTIFACT-CONTRACTS.json` 的 `input_policy.stage_profiles` 为准；`docs/STAGE-IO-OVERVIEW.md` 会同步展示。

## 5. 输出优化

输出原则是 **引用式输出**：不复制输入全文；基线、规格、上游产物用 ID/路径/章节引用；每个输出只写本阶段新增的决策、契约或证据。

- 摘要文件（`BASELINE-BRIEF.md`、`requirements-analysis.md`、`baseline-audit-report.md`、`acceptance.md`）只写结论/差异/证据，不重复明细表。
- `design.md` 只写本 Change 的决策/契约/实现约束/测试映射；基线内容引用 ID，不复制整份基线。
- 证据文件（`code-review.md`、`independent-verification-report.md`、`acceptance.md`）引用 JSON/日志/报告路径，不复述全部测试输出。
- 表格只保留决策项、契约项、证据项；模板固定字段不重复展开。

摘要文件的建议行数上限见契约 `output_policy.summary_budgets`（例如 `BASELINE-BRIEF.md` ≤60 行、`design.md` ≤400 行、`acceptance.md` ≤120 行）。超过上限时先检查是否复制了输入；必要时拆分 Change 或链接上游文件。

## 6. 与门禁的关系

- `check-step-contracts.py` 校验每个 03–10 阶段都有 `input_policy.stage_profiles`，且 `lean` 条数不超过 `max_files`。
- `workflow.py transition` 的 evidence 仍按完整 `inputs` 审计，不会因为精简读取而放过缺失的正式输入。
- 交接报告第 1 节必须列出实际读取的文件/章节；未读的按需文件不得声称已审查。
