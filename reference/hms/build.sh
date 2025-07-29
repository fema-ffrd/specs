IMAGE=hms-ffrd

docker build -t $IMAGE .

docker run --rm $IMAGE ./run_hms.sh "$(cat example-hms-config.json)"
docker run --rm -it --entrypoint /bin/bash $IMAGE
