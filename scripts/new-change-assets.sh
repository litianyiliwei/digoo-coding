#!/usr/bin/env bash
set -euo pipefail
if [[ $# -ne 1 ]]; then echo "Usage: $0 <change-id>" >&2; exit 2; fi
CHANGE_ID="$1"
[[ "$CHANGE_ID" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]] || { echo "Invalid change-id: use lowercase kebab-case." >&2; exit 2; }
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CHANGE_DIR="$ROOT/openspec/changes/$CHANGE_ID"
TEMPLATE_DIR="$ROOT/templates/change-assets"
[[ -d "$CHANGE_DIR" ]] || { echo "Change does not exist: $CHANGE_DIR. Create it first with openspec new change <id>." >&2; exit 1; }
mkdir -p "$CHANGE_DIR/api" "$CHANGE_DIR/design" "$CHANGE_DIR/evidence"
created=0; skipped=0
while IFS= read -r -d '' src; do
  rel="${src#"$TEMPLATE_DIR/"}"
  dst="$CHANGE_DIR/$rel"
  mkdir -p "$(dirname "$dst")"
  if [[ -e "$dst" ]]; then echo "SKIP existing: $dst"; skipped=$((skipped+1)); else cp "$src" "$dst"; echo "CREATED: $dst"; created=$((created+1)); fi
done < <(find "$TEMPLATE_DIR" -type f -print0)
echo "Created $created asset(s); preserved $skipped existing asset(s)."
echo "This helper creates supplemental files only; it does not generate OpenSpec proposal/spec/design/tasks artifacts."
