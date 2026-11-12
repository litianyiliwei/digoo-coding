# Acceptance Evidence

- Change ID: TODO
- Acceptance owner: TODO
- Date/build: TODO
- Overall result: PENDING

| AC ID | Result | Evidence/test report | Defect/deviation | Reviewer |
|---|---|---|---|---|
| AC-001 | Pending | TODO | TODO | TODO |

## UI acceptance（涉及 UI 时必须）

> 验收以机器证据为主：`design/evidence/figma-layout-check.json` 必须为 PASS。无差异、非 `UI-DERIVED` 的 PAGE 可按机器证据批量签收，`验收方式` 写“机器证据签收”；仅存在差异、`UI-DERIVED` 或未纳入断言的 PAGE 需要打开运行中的系统界面与真实 Figma 文件/评审稿并排核对，`验收方式` 写“并排核对”。不保存也不接受截图作为证据。
> 逐 PAGE 行仍必须齐全；任 PAGE 缺失签收或结果不是 ACCEPTED/DEVIATION_APPROVED 时不得归档。

| PAGE | Result | Figma node | 运行系统入口（URL/路由） | 差异/审批 | 验收方式 | Reviewer |
|---|---|---|---|---|---|---|
| PAGE-001 | ACCEPTED | `3:2` | `http://127.0.0.1:5180/login` | 无 | 机器证据签收 | 设计负责人 |

## Open blockers and risks

TODO
