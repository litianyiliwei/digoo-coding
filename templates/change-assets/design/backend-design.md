# Backend Detailed Design

- Change ID: `<change-id>`
- Status: `DRAFT | IN_REVIEW | APPROVED`
- Related specs / REQ / AC IDs: `<REQ-...; AC-...>`
- OpenAPI file: `api/openapi.yaml`
- Project baselines reused: `<paths + version/commit>`
- Baseline exception / ADR: `None` or `<ADR ID + approval status>`

> **Mandatory rule:** every business API operation in OpenAPI must map to one or more concrete I/O operations in `api-io-mapping.csv`. An I/O operation includes database/Mapper/SQL, file system, object storage, external HTTP/Feign, Redis, MQ, search/index, or another explicit infrastructure adapter. “调用 Service” is not itself an I/O operation. Each I/O operation must have a detailed row in `io-catalog.csv`. The mapping is a design gate, not an optional narrative.

## 1. API inventory and execution chain

| operationId | HTTP method/path | Controller | Application service | Domain operation(s) | API permission | Transaction boundary | Test IDs |
|---|---|---|---|---|---|---|---|
| `<must match OpenAPI>` | TODO | TODO | TODO | TODO | TODO | TODO | TEST-... |

For every operationId, describe the ordered I/O sequence in the next section and keep it consistent with `api-io-mapping.csv`.

## 2. API → I/O operation mapping (mandatory, one-to-many)

Machine-checkable source: `api-io-mapping.csv`. `sequence` 从 1 开始；数字递增表示执行顺序，相同序号可表示并行 IO（需在 notes 中明确并行依赖/汇合条件）。

| operationId | Sequence | IO ID | Required? | Transaction/consistency scope | Failure handling / compensation | Test IDs |
|---|---:|---|---|---|---|---|
| `<operationId>` | 1 | `IO-DB-001` | Yes | `TX-001` / N/A | TODO | TEST-001 |
| `<operationId>` | 2 | `IO-HTTP-001` | Conditional | Outside TX / TODO | timeout / retry / compensation TODO | TEST-002 |

**Review conditions:**
- Every operationId in OpenAPI appears in the mapping.
- Each API maps to at least one IO ID; multiple rows represent multiple calls and must specify order.
- Every IO ID exists in `io-catalog.csv`; no unmapped catalog row is allowed unless its `notes` explicitly explains why it is predesigned but not currently used.
- For a genuinely pure-computation/health endpoint with no I/O, do not silently omit the mapping. Use `NO_IO_EXCEPTION` in `io_id`, fill `no_io_reason` and `approved_by`, and obtain explicit approval. Strict checks must fail if either field is missing. This is a documented exception, not the default.
- If one endpoint updates a database and publishes a message, explicitly document the outbox/transactional publish strategy or the consistency/compensation strategy. Do not imply a DB transaction can atomically cover a remote HTTP request or ordinary MQ publish unless the design actually provides that guarantee.

## 3. I/O operation catalog

Machine-checkable source: `io-catalog.csv`; the table below is the human-readable detail.

| IO ID | Type | Resource/client | Operation / SQL / file path | Input contract | Output contract | Transaction / consistency | Timeout | Retry | Idempotency | Errors & mapping | Observability | Test IDs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `IO-DB-001` | `DB_READ` | `OrderMapper` | `selectById` | `orderId: UUID` | `Order?` | `TX-001` | N/A | N/A | Read-only | not found behavior | trace + duration | TEST-001 |

### 3.1 Database / Mapper / SQL / DDL / migration detail

For each database IO ID, specify:
- Physical table/view and columns read/written; SQL or Mapper method signature.
- Filters, sorting, pagination, uniqueness, indexes and expected cardinality.
- Transaction boundary, isolation assumptions, lock/optimistic version strategy and race conditions.
- Constraint violations and mapping to domain/API errors.
- Migration forward/rollback strategy, backward compatibility and deployment order.
- Data privacy, retention, audit trail and masking where applicable.

| IO ID | Mapper/repository method | Tables/columns | Read/write | Query/constraint/index | Concurrency/transaction | Error mapping | Migration impact |
|---|---|---|---|---|---|---|---|
| `IO-DB-001` | TODO | TODO | R/W | TODO | TODO | TODO | None / TODO |

### 3.2 Non-database I/O contracts

For each File I/O / object storage / Feign / HTTP / Redis / MQ / search / external SDK operation, specify:
- Client abstraction and method signature, including input/output schema.
- Destination/resource and data classification; authentication and secrets source.
- Timeout, retry budget/backoff, retryable vs non-retryable failures, circuit breaker/bulkhead where applicable.
- Idempotency key, deduplication, ordering, delivery semantics, dead-letter/compensation when applicable.
- Error translation, partial failure behavior, metrics/logs/traces and redaction.
- Test double and integration-test strategy.

| IO ID | Client/interface signature | Resource/destination | Input/output | Timeout/retry | Idempotency/delivery | Error/compensation | Observability | Test IDs |
|---|---|---|---|---|---|---|---|---|
| `IO-HTTP-001` | TODO | TODO | TODO | TODO | TODO | TODO | TODO | TEST-002 |

## 4. Domain types and methods

| Type / method ID | Type/method signature | Responsibility / invariant | Parameters / return | Side effects / I/O IDs | Exceptions | Unit tests |
|---|---|---|---|---|---|---|
| `DOM-OP-001` | TODO | TODO | TODO | `IO-DB-001` via repository / or none | TODO | TEST-... |

Domain methods should express business rules; they must not hide infrastructure I/O inside entities/value objects. State which application-service/repository/client boundary performs each I/O operation.

## 5. API logic and error paths

| operationId | Ordered business steps | Validation/authorization | Success response | Failure scenarios | Idempotency/concurrency | I/O IDs |
|---|---|---|---|---|---|---|
| `<operationId>` | 1. ... | TODO | TODO | TODO | TODO | `IO-...;IO-...` |

Describe for every step where the transaction starts/ends and what happens if each I/O operation fails. Include compensation, retry, deduplication or a deliberate no-compensation rationale.

## 6. Shared concerns

- Transaction and consistency model: TODO
- Locking / optimistic version / deduplication: TODO
- Authentication/authorization and object-level access: TODO
- Audit, logs, metrics, traces and sensitive-field masking: TODO
- Timeouts, retry budgets, circuit breaker and graceful degradation: TODO
- Performance assumptions and query budgets: TODO
- Migration/deploy/rollback sequence: TODO

## 7. Test coverage linked to API and I/O

| API operationId | IO ID | Unit test | Integration/contract test | Failure injection | Expected assertion |
|---|---|---|---|---|---|
| `<operationId>` | `IO-DB-001` | TEST-001 | TEST-002 | DB timeout / constraint violation | TODO |

At minimum test important success and failure paths for each API and each side-effecting I/O. Verify that DB state, remote side effects, retries, duplicate requests and compensation match the specification.

## 8. Unresolved decisions

| Question ID | Decision needed | Impacted operationId / IO ID | Owner | Blocking? | Due/condition |
|---|---|---|---|---|---|
| Q-001 | TODO | TODO | TODO | Yes/No | TODO |
