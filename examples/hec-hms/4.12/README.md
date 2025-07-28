HEC-HMS 4.12 Container Specification
========================

# Introduction
A containerized runner for HEC-HMS version 4.12 (linux) intended to run a single simulation.

# Build Instructions
A handful of files are expected to be present when building the container:

├── Dockerfile_4_12                 
├── run-hms.sh                      
├── src/  
│   └── compute.template.script    

To build and test the container:
```
docker build -f Dockerfile_4_12 -t hec-hms-4-12-runner .
docker run -it --entrypoint bash hec-hms-4-12-runner

java -version
gradle -v
ls /HEC-HMS-4.12
```

# Usage
This container is intended to run a linux version of hec-hms using local project files accessed through a bind-mount. Specifically, the [Jython API](https://www.hec.usace.army.mil/software/hec-hms/javadoc/hms/model/JythonHms.html) is used anto call the Java application through a series of bash scripts and a jython compute script:
- run-hms.sh
    - Update a template Jython script with user-defined parameters.
    - Call hec-hms.sh (shipped as a part of HEC-HMS) with the new Jython script
        - Call the Java module hms.Hms using script flag (-s) and Jython script path

Note: the control script (control.script) used for parameterizing the hec-ras run uses this template:
```
from hms.model.JythonHms import *
OpenProject("${PROJECT_NAME}", "${PROJECT_DIR}")
Compute("${SIM_NAME}")
```

## Running the container in batch mode:
Use a bind mount to reference local data from within the container. MNT_DIR should generally match the LOCAL_DIR name.

```
docker run -v "<LOCAL_DIR>:<MNT_DIR>" <IMAGE> <MNT_DIR> <PROJECT_NAME> <SIM_NAME>  

example 1:
docker run -v "C:\project\Salsipuedes_Creek:/project/Salsipuedes_Creek" hec-hms-4-12-runner /project/Salsipuedes_Creek Salsipuedes_Creek Feb_2017

example 2:
docker run -v "C:\project\tenk:/project/tenk" hec-hms-4-12-runner /project/tenk tenk "Jan 96 storm"
```

## Running the container in interactive mode:
```
docker run -it --entrypoint bash hec-hms-4-12-runner  

./run-hms.sh /project/tenk tenk "Jan 96 storm" (TODO: this won't work until we decide on including an hec-hms sample project or unpacking the existing samples.zip shipped with hec-hms)

```

# Inputs/Outputs/Logs
## Inputs:
- LOCAL_DIR (string): The local directory storing the hec-hms project files to be run
- PROJECT_NAME (string): The project name taken from the .hms file (ex: tenk.hms -> "tenk")
- SIM-NAME (string): The simulation name to run (found in .run file)

## Outputs:
- TODO (these currently aren't writing to the volume mount):
- `<SIM-NAME>.dss`: The results in a DSS data store
- `RUN_<SIM-NAME>.results`: XML version of results 
- `<SIM-NAME>.log`: Standard HEC-HMS log file for a simulation run

## Logs:
- TODO (no logging currently setup beyond standard hec-hms outputs)



