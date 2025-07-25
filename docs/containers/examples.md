# 🧱 Building Plugins with the Base Image

The FFRD container model enables flexible plugin development using a shared **base image**. This base image provides core utilities like:

- JSON configuration validation
- File download/upload via S3
- Environment variable injection

You can use **any language or framework** in your plugin, provided it builds on the base image via [multi-stage Docker builds](https://docs.docker.com/build/building/multi-stage/).

---

## ✅ Requirements

Your plugin container must:

- Accept a `--config` JSON input
- Use the base image to download inputs and set runtime environment variables
- Accept a list of required file names as arguments
- Read env vars like `DST_<NAME>` to locate input files

---

## 🛠️ Example: HEC-RAS in .NET

**Directory structure:**

```bash
my-hec-ras-plugin/
├── main.csproj
├── Program.cs
├── plugin-schema.json
├── Dockerfile
```

**Dockerfile:**

```Dockerfile
FROM mcr.microsoft.com/dotnet/sdk:6.0 AS build
WORKDIR /app
COPY . .
RUN dotnet publish -c Release -o out

FROM ffrd/base:latest
COPY --from=build /app/out /usr/local/bin/
COPY plugin-schema.json /app/new-schema.json
```

**Command:**

```bash
docker run my-hec-ras-plugin \
  --config '{
    "program": "hec-ras",
    "downloads": [...],
    "files": ["flow_file"]
  }' \
  hec-ras flow_file
```

---

## ☕ Example: Java + HEC-HMS with Upload

```Dockerfile
FROM eclipse-temurin:17 AS build
WORKDIR /src
COPY . .
RUN ./gradlew build

FROM ffrd/base:latest
COPY --from=build /src/build/libs/hms.jar /usr/local/bin/hms.jar
COPY plugin-schema.json /app/new-schema.json
```

**Entrypoint:**

```bash
java -jar /usr/local/bin/hms.jar results rainfall

# Use `upload` to persist output:
upload s3://bucket/sim/output.tif --path /tmp/results.tif
```

---

## 💡 Note

- Add `--help` to your CLI apps for better developer experience
- Use `jq` to merge your plugin schema with the base:

```bash
jq -s '.[0] * .[1]' base-schema.json plugin-schema.json > config-schema.json
```

