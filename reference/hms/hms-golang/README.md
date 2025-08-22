# Golang + Logging HEC-HMS Example

A HEC-HMS runner image built with Go, with logging.

## Build

To build the image:

```
docker build -t go-hms-runner .
```

To build with a specific version of HMS, use the `HMS_VERSION` build argument.

```
docker build -t go-hms-runner:4.11 --build-arg HMS_VERSION=4.11 .
```

## Run

See the CLI help:

```
docker run go-hms-runner --help
```

To run the included Tenk example model:

```
docker run go-hms-runner --example
```

or, alternatively:

```
docker run go-hms-runner --project-file /opt/HEC-HMS-4.12/samples/tenk/tenk.hms --sim-name "Jan 96 storm"
```

Run the Tenk example by mounting a volume:

```
docker run -v /mnt/c/temp/hms-samples/:/tmp/samples go-hms-runner --project-file /tmp/samples/tenk/tenk.hms --sim-name "Jan 96 storm"
```

To run the Tenk example with a JSON file, first create a JSON file based on the HMS schema:

```json
{
    "hms_schema": {
        "project_file": "/opt/HEC-HMS-4.12/samples/tenk/tenk.hms",
        "sim_name": "Jan 96 storm"
    }
}
```

Then, to use the JSON file to configure the input parameters:

```
docker run -v .:/tmp go-hms-runner --json-file /tmp/tenk.json
```

Use the `--log-format` flag to output logs as JSON:

```
docker run go-hms-runner --project-file /opt/HEC-HMS-4.12/samples/tenk/tenk.hms --sim-name "Jan 96 storm" --log-format json
```
