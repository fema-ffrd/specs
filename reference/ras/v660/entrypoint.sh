#!/usr/bin/env bash
set -euo pipefail
VALIDATE=/usr/local/bin/validate
RESOLVE=/usr/local/bin/resolve-config

# Require JSON config as first argument and validate it using /usr/bin/validate only
# Accept JSON config as first argument or from stdin
if [ $# -lt 1 ]; then
  if [ -t 0 ]; then
    echo "❌ JSON config must be provided as the first argument or piped via stdin. Aborting."
    exit 1
  fi
  JSON_PAYLOAD=$(cat)
else
  JSON_PAYLOAD="$1"
fi
RUN_SCRIPT=./run_unsteady.py
SCHEMA="action.ras.run_unsteady_simulation.json"

echo "🔍 Running schema validation..."
if ! python3 "$VALIDATE" -s "$SCHEMA" -i "$JSON_PAYLOAD"; then
  echo "❌ Validation failed. Aborting."
  exit 1
fi

# RESOLVED_CONFIG=$($RESOLVE --verbose "$JSON_PAYLOAD")
# echo $RESOLVED_CONFIG

python3 $RUN_SCRIPT $JSON_PAYLOAD