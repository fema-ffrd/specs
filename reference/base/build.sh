IMAGE=ffrd_base
docker build -t $IMAGE .

# Test with validation example
docker run --rm \
  $IMAGE \
  -s "action.json" \
  -i "$(cat example-config.json)"

# docker run --rm \
#   --env-file .env \
#   --entrypoint download_from_config \
#   $IMAGE \
#   "$(cat example-config.json)"