# Stage 1: Build Go binary
FROM golang:1.21 AS builder

WORKDIR /go/src/app

COPY main.go .
COPY schema-extension.json .

RUN go build -o /go/bin/myapp main.go

# Stage 2: Extend base Python image
FROM ffrd_base

# Copy Go binary into final image
COPY --from=builder /go/bin/myapp /usr/local/bin/myapp

# Merge original and new schema into a single schema
COPY --from=builder /go/src/app/schema-extension.json /app/schema-extension.json

# Install jq to allow JSON schema merging
RUN apt-get update && apt-get install -y jq && rm -rf /var/lib/apt/lists/*

# Merge base config-schema.json with the extension
RUN jq -s '.[0] * .[1]' /app/config-schema.json /app/schema-extension.json > /app/config-schema.merged.json \
    && mv /app/config-schema.merged.json /app/config-schema.json \
    && rm /app/schema-extension.json


COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]


