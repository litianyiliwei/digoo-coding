#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 1 ]]; then echo "Usage: $0 <change-id>" >&2; exit 2; fi
CHANGE_ID="$1"
[[ "$CHANGE_ID" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] || { echo "Invalid change-id: use lowercase kebab-case." >&2; exit 2; }
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON="$(command -v python3 || command -v python)" || { echo "python3/python not found in PATH" >&2; exit 2; }
CHANGE_DIR="$ROOT/openspec/changes/$CHANGE_ID"
TEMPLATE_DIR="$ROOT/templates/change-assets"
[[ -d "$CHANGE_DIR" ]] || { echo "Change does not exist: $CHANGE_DIR. Create it first with openspec new change <id>." >&2; exit 1; }
mkdir -p "$CHANGE_DIR/api" "$CHANGE_DIR/design" "$CHANGE_DIR/evidence"
created=0; skipped=0
while IFS= read -r -d '' src; do
  rel="${src#"$TEMPLATE_DIR/"}"
  # baseline-binding.json is generated from the live frozen Manifest/registry, never copied as a placeholder.
  [[ "$rel" == "design/baseline-binding.json" ]] && continue
  dst="$CHANGE_DIR/$rel"
  mkdir -p "$(dirname "$dst")"
  if [[ -e "$dst" ]]; then echo "SKIP existing: $dst"; skipped=$((skipped+1)); else cp "$src" "$dst"; echo "CREATED: $dst"; created=$((created+1)); fi
done < <(find "$TEMPLATE_DIR" -type f -print0)
echo "Created $created asset(s); preserved $skipped existing asset(s)."
if [[ ! -f "$CHANGE_DIR/design/baseline-impact.md" ]]; then
  echo "ERROR: mandatory design/baseline-impact.md template was not created." >&2
  exit 1
fi
echo "Mandatory baseline impact record: $CHANGE_DIR/design/baseline-impact.md"
if [[ ! -f "$CHANGE_DIR/design/baseline-binding.json" ]]; then
  "$PYTHON" "$ROOT/scripts/baseline-governance.py" init-binding --change-id "$CHANGE_ID"
else
  echo "PRESERVED existing baseline binding: $CHANGE_DIR/design/baseline-binding.json"
fi
echo "This helper creates supplemental files only; it does not generate OpenSpec proposal/spec/design/tasks artifacts."
