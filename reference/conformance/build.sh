IMAGE=conformance

docker build -t $IMAGE .

# docker run --rm -v ./data:/data $IMAGE "$(cat example-ras-config.json)"

docker run --rm \
  --env-file .env \
  $IMAGE \
  "$(cat example-ras-config.json)"

# docker run --rm -v ./data:/data $IMAGE "$(cat example-ras-config.json)"
# docker run --rm -v ./data:/data --entrypoint /bin/bash $IMAGE -c "ls -l /data"