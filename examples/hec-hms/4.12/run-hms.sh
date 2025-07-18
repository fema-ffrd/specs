#!/bin/bash

set -e

# Add display settings to ensure Xvfb is running and DISPLAY is set for headless execution
if [ -z "$DISPLAY" ]; then
  Xvfb :99 -screen 0 1024x768x16 &
  export DISPLAY=:99
  echo "Virtual display server started and DISPLAY set to :99"
fi

# run_hms
# Runs the HEC-HMS simulation with the given project directory, project name, and simulation name.
# Arguments:
#   $1 - Project directory (local or URI)
#   $2 - Project name (hms project name)
#   $3 - Simulation name (which hms simulation to run)
# Usage: ./run-hms.sh <PROJECT_DIR> <PROJECT_NAME> <SIM_NAME> (ex: ./run-hms.sh project/salsipuedes-creek Salsipuedes_Creek Feb_2017)
run_hms() {
  local PROJECT_DIR="$1"
  local PROJECT_NAME="$2"
  local SIM_NAME="$3"

  echo "Running HEC-HMS simulation for project: $PROJECT_NAME, simulation name: $SIM_NAME in directory: $PROJECT_DIR"

  # TODO: Decide how to get the data (if local then use bind mount path, if cloud then pull from cloud storage)

  # validate local project directory exists
  if [[ ! -d "$PROJECT_DIR" ]]; then
    echo "Error: Project directory '$PROJECT_DIR' does not exist."
    exit 1
  fi

  TEMPLATE=src/compute.template.script
  SCRIPT=src/compute.script

  # Substitute variables in the template and create a new compute.script used by HMS's hec-hms.sh script
  sed \
    -e "s|\${PROJECT_NAME}|$PROJECT_NAME|g" \
    -e "s|\${PROJECT_DIR}|$PROJECT_DIR|g" \
    -e "s|\${SIM_NAME}|$SIM_NAME|g" \
    "$TEMPLATE" > "$SCRIPT"

  # Run HEC-HMS with the newly generated script
  /HEC-HMS-4.12/hec-hms.sh -s "$SCRIPT"
}

# Check if the correct number of arguments is provided
if [[ $# -ne 3 ]]; then
  echo "Usage: $0 <PROJECT_DIR> <PROJECT_NAME> <SIM_NAME>"
  exit 1
fi

# Call the run_hms function with the provided arguments
run_hms "$1" "$2" "$3"