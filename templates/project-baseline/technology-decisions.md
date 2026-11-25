# Technology Selection Decisions

> Change ID: N/A (project-level baseline)
> Status: PENDING
> Source baseline: PENDING
> Related requirement/AC IDs: PENDING
> Version/date: PENDING

> Record the technology selection interview, candidates, costs, and the user's confirmation. Unconfirmed selections stay PENDING with owner and blocking condition. Individual decisions promoted to ADRs are indexed in `docs/adr/README.md`.

## Interview Record

| Date | Participants | Question | Answer |
|---|---|---|---|
| PENDING | PENDING | PENDING | PENDING |

## Candidate Comparison

| Domain | Option | Pros | Cons | Cost | Existing-system Constraints | Verdict |
|---|---|---|---|---|---|---|
| PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |

## Selection and Reasons

PENDING — domain → selected option → reason → ADR ID (when one exists).

## Static Analysis Toolchain

> 03 adoption decision (also recorded in `## Interview Record`): ask the user/technical lead whether static-analysis gates are adopted. If **not adopted**, write `N/A + reason` here and in `test-strategy.md`, do not create `docs/architecture/quality-gates.json`, keep it out of the `test_quality` file list, and leave `QUALITY-STATIC-001` RETIRED. If **adopted**, per selected language choose tools, pin versions, list packages/plugins, decide config landing paths, severity policy, and waiver policy. Installation is an explicitly authorized task at 08, never automatic. The machine-readable result is `docs/architecture/quality-gates.json`; starter configs live in `templates/static-analysis/`. Every selected language must have at least one blocking stack unless `test-strategy.md` records `N/A + reason`.

- Adoption decision: PENDING — adopted / not adopted, reason, confirmer, date.

| Language | Chosen tools | Version/pinning | Package/plugin list | Config landing paths | Severity and waiver policy | Rejected alternatives |
|---|---|---|---|---|---|---|
| PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |

- Selected pack(s): PENDING — `templates/static-analysis/<language>/` copied to which stack root at 08.
- Deviations from the shipped rule pack: PENDING — rule/path change, reason, and where it is recorded (`quality-gates.json` wins for execution).
- Confirmation: PENDING — owner/approver and date of the selection decision.

## Existing System Secondary-Development Constraints

> Required when the system origin is secondary development on an existing system; for a new system, write `N/A + reason`. The code address must actually have been read; record the areas read and the constraints converted to `LEGACY-*` in `constraint-registry.json`.

| System origin | Code address (repository/branch/commit) | Areas actually read | Constraints (→ `LEGACY-*`) | Compatibility/rollback notes |
|---|---|---|---|---|
| PENDING | PENDING | PENDING | PENDING | PENDING |

## Third-Party Interface Dependency List

> List every third-party interface the architecture depends on; write `NONE + reason` when there are none. The EXTERNAL data flows in `data-flows.md` and the integration conventions in `api-conventions.md` must match this table.

| Provider | Purpose | Protocol | Authentication | SLA/quota | Sandbox/test account | Approval | Data sharing/privacy | Owner |
|---|---|---|---|---|---|---|---|---|
| PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING | PENDING |

### Third-Party Library Licenses

| Dependency | Version | License | Upgrade Policy | Risk |
|---|---|---|---|---|
| PENDING | PENDING | PENDING | PENDING | PENDING |

## Confirmation

| Domain | Confirmed by | Date | Evidence |
|---|---|---|---|
| PENDING | PENDING | PENDING | PENDING |

## Pending Items

- PENDING — unknown selection, owner, blocking condition.
