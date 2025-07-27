#!/bin/bash
set -e

CONFIG_JSON="$1"

validate "$CONFIG_JSON"

mkdir -p /configs

echo "$CONFIG_JSON" > /configs/conformance.json

download_from_config "$CONFIG_JSON"

MODELDIR=$(echo "$CONFIG_JSON" | jq -r '.ras_schema.model_directory')
MODEL=$(echo "$CONFIG_JSON" | jq -r '.ras_schema.model_name')

/usr/local/bin/run-ras-model $MODELDIR $MODEL