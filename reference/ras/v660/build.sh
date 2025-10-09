IMAGE=ras
docker build --platform linux/amd64 -t $IMAGE .

## Uncomment to check (local) data mounting
# docker run --platform linux/amd64 --rm -v ./data:/data --entrypoint /bin/bash $IMAGE -c "ls -l /data"

# Uncomment to run local (store=FS) with no  environment variables (data must be mounted in /data)
docker run --platform linux/amd64 --rm -v ./data:/mnt $IMAGE "$(cat examples/ras-unsteady-payload-FS.json)"

## Uncomment to run with S3 environment variables where 1) data is uploaded to S3 and 2) results are copied locally
# docker run --platform linux/amd64 --rm --env-file .env -v ./data:/mnt  $IMAGE "$(cat examples/ras-unsteady-payload-S3-1.json)"
# docker run --platform linux/amd64 --rm --env-file .env -v ./data:/mnt  $IMAGE "$(cat examples/ras-unsteady-payload-S3-2.json)"