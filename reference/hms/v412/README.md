# HEC-HMS 4.12 Container Specification

# Introduction

A containerized runner for HEC-HMS version 4.12 (linux) intended to run a single simulation.

# Build Instructions

A handful of files are expected to be present when building the container:

├── Dockerfile_4_12\
├── hms_cli.py

To build and test the container (using the tenk example project):

```
docker build -f Dockerfile_4_12 -t hec-hms-4-12-runner .
docker run --rm -it hec-hms-4-12-runner --example tenk
```

# Usage

This container is intended to run a linux version of hec-hms using local project files accessed through a bind-mount. Specifically, the [Jython API](https://www.hec.usace.army.mil/software/hec-hms/javadoc/hms/model/JythonHms.html) is used to call the Java application through a python cli script:

- hms_cli.py
  - setup an integration test using the default tenk project
  - Update a template Jython script with user-defined parameters and store in memory
  - Call the Java module hms.Hms using script flag (-s) and Jython script path

Note: the control script (control.script) used for parameterizing the hec-ras run uses this template:

```
from hms.model.JythonHms import *
OpenProject("${PROJECT_NAME}", "${PROJECT_DIR}")
ComputeRun("${SIM_NAME}")
SaveAllProjectComponents()
```

## Running the container in batch mode:

Use a bind mount to reference local data from within the container. MNT_DIR should generally match the LOCAL_DIR name.

You must specify exactly one input method:

- `--project_file <project_file_PATH> --sim_name <SIM_NAME>`
- `--json_file <JSON_FILE_PATH>` (see schema below)
- `--example tenk`

```
# Direct CLI arguments
docker run -v "<LOCAL_DIR>:<MNT_DIR>" <IMAGE> --project_file <project_file_PATH> --sim_name <SIM_NAME>

example 1 (project_file and sim_name):
docker run -v "C:\project\Salsipuedes_Creek:/project/Salsipuedes_Creek" hec-hms-4-12-runner \
  --project_file /project/Salsipuedes_Creek/Salsipuedes_Creek.hms --sim_name Feb_2017

example 2 (json):
docker run -v "<LOCAL_DIR>:<MNT_DIR>" <IMAGE> --json_file <JSON_FILE_PATH>

example 3 (tenk example):
docker run hec-hms-4-12-runner --example tenk
```

## Running the container in interactive mode (with the tenk example project):

```
docker run -it --entrypoint bash hec-hms-4-12-runner  
python3 hms_cli.py --example tenk
```

# Inputs/Outputs/Logs

## Inputs:

- project_file (string): Path to the .hms project file (e.g., /project/tenk/tenk.hms) (if using CLI args or JSON)
- sim_name (string): The simulation name to run (found in .run file) (if using CLI args or JSON)
- json_file (string): Path to a JSON file with the following schema:
  ```json
  {
    "hms_schema": {
      "project_file": "/data/samples/tenk/tenk.hms",
      "sim_name": "Jan 96 storm"
    }
  }
  ```
- example (string): one of [tenk]

## Outputs:

These are written to the bind mount when run in batch mode:

- `<SIM-NAME>.dss`: The results in a DSS data store
- `RUN_<SIM-NAME>.results`: XML version of results
- `<SIM-NAME>.log`: Standard HEC-HMS log file for a simulation run
- TODO: confirm all hec-hms outputs.

## Logs:

- TODO (no logging currently setup beyond standard hec-hms outputs)
