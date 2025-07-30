#!/bin/bash
set -e

CONFIG_JSON="$1"

validate "$CONFIG_JSON"

mkdir -p /configs

echo "$CONFIG_JSON" > /configs/conformance.json

download_from_config "$CONFIG_JSON"

# Extract HMS schema as a compact JSON string
PROJFILE=$(echo "$CONFIG_JSON" | jq -r '.hms_schema.project_file')
SIMNAME=$(echo "$CONFIG_JSON" | jq -r '.hms_schema.sim_name')

echo "Running HMS simulation for:"
echo "$PROJFILE"
echo "$SIMNAME"

/app/run_hms.sh "$PROJFILE" "$SIMNAME"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ HMS simulation completed successfully."
else
    echo "❌ HMS simulation failed!" >&2
    exit $EXIT_CODE
fi

MODELDIR=$(echo "$CONFIG_JSON" | jq -r '.ras_schema.model_directory')
MODEL=$(echo "$CONFIG_JSON" | jq -r '.ras_schema.model_name')

echo "Running RAS model with:"
echo "MODELDIR: $MODELDIR"
echo "MODEL: $MODEL"

if /usr/local/bin/run-ras-model "$MODELDIR" "$MODEL"; then
    echo "✅ RAS model simulation completed successfully."
else
    echo "❌ RAS model simulation failed!" >&2
    exit 1
fi