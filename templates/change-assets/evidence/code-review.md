# Code Review Evidence

- Change ID: TODO
- Reviewer/tool: TODO
- Review date/commit: TODO
- Review conclusion: TODO (PASS / APPROVED / NO_BLOCKING_FINDINGS; FAIL/BLOCKED must not transition out of stage 08)
- Findings: none

## Findings by severity

| Severity | File/line | Finding | Resolution/evidence | Status |
|---|---|---|---|---|
| TODO | TODO | TODO | TODO | Pending |

> When there are no findings, delete the data row of the table above and change `- Findings:` to `none`; status may only use fixed/resolved/closed/accepted/risk-accepted/n/a/none.

## Static analysis

> Machine-copied from `design/evidence/static-analysis.json` when `docs/architecture/quality-gates.json` exists: copy the stack id, tool id, command, configs (path @ sha256), result, and exit code verbatim from the evidence JSON; do not paraphrase. Rows must end with the literal `exit 0`. When the project has not adopted quality gates, delete the data row and write `- Static analysis: N/A (no quality-gates.json)`.

| Stack | Tool | Command (from evidence) | Configs (path @ sha256) | Result | Exit code |
|---|---|---|---|---|---|
| frontend-web | eslint | `npx --no-install eslint --max-warnings 0 .` | `eslint.config.js @ <sha256>` | PASS | exit 0 |

Waived items copied from the evidence `waivers_applied` list (write `none` when empty) and their approver:

| Waiver id | File | Rule | Approved by | Expires at |
|---|---|---|---|---|
| PENDING | PENDING | PENDING | PENDING | PENDING |

> `scripts/check-code-review.py` requires a line containing the stack id, the tool id, and the literal `exit 0`; `exit code 0` and `exit=0` are not accepted. An expired or invalid waiver blocks review.

## Spec compliance, security, data consistency, failure paths

TODO

## UI fidelity

> Required for UI Changes; when there is no UI, delete this section and write `- UI fidelity: N/A (no UI)`.
> The machine evidence is `evidence/figma-layout-check.json` (measured by `scripts/check-figma-layout.py` at a 1440×900 viewport); screenshots are not used.
> Paths are relative to the Change's `design/` directory; `assertion elements/max deviation` must be copied directly from the JSON's `element_count` / `max_delta_px`, not manually estimated.
> **UI verification relies primarily on machine evidence**: for PAGES with no differences, write "machine evidence sign-off" in the `Review method` column; only PAGES with differences or `UI-DERIVED` are written as "manual review", with the reason and approver given in the `Difference` column.

| PAGE | Design source reference (HTML data-node-id / Figma node) | Assertion elements/max deviation | Layout evidence | Difference | Conclusion | Approver | Review method |
|---|---|---|---|---|---|---|---|
| PAGE-001 | `3:2` | `8 elements / 0.0px (tol 2px)` | `evidence/figma-layout-check.json#PAGE-001` | None | PASS | — | machine evidence sign-off |

> Conclusions may only be PASS / FIXED / APPROVED / DEVIATION_APPROVED / N/A; when there is a difference it must be DEVIATION_APPROVED with the approver named, otherwise stage 08 is blocked.
