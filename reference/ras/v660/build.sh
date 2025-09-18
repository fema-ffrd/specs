IMAGE=ras
docker build --platform linux/amd64 -t $IMAGE .

docker run --platform linux/amd64  --rm -v ./data:/data $IMAGE "$(cat example-ras-config.json)"
# docker run --platform linux/amd64 --rm -v ./data:/data --entrypoint /bin/bash $IMAGE -c "ls -l /data"