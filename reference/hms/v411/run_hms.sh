#!/usr/bin/sh

# usage: ./run_hms.sh '{"hms_schema":{"project_file":"/data/samples/tenk/tenk.hms","sim_name":"Jan 96 storm"}}'
if [ $# -eq 1 ]; then
    CONFIG_JSON_STR="$1"
    echo "Received JSON config: $CONFIG_JSON_STR"
    PROJFILE=$(echo "$CONFIG_JSON_STR" | jq -r '.hms_schema.project_file')
    SIMNAME=$(echo "$CONFIG_JSON_STR" | jq -r '.hms_schema.sim_name')
    echo "Parsed project_file: $PROJFILE"
    echo "Parsed sim_name: $SIMNAME"

else
    PROJFILE=$1
    SIMNAME=$2
    echo "Received PROJFILE: $PROJFILE"
    echo "Received SIMNAME: $SIMNAME"
fi

set -e

echo ""
echo "---------Run HMS Simulation----------"
echo ""
echo "PROJFILE: $PROJFILE"
echo "SIMNAME: $SIMNAME"
echo "Sending $SIMNAME to hms-compute"

java \
  -XX:+ExitOnOutOfMemoryError \
  -XX:MaxRAMPercentage=75 \
  -XX:+UseContainerSupport \
  -Djava.library.path=/HEC-HMS-4.11/bin/gdal:/HEC-HMS-4.11/bin \
  -jar /HEC-HMS-4.11/lib/hms-compute.jar \
  "$PROJFILE" \
  "$SIMNAME"

if [ $? -eq 0 ]; then
    echo "✅ HMS simulation completed successfully."
    exit 0
else
    echo "❌ HMS simulation failed!" >&2
    exit 1
fi