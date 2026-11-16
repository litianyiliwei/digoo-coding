# Independent Verification Report

- Change ID:
- Verifier (Agent/person/independent session ID):
- Builder (Agent/person/session ID):
- Verification time:
- Verdict: PASS / FAIL / BLOCKED
- Revision under test (commit or diff fingerprint):
- Whether the Revision remained unchanged during verification: YES / NO
- Whether the read-only constraint was observed: YES / NO

## 1. Verification Scope and Input Versions

| Input | Path/version | Read | Approval status |
|---|---|---|---|
| OpenSpec proposal/specs/design/tasks | | | |
| baseline-impact and baseline version | | | |
| OpenAPI / API-IO / IO catalog | | | |
| Frontend/backend detailed design / test design | | | |

## 2. Acceptance Criteria Verification

| AC ID | Expected behavior | Verification method | Evidence path/test | Result PASS/FAIL/NOT_RUN |
|---|---|---|---|---|

## 3. Test and Check Execution Evidence

| Command | Exit code | Result | Log/report path |
|---|---:|---|---|

## 4. Contract and Engineering Constraint Checks

- API → IO mapping:
- IO contract/transactions/idempotency/exceptions:
- Data migration and compatibility:
- Permissions/security/privacy:
- Baseline constraints:
- OpenSpec tasks:

## UI Consistency Verification (required for UI Changes)

> Use the independently re-run runtime geometry assertions in `evidence/figma-layout-check.json` for each PAGE; do not use screenshots.
> `layout_checks` must be consistent with the table in this document; if any PAGE lacks evidence, exceeds tolerance, or has unapproved differences, the Verdict must not be PASS.

| PAGE | Figma node | Number of assertion elements | Max deviation | Missing/difference | Verdict |
|---|---|---|---|---|---|
| PAGE-001 | `3:2` | 8 | 0.0px / tol 2px | None | PASS/FAIL/NOT_RUN |

## 5. Findings

| ID | Severity | Description | Reproduction steps/evidence | Responsible stage |
|---|---|---|---|---|

## 6. Not-Executed Items and Limitations

| Check item | Reason not executed | Blocking |
|---|---|---|

## 7. Final Verdict

- Verdict: PASS / FAIL / BLOCKED
- Allowed to enter manual acceptance: YES / NO
- Return stage and remediation requirements:
- Verifier notes:
