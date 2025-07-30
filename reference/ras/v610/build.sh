IMAGE=ffrd_child
docker build -t $IMAGE .

# docker run --rm $IMAGE

docker run --rm -v ./data:/data $IMAGE "$(cat example-ras-config.json)"
# docker run --rm -v ./data:/data --entrypoint /bin/bash $IMAGE -c "ls -l /data"