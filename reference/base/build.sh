IMAGE=my-base-image 
docker build -t $IMAGE .

docker run --rm  \
  -v $(pwd)/.env:/app/.env \
  $IMAGE \
  --config '{
    "downloads": [
      {
        "name": "trinity_log",
        "source": "s3://trinity-pilot/logs/uploads/1749572844-qA5QR7gBvY.json",
        "destination": "/tmp/1749572844-qA5QR7gBvY.json"
      }
    ]
  }' download

# docker run --rm  $IMAGE 