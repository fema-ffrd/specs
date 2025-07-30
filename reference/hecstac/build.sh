IMAGE=hecstac

docker build . -t $IMAGE

# docker run --rm $IMAGE
EXAMPLE_MODEL=/data/Muncie.prj
EXAMPLE_ITEM_ID=Muncie
EXAMPLE_CRS="$(cat data/projection.prj)"

docker run --rm -v ./data:/data $IMAGE $EXAMPLE_MODEL $EXAMPLE_ITEM_ID  "$EXAMPLE_CRS"
# docker run --rm -v ./data:/data --entrypoint /bin/bash $IMAGE -c "ls -l /data"