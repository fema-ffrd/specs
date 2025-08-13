# Golang + Logging HEC-HMS Example

A HEC-HMS runner image built with Go, with full logging.

## Build

To build the image:

```
docker build -t go-hms-runner .
```

## Run

See the CLI help:

```
docker run go-hms-runner --help
```

Run the Tenk example by mounting a volume:

```
docker run -v /mnt/c/temp/hms-samples/:/tmp/samples go-hms-runner --project-file /tmp/samples/tenk/tenk.hms --sim-name "Jan 96 storm"
```

Use the `--log-format` flag to output logs as JSON:

```
docker run -v /mnt/c/temp/hms-samples/:/tmp/samples go-hms-runner --project-file /tmp/samples/tenk/tenk.hms --sim-name "Jan 96 storm" --log-format json
```
