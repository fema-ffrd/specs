#!/usr/bin/env bash
set -euo pipefail
VALIDATE=/usr/local/bin/validate

# Require JSON config as first argument and validate it using /usr/bin/validate only
if [ $# -lt 1 ]; then
  echo "❌ JSON config must be provided as the first argument. Validation is required. Aborting."
  exit 1
fi


JSON_PAYLOAD="$1"
RUN_SCRIPT=./run_unsteady.py
SCHEMA="action.ras.run_unsteady_simulation.json"

echo "🔍 Running schema validation..."
if ! python3 "$VALIDATE" -s "$SCHEMA" -i "$JSON_PAYLOAD"; then
  echo "❌ Validation failed. Aborting."
  exit 1
fi

python3 $RUN_SCRIPT $JSON_PAYLOAD