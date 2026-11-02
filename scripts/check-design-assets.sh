#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 1 || $# -gt 3 ]]; then echo "Usage: $0 <change-id> [--strict] [--lint-api]" >&2; exit 2; fi
CHANGE_ID="$1"; shift
STRICT=0; LINT_API=0
for arg in "$@"; do case "$arg" in --strict) STRICT=1;; --lint-api) LINT_API=1;; *) echo "Unknown argument: $arg" >&2; exit 2;; esac; done
[[ "$CHANGE_ID" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] || { echo "Invalid change-id." >&2; exit 2; }
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$(command -v python3 || command -v python)"
[[ -n "$PY" ]] || { echo "Neither python3 nor python is available." >&2; exit 2; }
DIR="$ROOT/openspec/changes/$CHANGE_ID"
[[ -d "$DIR" ]] || { echo "Change not found: $DIR" >&2; exit 1; }
required=("$DIR/api/openapi.yaml" "$DIR/design/frontend-design.md" "$DIR/design/backend-design.md" "$DIR/design/test-design.md" "$DIR/design/api-io-mapping.csv" "$DIR/design/io-catalog.csv" "$DIR/traceability.csv")
missing=0; placeholders=0
for f in "${required[@]}"; do
  if [[ ! -s "$f" ]]; then echo "ERROR MISSING: ${f#$ROOT/}"; missing=1; continue; fi
  if grep -nE 'TODO|TBD|PENDING|待确认|待补充' "$f" >/dev/null; then echo "WARN PLACEHOLDER: ${f#$ROOT/}"; placeholders=1; fi
done
if (( missing )); then echo "Detailed design assets missing." >&2; exit 1; fi
if (( STRICT && placeholders )); then echo "Strict mode failed: design placeholders remain." >&2; exit 1; fi
trace_args=(--file "$DIR/traceability.csv")
if (( STRICT )); then trace_args+=(--strict); fi
"$PY" "$ROOT/scripts/check-traceability.py" "${trace_args[@]}"
io_args=("$DIR/api/openapi.yaml" "$DIR/design/api-io-mapping.csv" "$DIR/design/io-catalog.csv")
if (( STRICT )); then io_args+=(--strict); fi
"$PY" "$ROOT/scripts/check-api-io-mapping.py" "${io_args[@]}"
if (( LINT_API )); then bash "$ROOT/scripts/validate-openapi.sh" "$DIR/api/openapi.yaml"; fi
echo "Detailed design asset structure and API→IO mapping passed."
