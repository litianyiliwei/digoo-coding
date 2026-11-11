#!/usr/bin/env bash
set -euo pipefail
if [[ $# -lt 1 || $# -gt 3 ]]; then echo "Usage: $0 <change-id> [--strict] [--lint-api]" >&2; exit 2; fi
CHANGE_ID="$1"; shift
STRICT=0; LINT_API=0
for arg in "$@"; do case "$arg" in --strict) STRICT=1;; --lint-api) LINT_API=1;; *) echo "Unknown argument: $arg" >&2; exit 2;; esac; done
[[ "$CHANGE_ID" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] || { echo "Invalid change-id." >&2; exit 2; }
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$(command -v python3 || command -v python)" || { echo "python3/python not found in PATH" >&2; exit 2; }
DIR="$ROOT/openspec/changes/$CHANGE_ID"
[[ -d "$DIR" ]] || { echo "Change not found: $DIR" >&2; exit 1; }

DESIGN="$DIR/design.md"
TRACE="$DIR/traceability.csv"
TEST_CASES="$DIR/design/test-cases.csv"
OPENAPI="$DIR/api/openapi.yaml"
API_MAP="$DIR/design/api-io-mapping.csv"
IO_CATALOG="$DIR/design/io-catalog.csv"

required=("$DESIGN" "$TRACE" "$TEST_CASES")
missing=0
for f in "${required[@]}"; do
  if [[ ! -s "$f" ]]; then echo "ERROR MISSING: ${f#$ROOT/}"; missing=1; fi
done
if (( missing )); then echo "Core design assets missing." >&2; exit 1; fi

# design.md must carry the five unified sections.
for section in '## 设计决策' '## 接口设计' '## 前端详细设计' '## 后端详细设计' '## 测试设计'; do
  if ! grep -qF "$section" "$DESIGN"; then echo "ERROR MISSING SECTION: design.md -> $section"; missing=1; fi
done
if (( missing )); then echo "design.md is missing unified design sections." >&2; exit 1; fi

# API assets are conditional: required only when OpenAPI actually defines operations.
API_SCOPE_NONE=0
if [[ -f "$OPENAPI" ]] && grep -Eq 'x-api-scope:[[:space:]]*none' "$OPENAPI"; then API_SCOPE_NONE=1; fi
if [[ ! -f "$OPENAPI" || $API_SCOPE_NONE -eq 0 ]]; then
  for f in "$OPENAPI" "$API_MAP" "$IO_CATALOG"; do
    if [[ ! -s "$f" ]]; then echo "ERROR MISSING: ${f#$ROOT/}"; missing=1; fi
  done
fi
if (( missing )); then echo "API design assets missing (or use x-api-scope: none)." >&2; exit 1; fi

placeholders=0
for f in "$DESIGN" "$TRACE" "$TEST_CASES" "$API_MAP" "$IO_CATALOG"; do
  [[ -f "$f" ]] || continue
  if grep -nE 'TODO|TBD|PENDING|待确认|待补充' "$f" >/dev/null; then echo "WARN PLACEHOLDER: ${f#$ROOT/}"; placeholders=1; fi
done
if (( STRICT && placeholders )); then echo "Strict mode failed: design placeholders remain." >&2; exit 1; fi

trace_args=(--file "$TRACE")
if (( STRICT )); then trace_args+=(--strict); fi
"$PYTHON" "$ROOT/scripts/check-traceability.py" "${trace_args[@]}"

test_args=(--change "$CHANGE_ID")
if (( STRICT )); then test_args+=(--strict); fi
"$PYTHON" "$ROOT/scripts/check-test-cases.py" "${test_args[@]}"

section_args=(--change "$CHANGE_ID")
if (( STRICT )); then section_args+=(--strict); fi
"$PYTHON" "$ROOT/scripts/check-design-sections.py" "${section_args[@]}"

api_trace_args=(--change "$CHANGE_ID")
if (( STRICT )); then api_trace_args+=(--strict); fi
"$PYTHON" "$ROOT/scripts/check-api-traceability.py" "${api_trace_args[@]}"

# UI-bearing Changes must have consumed the real Figma design (not screenshots/guesses).
# No-UI Changes either carry a figma-audit.md with 设计来源状态：N/A + 理由, or closed
# stage 06 explicitly with --no-ui; in the latter case there is no file to re-check here.
if [[ -f "$DIR/design/figma-audit.md" ]]; then
  figma_args=(--change "$CHANGE_ID")
  if (( STRICT )); then figma_args+=(--strict); fi
  "$PYTHON" "$ROOT/scripts/check-figma-audit.py" "${figma_args[@]}"
else
  echo "Figma audit: design/figma-audit.md absent; stage 06 must have declared no UI."
fi

if [[ -f "$OPENAPI" && $API_SCOPE_NONE -eq 0 ]]; then
  io_args=("$OPENAPI" "$API_MAP" "$IO_CATALOG")
  if (( STRICT )); then io_args+=(--strict); fi
  "$PYTHON" "$ROOT/scripts/check-api-io-mapping.py" "${io_args[@]}"
  if (( LINT_API )); then bash "$ROOT/scripts/validate-openapi.sh" "$OPENAPI"; fi
else
  echo "API scope: none (x-api-scope: none); API→IO checks skipped."
fi
echo "Unified design (design.md sections), test-case matrix, traceability and API→IO mapping passed."
