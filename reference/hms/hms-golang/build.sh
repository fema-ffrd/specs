# build the docker image
docker build -t go-hms-runner:4.13-beta.6 .

# passing json template (as string) which will be validate and resolved in entrypoint.sh
# docker run -v ${PWD}:/workspace go-hms-runner:4.13-beta.6 "$(cat examples/hms-simulation-payload-FS.json)"