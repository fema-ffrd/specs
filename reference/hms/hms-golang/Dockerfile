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
# TODO: encountering DSS errors when attempting to run v4.13 image
ARG HMS_VERSION="4.12"
ARG HMS_HOME="/opt/HEC-HMS-${HMS_VERSION}"
RUN if [ "$HMS_VERSION" = "4.13" ]; then \
        # HEC-HMS 4.13 download URL is slightly different
        HMS_DOWNLOAD_URL="https://www.hec.usace.army.mil/nexus/repository/maven-public/mil/army/usace/hec/hec-hms/${HMS_VERSION}-linux64/hec-hms-${HMS_VERSION}-linux64-linux64.tar.gz"; \
    else \
        HMS_DOWNLOAD_URL="https://www.hec.usace.army.mil/nexus/repository/maven-public/mil/army/usace/hec/hec-hms/${HMS_VERSION}-linux64/hec-hms-${HMS_VERSION}-linux64.tar.gz"; \
    fi \
    # Download & extract HMS
    && wget "${HMS_DOWNLOAD_URL}" -O hec-hms.tar.gz \
    && tar -xvzf hec-hms.tar.gz -C /opt \
    && rm hec-hms.tar.gz \
    # Ensure that Java is executable
    && chmod +x ${HMS_HOME}/jre/bin/java \
    # Extract samples
    && mkdir -p ${HMS_HOME}/samples \
    && unzip ${HMS_HOME}/samples.zip -d /tmp/samples \
    && TMP_SAMPLES=$(dirname $(find /tmp/samples -name tenk)) \
    && cp -r $TMP_SAMPLES/* ${HMS_HOME}/samples/ \
    && chmod -R 777 ${HMS_HOME}/samples/ \
    && rm -rf /tmp/samples

# Runner binary
COPY --from=builder /hms-runner /usr/local/bin/hms-runner

# Environment expected by the wrapper / HMS
ENV HMS_HOME="${HMS_HOME}" \
    PATH=/usr/local/bin:/usr/bin:/bin

# Optional: non-root execution
USER 1000:1000
WORKDIR /workspace

ENTRYPOINT ["hms-runner"]
