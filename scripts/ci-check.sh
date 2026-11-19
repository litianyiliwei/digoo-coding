#!/usr/bin/env bash
# Repository-level CI entry point. Safe to run locally; does not mutate state.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# check-package.py already runs the step-contract, output-consumption,
# output-template-matrix and stage-io-overview checks; do not repeat them here.
python scripts/check-package.py
bash scripts/test-scripts.sh
python scripts/gen-manifest.py --check
python scripts/check-layout.py --mode auto
if [[ -f toolkit-lock.json ]]; then
  python scripts/toolkit-sync.py verify --require-lock
fi

if [[ -f docs/architecture/baseline-manifest.json ]]; then
  bash scripts/check-required-files.sh --strict
  python scripts/baseline-governance.py audit --require-frozen
  python scripts/check-requirements.py --strict
  python scripts/check-reference-research.py --strict
  python scripts/check-architecture-baseline.py --strict
else
  echo "SKIP_PROJECT_BASELINE_CHECKS=not-initialized"
fi

if [[ -f docs/architecture/quality-gates.json ]]; then
  python scripts/check-quality-gates.py --root . --strict --require-materialized
else
  echo "SKIP_STATIC_GATES=not-adopted"
fi

echo "CI_CHECKS_PASSED"
