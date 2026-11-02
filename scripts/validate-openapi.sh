#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 1 ]]; then echo "Usage: $0 <openapi.yaml|openapi.yml|openapi.json>" >&2; exit 2; fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SPEC_INPUT="$1"
if [[ "$SPEC_INPUT" = /* ]]; then SPEC="$SPEC_INPUT"
elif [[ -f "$PWD/$SPEC_INPUT" ]]; then SPEC="$PWD/$SPEC_INPUT"
else SPEC="$ROOT/$SPEC_INPUT"
fi
[[ -s "$SPEC" ]] || { echo "OpenAPI file not found or empty: $SPEC_INPUT" >&2; exit 1; }

if command -v redocly >/dev/null 2>&1; then
  redocly lint "$SPEC"
elif command -v npx >/dev/null 2>&1; then
  echo "Using npx to resolve @redocly/cli (may require network access); pin a version in CI for reproducibility." >&2
  npx --yes @redocly/cli lint "$SPEC"
elif command -v docker >/dev/null 2>&1; then
  SPEC_DIR="$(dirname "$SPEC")"
  SPEC_NAME="$(basename "$SPEC")"
  docker run --rm -v "$SPEC_DIR:/work:ro" -w /work redocly/cli lint "$SPEC_NAME"
else
  echo "No Redocly CLI, npx, or Docker available; validation was NOT run." >&2
  exit 2
fi
