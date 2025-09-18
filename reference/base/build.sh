IMAGE=ffrd_base
docker build -t $IMAGE .

docker run --rm \
  $IMAGE \
  "$(cat example-config.json)"

# docker run --rm \
#   --env-file .env \
#   --entrypoint download_from_config \
#   $IMAGE \
#   "$(cat example-config.json)"