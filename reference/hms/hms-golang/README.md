# Golang + Logging HEC-HMS Example

A HEC-HMS runner image built with Go, with logging.

## Build

To build the image:

```
docker build -t hms-runner .
```

To build with a specific version of HMS, use the `HMS_VERSION` build argument.

```
docker build -t hms-runner:4.11 --build-arg HMS_VERSION=4.11 .
```

## Run

See the CLI help:

```
docker run hms-runner --help
```

### Running the Tenk Example

To run the included Tenk example model:

```
docker run hms-runner --example
```

or, alternatively:

```
docker run hms-runner --project-file /opt/HEC-HMS-4.12/samples/tenk/tenk.hms --sim-name "Jan 96 storm"
```

Run the Tenk example by mounting a volume:

```
docker run -v /mnt/c/temp/hms-samples/:/tmp/samples hms-runner --project-file /tmp/samples/tenk/tenk.hms --sim-name "Jan 96 storm"
```

To run the Tenk example with a JSON file, first create a JSON file based on the HMS schema:

```json
{
    "project_file": "/opt/HEC-HMS-4.12/samples/tenk/tenk.hms",
    "sim_name": "Jan 96 storm"
}
```

Then, to use the JSON file to configure the input parameters:

```
docker run -v .:/tmp hms-runner --json-file /tmp/tenk.json
```

Use the `--log-format` flag to output logs as JSON:

```
docker run hms-runner --project-file /opt/HEC-HMS-4.12/samples/tenk/tenk.hms --sim-name "Jan 96 storm" --log-format json
```

### Run and Export Spatial Excess Precipitation

To run a model with spatially distributed precipitation and then export excess preciptation grids in HEC-RAS HDF format (`.p##.tmp.hdf`) or `.dss` format:

```
$ docker run -it -v /tmp/trinity:/workspace/trinity hms-runner --project-file /workspace/trinity/trinity.hms --sim-name apr-may-1990 --excess-precip /workspace/trinity/excess-precip.p01.tmp.hdf
```

Or, via JSON input:

```json
{
  "project_file": "/workspace/trinity/trinity.hms",
  "sim_name": "apr-may-1990",
  "excess_precip": "/workspace/trinity/excess-precip_apr-may-1990.p01.tmp.hdf"
}
```

```
$ $ docker run -it -v /tmp/trinity:/workspace/trinity go-hms-runner --json-file /workspace/trinity/test-trinity.json
```
