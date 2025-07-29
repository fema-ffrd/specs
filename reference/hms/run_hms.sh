#!/usr/bin/sh

# usage: ./run_hms.sh '{"project_file":"/data/tenk","sim_name":"Jan 96 storm"}'
if [ $# -eq 1 ]; then
    CONFIG_JSON_STR="$1"
    echo "Received JSON config: $CONFIG_JSON_STR"
    PROJFILE=$(echo "$CONFIG_JSON_STR" | jq -r '.hms_schema.project_file')
    SIMNAME=$(echo "$CONFIG_JSON_STR" | jq -r '.hms_schema.sim_name')
    echo "Parsed project_file: $PROJFILE"
    echo "Parsed sim_name: $SIMNAME"
    SIMDIR=$(dirname "$PROJFILE")
else
    SIMDIR=$1
    PROJFILE=$2
    echo "Received SIMDIR: $SIMDIR"
    echo "Received PROJFILE: $PROJFILE"
fi

#!/bin/bash
set -e

echo ""
echo "---------Run HMS Simulation----------"
echo ""
echo "SIMDIR: $SIMDIR"
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