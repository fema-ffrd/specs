# ---------------------------------------------------------------------
# 1) BUILD STAGE  – compile static Linux binary
# ---------------------------------------------------------------------
FROM golang:1.24-alpine AS builder

WORKDIR /src
ENV CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN go build -o /hms-runner main.go

# ---------------------------------------------------------------------
# 2) RUNTIME STAGE – minimal image with HMS + busybox + wrapper
# ---------------------------------------------------------------------
FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y \
       wget unzip libxrender1 libxtst6 libxi6 libfreetype6 libgfortran5 libfontconfig1 \
    && rm -rf /var/lib/apt/lists/*

# HMS distribution (must already be extracted in build context)
# Download and extract HEC-HMS
ARG HEC_HMS_VERSION="4.12"
ARG HEC_HMS_DOWNLOAD_URL="https://www.hec.usace.army.mil/nexus/repository/maven-public/mil/army/usace/hec/hec-hms/${HEC_HMS_VERSION}-linux64/hec-hms-${HEC_HMS_VERSION}-linux64.tar.gz"
RUN wget "${HEC_HMS_DOWNLOAD_URL}" -O hec-hms.tar.gz \
    && tar -xvzf hec-hms.tar.gz -C /opt \
    && rm hec-hms.tar.gz

# Runner binary
COPY --from=builder /hms-runner /usr/local/bin/hms-runner

# Environment expected by the wrapper / HMS
ENV HMS_HOME="/opt/HEC-HMS-${HEC_HMS_VERSION}" \
    PATH=/usr/local/bin:/usr/bin:/bin

# Optional: non-root execution
USER 1000:1000
WORKDIR /workspace

ENTRYPOINT ["hms-runner"]
