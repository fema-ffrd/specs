#!/usr/bin/env bash
set -euo pipefail
VALIDATE=/usr/local/bin/validate
RESOLVE=/usr/local/bin/resolve-config

# Require JSON config as first argument and validate it using /usr/bin/validate only
if [ $# -lt 1 ]; then
  echo "❌ JSON config must be provided as the first argument. Validation is required. Aborting."
  exit 1
fi


JSON_PAYLOAD="$1"
RUN_SCRIPT=./hms_cli.py
SCHEMA="action.hms.run_simulation.json"

echo "🔍 Running schema validation..."
if ! python3 "$VALIDATE" -s "$SCHEMA" -i "$JSON_PAYLOAD"; then
  echo "❌ Validation failed. Aborting."
  exit 1
fi

# python3 $RUN_SCRIPT $JSON_PAYLOAD
RESOLVED_CONFIG=$($RESOLVE --verbose "$JSON_PAYLOAD")
echo "$RESOLVED_CONFIG" | jq

# echo $RESOLVED_CONFIG | python3 $RUN_SCRIPT