# validates (using JSON_STRING in entrypoint method), but not yet passing to the go binary to running hms.
docker run -v ${PWD}:/workspace go-hms-runner:4.13-beta.6 /workspace/examples/hms-simulation-payload-FS.json

# what's expected to work (using JSON_PAYLOAD in entrypoint method), but running into line too long error on Windows. (also not yet tested passing to the go binary to running hms).
docker run -v ${PWD}:/workspace go-hms-runner:4.13-beta.6 "$(cat /workspace/examples/hms-simulation-payload-FS.json)"