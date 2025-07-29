IMAGE=conformance

docker build -t $IMAGE .

# docker run --rm --env-file .env \
#     $IMAGE "$(cat example-conformance-config.json)"

docker run --rm --env-file .env  $IMAGE "$(cat example-conformance-config.json)"