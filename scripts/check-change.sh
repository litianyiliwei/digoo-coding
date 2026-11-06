#!/usr/bin/env bash
set -euo pipefail

usage() { echo "Usage: $0 <change-id|openspec/changes/<change-id>> [--no-openspec]"; }
if [[ $# -lt 1 || $# -gt 2 ]]; then usage >&2; exit 2; fi
ARG="$1"
SKIP_OPENSPEC=0
if [[ "${2:-}" == "--no-openspec" ]]; then SKIP_OPENSPEC=1; elif [[ $# -eq 2 ]]; then usage >&2; exit 2; fi
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
if [[ "$ARG" == openspec/changes/* ]]; then CHANGE_DIR="$ROOT/$ARG"; CHANGE_ID="${ARG##*/}"; else CHANGE_ID="$ARG"; CHANGE_DIR="$ROOT/openspec/changes/$CHANGE_ID"; fi
if [[ ! "$CHANGE_ID" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then echo "Invalid change-id: $CHANGE_ID (use lowercase kebab-case)." >&2; exit 2; fi
if [[ ! -d "$CHANGE_DIR" ]]; then echo "Change directory not found: $CHANGE_DIR" >&2; exit 1; fi

missing=0
for f in proposal.md design.md tasks.md; do
  if [[ ! -s "$CHANGE_DIR/$f" ]]; then echo "ERROR MISSING: $CHANGE_DIR/$f"; missing=1; fi
done
META="$CHANGE_DIR/.openspec.yaml"
SKIP_SPECS=0
if [[ -f "$META" ]] && grep -Eq '^skip_specs:[[:space:]]*true[[:space:]]*$' "$META"; then SKIP_SPECS=1; fi
if (( ! SKIP_SPECS )); then
  if [[ ! -d "$CHANGE_DIR/specs" ]] || ! find "$CHANGE_DIR/specs" -type f -name spec.md -print -quit | grep -q .; then
    echo "ERROR MISSING: specs/<capability>/spec.md (unless .openspec.yaml sets skip_specs: true)"
    missing=1
  fi
fi
if [[ -s "$CHANGE_DIR/tasks.md" ]] && ! grep -Eq '^[-*][[:space:]]+\[[ xX]\][[:space:]]+' "$CHANGE_DIR/tasks.md"; then
  echo "ERROR: tasks.md has no Markdown checkbox tasks (- [ ] / - [x]); OpenSpec won't track progress correctly."
  missing=1
fi
if (( missing )); then echo "Change structure check failed." >&2; exit 1; fi
if (( ! SKIP_OPENSPEC )); then
  if (( SKIP_OPENSPEC == 0 )); then
    if ! command -v openspec >/dev/null 2>&1; then
      echo "OpenSpec CLI not found. Install/configure it or explicitly pass --no-openspec for structural-only validation." >&2
      exit 2
    fi
    (cd "$ROOT" && openspec validate "$CHANGE_ID" --strict)
  fi
else
  echo "WARNING: OpenSpec semantic validation explicitly skipped (--no-openspec)."
fi
echo "Change structural checks passed: $CHANGE_ID"
