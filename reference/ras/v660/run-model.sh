#!/usr/bin/sh

# usage: ./run.sh '{"model_directory":"/sim/sample-model/","model_name":"Muncie", "plan_id":"4"}'
#        ./run.sh /sim/sample-model Muncie 4
#        ./run.sh /sim/sample-model Muncie 04

if [ $# -eq 1 ]; then
    CONFIG_JSON_STR="$1"
    MODELDIR=$(echo "$CONFIG_JSON_STR" | jq -r '.ras_schema.model_directory')
    MODEL=$(echo "$CONFIG_JSON_STR" | jq -r '.ras_schema.model_name')
    PLAN_ID=$(echo "$CONFIG_JSON_STR" | jq -r '.ras_schema.plan_id')
else
    MODELDIR=$1
    MODEL=$2
    PLAN_ID=$3
fi

INDEX_NUM=$(printf "%s" "$PLAN_ID" | sed 's/[^0-9]//g' | sed 's/^0*//')
if [ -z "$INDEX_NUM" ]; then
    INDEX_NUM=0
fi
INDEX_PADDED=$(printf "%02d" "$INDEX_NUM")

RAS_LIB_PATH=/ras/libs:/ras/libs/mkl:/ras/libs/rhel_8
export LD_LIBRARY_PATH=$RAS_LIB_PATH:$LD_LIBRARY_PATH

RAS_EXE_PATH=/ras/bin
export PATH=$RAS_EXE_PATH:$PATH
RAS_EXE_PATH=/ras/bin
export PATH=$RAS_EXE_PATH:$PATH

cd "$MODELDIR"

# set -o pipefail
if RasUnsteady "${MODEL}.p${INDEX_PADDED}.tmp.hdf" "x${INDEX_PADDED}" 2>&1 | tee /dev/stderr | grep -q "Finished Unsteady Flow Simulation"; then
    sleep 2
    mv "${MODEL}.p${INDEX_PADDED}.tmp.hdf" "${MODEL}.p${INDEX_PADDED}.hdf"
    echo "RasUnsteady succeeded — moved to ${MODEL}.p${INDEX_PADDED}.hdf"
    exit 0
else
    echo "Error: RasUnsteady failed." >&2
    exit 2
fi