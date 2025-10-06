# You'll need the trinity caliabration HMS model for testing a valid hms project from the USACE Model Library
# aws s3 sync s3://ffrd-trinity/calibration/hydrology/trinity ffrd-trinity

# build the base image first (see reference/base)

# build the docker image
docker build --build-arg HMS_VERSION=4.13-beta.6 -t go-hms-runner:4.13-beta.6 .

# uncomment to run local (store=FS) with no environment variables. Assumes local ffrd-trinity folder (must be to target location /mnt)
# docker run -v ${PWD}/ffrd-trinity:/mnt go-hms-runner:4.13-beta.6 "$(cat examples/hms-simulation-payload-FS.json)"

# uncomment to run with S3 environment variables where 1) data is uploaded to S3 and 2) results are exported to S3
# docker run --env-file .env -v ${PWD}/ffrd-trinity:/mnt go-hms-runner:4.13-beta.6 "$(cat examples/hms-simulation-payload-S3-1.json)"


