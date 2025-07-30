HEC-HMS 4.12 Container Specification
========================

# Introduction
A containerized runner for HEC-HMS version 4.12 (linux) intended to run a single simulation.

# Build Instructions
A handful of files are expected to be present when building the container:

├── Dockerfile_4_12                 
├── hms_cli.py                      

To build and test the container (using the tenk example project):
```
docker build -f Dockerfile_4_12 -t hec-hms-4-12-runner .
docker run --rm -it hec-hms-4-12-runner --example tenk
```

# Usage
This container is intended to run a linux version of hec-hms using local project files accessed through a bind-mount. Specifically, the [Jython API](https://www.hec.usace.army.mil/software/hec-hms/javadoc/hms/model/JythonHms.html) is used anto call the Java application through a python cli script
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

```
docker run -v "<LOCAL_DIR>:<MNT_DIR>" <IMAGE> --project-dir <MNT_DIR> --project-name <PROJECT_NAME> --sim-name <SIM_NAME>

example 1:
docker run -v "C:\project\Salsipuedes_Creek:/project/Salsipuedes_Creek" hec-hms-4-12-runner \
  --project-dir /project/Salsipuedes_Creek --project-name Salsipuedes_Creek --sim-name Feb_2017

example 2:
docker run -v "C:\project\river_bend:/project/river_bend" hec-hms-4-12-runner --project-dir /project/river_bend --project-name river_bend --sim-name "Minimum Facility"
```

## Running the container in interactive mode (with the tenk example project):
```
docker run -it --entrypoint bash hec-hms-4-12-runner  
python3 hms_cli.py --example tenk
```

# Inputs/Outputs/Logs
## Inputs:
- LOCAL_DIR (string): The local directory storing the hec-hms project files to be run
- PROJECT_NAME (string): The project name taken from the .hms file (ex: tenk.hms -> "tenk")
- SIM-NAME (string): The simulation name to run (found in .run file)

## Outputs:
These are written to the bind mount with run in batch mode:  
- `<SIM-NAME>.dss`: The results in a DSS data store
- `RUN_<SIM-NAME>.results`: XML version of results 
- `<SIM-NAME>.log`: Standard HEC-HMS log file for a simulation run
- TODO: validate these and there are likely others.

## Logs:
- TODO (no logging currently setup beyond standard hec-hms outputs)



