#!/usr/bin/sh

# usage: ./run.sh '{"model_directory":"/sim/sample-model/","model_name":"Muncie"}'
if [ $# -eq 1 ]; then
    CONFIG_JSON_STR="$1"
    MODELDIR=$(echo "$CONFIG_JSON_STR" | jq -r '.ras_schema.model_directory')
    MODEL=$(echo "$CONFIG_JSON_STR" | jq -r '.ras_schema.model_name')
else
    MODELDIR=$1
    MODEL=$2
fi

RAS_LIB_PATH=/ras/libs:/ras/libs/mkl:/ras/libs/rhel_8
export LD_LIBRARY_PATH=$RAS_LIB_PATH:$LD_LIBRARY_PATH

RAS_EXE_PATH=/ras/v61
export PATH=$RAS_EXE_PATH:$PATH

echo $MODELDIR

cd $MODELDIR
RasUnsteady $MODEL.c04 b04