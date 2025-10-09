#!/usr/bin/env bash
set -euo pipefail

VALIDATE=/usr/local/bin/validate
COMPILE_SCRIPT=/usr/local/bin/compile-workflow
SCHEMA="workflow.json"

# Accept JSON config as first argument or from stdin
if [ $# -lt 1 ]; then
  if [ -t 0 ]; then
    echo "❌ JSON config must be provided as the first argument or piped via stdin. Aborting." >&2
    exit 1
  fi
  JSON_PAYLOAD=$(cat)
else
  JSON_PAYLOAD="$1"
fi

echo "🔍 Running schema validation..." >&2
if ! python3 "$VALIDATE" -s "$SCHEMA" -i "$JSON_PAYLOAD" >&2; then
  echo "❌ Validation failed. Aborting." >&2
  exit 1
fi

echo "✅ Validation successful. Compiling workflow..." >&2
python3 "$COMPILE_SCRIPT" "$JSON_PAYLOAD"
