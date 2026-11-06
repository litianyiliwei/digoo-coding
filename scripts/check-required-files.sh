#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STRICT=0
if [[ "${1:-}" == "--strict" ]]; then STRICT=1; shift; fi
if [[ $# -gt 0 ]]; then echo "Usage: $0 [--strict]" >&2; exit 2; fi
cd "$ROOT"

required=(
  "docs/product/requirements-analysis.md"
  "docs/product/glossary.md"
  "docs/product/workflows.md"
  "docs/product/data-objects.csv"
  "docs/product/rd-matrix.csv"
  "docs/product/business-rules.md"
  "docs/product/acceptance-policy.md"
  "docs/product/open-questions.md"
  "docs/architecture/system-context.md"
  "docs/architecture/technology-decisions.md"
  "docs/architecture/containers-and-deployment.md"
  "docs/architecture/data-flows.md"
  "docs/architecture/logical-erd.md"
  "docs/architecture/domain-boundaries.md"
  "docs/architecture/api-conventions.md"
  "docs/architecture/frontend-conventions.md"
  "docs/architecture/test-strategy.md"
  "docs/architecture/baseline-status.md"
  "docs/project/baseline-audit-report.md"
  "docs/TEMPLATE-POLICY.md"
  "docs/OUTPUT-TEMPLATE-MATRIX.csv"
)
missing=0
placeholders=0
for f in "${required[@]}"; do
  if [[ ! -s "$f" ]]; then echo "ERROR MISSING: $f"; missing=1; continue; fi
  if grep -nE 'TODO(:|\b)|TBD|\[填充\]|待确认' "$f" >/dev/null; then
    echo "WARN PLACEHOLDER: $f"
    placeholders=1
  fi
done
if (( missing )); then echo "Required baseline files missing/empty." >&2; exit 1; fi
if (( STRICT && placeholders )); then echo "Strict mode failed: baseline templates still contain placeholders." >&2; exit 1; fi
echo "Required baseline file presence check passed."
if (( placeholders )); then echo "Warning: placeholders remain. Use --strict to enforce a fully populated baseline."; fi
