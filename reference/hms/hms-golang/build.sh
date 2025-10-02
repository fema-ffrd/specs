# You'll need the trinity caliabration HMS model for testing a valid hms project from the USACE Model Library
# aws s3 sync s3://ffrd-trinity/calibration/hydrology/trinity ffrd-trinity

# build the docker image
docker build -t go-hms-runner:4.13-beta.6 .

# with a mount to ffrd-trinity folder (calibration demo, which is runnable with the data)
docker run -v ${PWD}/ffrd-trinity:/ffrd-trinity go-hms-runner:4.13-beta.6 "$(cat examples/hms-simulation-payload-FS.json)"