#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$(command -v python3 || command -v python)"
[[ -n "$PY" ]] || { echo "Neither python3 nor python is available." >&2; exit 2; }
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cat > "$TMP/openapi.yaml" <<'EOF'
openapi: 3.1.0
info: {title: Test, version: 1.0.0}
paths:
  /orders/{id}:
    get:
      operationId: getOrder
      responses: {"200": {description: OK}}
  /orders:
    post:
      operationId: createOrder
      responses: {"201": {description: Created}}
x-api-scope: defined
EOF
cat > "$TMP/mapping.csv" <<'EOF'
operation_id,sequence,io_id,required,transaction_scope,failure_handling,test_ids,no_io_reason,approved_by,notes
getOrder,1,IO-DB-READ-001,Yes,TX-READ,Return 404 when missing,TEST-001,,,read by id
createOrder,1,IO-DB-WRITE-001,Yes,TX-CREATE,Rollback on constraint failure,TEST-002,,,insert order
createOrder,2,IO-MQ-PUBLISH-001,Yes,After commit / outbox,Outbox retry and dedupe,TEST-003,,,publish event
EOF
cat > "$TMP/catalog.csv" <<'EOF'
io_id,io_type,resource_or_client,operation,input_contract,output_contract,transaction_or_consistency,timeout_ms,retry_policy,idempotency,errors_and_mapping,observability,test_ids,notes
IO-DB-READ-001,DB_READ,OrderMapper,selectById,orderId UUID,Order?,TX-READ,N/A - local DB operation,N/A - no retry for read,read only,not found -> 404,trace + duration,TEST-001,read
IO-DB-WRITE-001,DB_WRITE,OrderMapper,insert,OrderDraft,Order,TX-CREATE,500,N/A - no retry within transaction,unique order id,conflict -> 409,trace + db duration,TEST-002,write
IO-MQ-PUBLISH-001,MQ_PUBLISH,OutboxPublisher,publishOrderCreated,OrderCreated,ack,outbox eventual consistency,1000,exponential backoff,consumer dedupe,send failure persists outbox,metric + trace,TEST-003,event
EOF
"$PY" "$ROOT/scripts/check-api-io-mapping.py" "$TMP/openapi.yaml" "$TMP/mapping.csv" "$TMP/catalog.csv" --strict
# Negative case: remove one API's mapping; it must fail.
grep -v '^getOrder,' "$TMP/mapping.csv" > "$TMP/bad-mapping.csv"
if "$PY" "$ROOT/scripts/check-api-io-mapping.py" "$TMP/openapi.yaml" "$TMP/bad-mapping.csv" "$TMP/catalog.csv" >/dev/null 2>&1; then
  echo "ERROR: missing API mapping was not rejected" >&2; exit 1
fi
# Explicit no-API case should pass only with x-api-scope: none and empty mapping/catalog.
cat > "$TMP/no-api.yaml" <<'EOF'
openapi: 3.1.0
info: {title: UI-only change, version: 1.0.0}
paths: {}
x-api-scope: none
EOF
printf 'operation_id,sequence,io_id,required,transaction_scope,failure_handling,test_ids,no_io_reason,approved_by,notes\n' > "$TMP/empty-mapping.csv"
printf 'io_id,io_type,resource_or_client,operation,input_contract,output_contract,transaction_or_consistency,timeout_ms,retry_policy,idempotency,errors_and_mapping,observability,test_ids,notes\n' > "$TMP/empty-catalog.csv"
"$PY" "$ROOT/scripts/check-api-io-mapping.py" "$TMP/no-api.yaml" "$TMP/empty-mapping.csv" "$TMP/empty-catalog.csv" --strict
# API with no mapping must fail.
if "$PY" "$ROOT/scripts/check-api-io-mapping.py" "$TMP/openapi.yaml" "$TMP/empty-mapping.csv" "$TMP/empty-catalog.csv" >/dev/null 2>&1; then
  echo "ERROR: API contract with no mapping was not rejected" >&2; exit 1
fi
echo "API→IO mapping positive/negative tests passed."
