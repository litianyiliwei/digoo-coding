# Test Design

- Change ID: `<change-id>`
- Related specs / ACs: `<IDs>`
- Test strategy/version: `<reference>`

## AC/API/IO test matrix

| AC/REQ ID | Test ID | operationId | IO ID(s) | Layer | Preconditions/data | Steps | Expected result/assertion | Failure injection | Automation/command | Cleanup |
|---|---|---|---|---|---|---|---|---|---|---|
| AC-001 | TEST-001 | `getExample` | `IO-DB-001` | Integration | TODO | TODO | TODO | DB timeout/not found | TODO | TODO |

## Coverage rules

- Every acceptance criterion must map to at least one test, or record `N/A` with a reason and reviewer.
- Every OpenAPI `operationId` must have contract/API tests.
- Every `io_id` in `api-io-mapping.csv` must be covered by one or more relevant unit/integration/failure-injection tests.
- Side-effecting I/O must test success and important failure behavior; database I/O covers constraints, transaction rollback and concurrency where applicable.
- External dependencies specify fake/mock setup and at least one integration/contract verification strategy.

## External dependency fakes and environments

| IO ID | Fake/Mock | Integration environment | Secrets/config | Failure modes simulated |
|---|---|---|---|---|
| IO-HTTP-001 | TODO | TODO | TODO | timeout / 4xx / 5xx |

## Manual verification

| AC ID | Manual steps | Expected result | Reason not automated | Evidence path | Reviewer |
|---|---|---|---|---|---|
| AC-001 | TODO | TODO | TODO | evidence/acceptance.md | TODO |
