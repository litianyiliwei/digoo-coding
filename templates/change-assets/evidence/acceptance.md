# Acceptance Evidence

- Change ID: TODO
- Acceptance owner: TODO
- Date/build: TODO
- Overall result: PENDING

| AC ID | Result | Evidence/test report | Defect/deviation | Reviewer |
|---|---|---|---|---|
| AC-001 | Pending | TODO | TODO | TODO |

## UI acceptance

> Acceptance relies primarily on machine evidence: `design/evidence/figma-layout-check.json` must be PASS. PAGES with no differences and not `UI-DERIVED` may be batch-signed off based on machine evidence, with `Acceptance method` written as "machine evidence sign-off"; only PAGES with differences, `UI-DERIVED`, or not covered by assertions require opening the running system UI side-by-side with the real Figma file/review draft for comparison, with `Acceptance method` written as "side-by-side verification". Screenshots are neither saved nor accepted as evidence.
> Per-PAGE rows must still be complete; if any PAGE is missing sign-off or its result is not ACCEPTED/DEVIATION_APPROVED, archiving must not proceed.

| PAGE | Result | Figma node | Running system entry (URL/route) | Difference/approval | Acceptance method | Reviewer |
|---|---|---|---|---|---|---|
| PAGE-001 | ACCEPTED | `3:2` | `http://127.0.0.1:5180/login` | None | machine evidence sign-off | Design owner |

## Static analysis

> When `docs/architecture/quality-gates.json` exists, acceptance re-runs `bash scripts/verify-before-completion.sh <change-id>` (the completion script includes the static gates by default; `--skip-static` is not full verification) and copies this section verbatim from `design/evidence/static-analysis.json` and `design/evidence/static-analysis-independent.json`: copy the stack id, tool id, command, configs (path @ sha256), result, and exit code from the evidence JSON; do not paraphrase. Rows must end with the literal `exit 0`. Expired/invalid waivers, a non-PASS verdict, or a drifted gates file block acceptance. When the project has not adopted quality gates, delete the data row and the waiver row and write `- Static analysis: N/A (no quality-gates.json)`.

| Stack | Tool | Command (from evidence) | Configs (path @ sha256) | Result | Exit code |
|---|---|---|---|---|---|
| frontend-web | eslint | `npx --no-install eslint --max-warnings 0 .` | `eslint.config.js @ <sha256>` | PASS | exit 0 |

Waived items copied from the evidence `waivers_applied` list (write `none` when empty) and their approver:

| Waiver id | File | Rule | Approved by | Expires at |
|---|---|---|---|---|
| PENDING | PENDING | PENDING | PENDING | PENDING |

## Open blockers and risks

TODO
