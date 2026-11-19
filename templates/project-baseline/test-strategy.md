# Test Strategy

> Change ID: N/A (project-level baseline)
> Status: PENDING
> Source baseline: PENDING
> Related requirement/AC IDs: PENDING
> Version/date: PENDING

## Test Levels

| Level | Scope | Owner | Required for |
|---|---|---|---|
| PENDING | PENDING | PENDING | PENDING |

## Commands

| Purpose | Command | Environment |
|---|---|---|
| PENDING | PENDING | PENDING |

## Environments

| Environment | Purpose | Data | Access |
|---|---|---|---|
| PENDING | PENDING | PENDING | PENDING |

## Quality Gates

- PENDING — which commands must pass before review, before independent verification, and before acceptance.
- Static analysis is adopted by a 03 decision: when adopted, the machine-readable source of truth is `docs/architecture/quality-gates.json` (validated by `python scripts/check-quality-gates.py --strict`; materialized and green at 08/09/CI). When not adopted, record `N/A + reason` here and in `technology-decisions.md`; the static-analysis sections and commands stay dormant.

## Static Analysis and Quality Gates

> Applicable when the project adopts static analysis at 03. The JSON wins for execution; this section explains the decisions. Undecided values stay `PENDING` with owner and blocking condition until 03 freezes the baseline. When not adopted, write `N/A + reason` and skip the table and command rows below; the 03 decision covers tool selection, version pinning, packages/plugins, config landing paths, severity policy, and waiver policy.

| Stack id | Language | Stack root | Config landing paths | Blocking tools | Command list (mirrors `quality-gates.json`) | Blocking policy | Deliberate advisory items |
|---|---|---|---|---|---|---|---|
| PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | Errors block (`blocking_severities: ["error"]`); warnings and style findings are advisory and never fail a gate. Zero-warning is not required | PENDING |

- Tier policy: correctness/security/type-error rules are blocking; style/format/suggestion rules are advisory (`mode: "advisory"`) and are recorded in evidence but never fail the gate. A zero-warning run is not required.

### Waiver Policy

- Scope: Change-scoped only (`openspec/changes/<change-id>/design/static-waivers.json`, per `policy.waiver_file`); waivers are never stored in the frozen gates file.
- Approver: PENDING — a named real approver is required (`policy.waiver.requires_approver: true`).
- Maximum lifetime: 90 days (`policy.waiver.max_days`; PENDING — confirm the value at 03 freeze).
- Recording: every applied waiver is summarized in `code-review.md` `## Static analysis` and reconciled in `acceptance.md`. Inline suppression without a matching waiver is a blocking 09 finding even when the tool exits 0.
- Reuse: a waiver expires with its Change; if the exception is still needed, it is re-recorded in the next Change.

### Which Command Runs Where

| Stage | Command | Required outcome |
|---|---|---|
| 03 Overall architecture (structure only) | `python scripts/check-quality-gates.py --strict` | when adopted: exit 0 with stack roots/configs declared, not required materialized; when not adopted: `QUALITY_GATES_NOT_ADOPTED` and exit 0 |
| 08 Implementation | `python scripts/check-quality-gates.py --strict --require-materialized`; `python scripts/run-quality-gates.py <change-id> --output openspec/changes/<change-id>/design/evidence/static-analysis.json`; `python scripts/check-static-analysis.py --change <change-id> --strict` | PASS; zero blocking findings; evidence written |
| 09 Independent verification | `python scripts/run-quality-gates.py <change-id> --independent --identity <verifier> --builder-identity <builder> --output openspec/changes/<change-id>/design/evidence/static-analysis-independent.json`; `python scripts/check-static-analysis.py --change <change-id> --expect-independent` | PASS; distinct verifier/builder identities |
| 10 Acceptance | `bash scripts/verify-before-completion.sh <change-id>` (includes the static gates) | PASS; no expired or invalid waiver |

- N/A policy: when adopted, a selected language with no practical static-analysis stack records `N/A + reason` in both this section and `technology-decisions.md`; otherwise every selected language has at least one blocking stack. When static analysis is not adopted, the whole section is `N/A + reason`.

## Flaky Test Policy

- PENDING — detection, quarantine rules, owner, re-enable condition.
</content>
