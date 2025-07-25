# 🔌 Plugin Image Specification

This document outlines how to develop a **plugin image** that builds on the FFRD base image. Plugin images are responsible for:

- Providing the main executable (e.g., `myapp`, `hec-ras`, `hms.jar`)
- Accepting command-line arguments to process downloaded files
- Reading env vars (like `DST_<NAME>`) to locate inputs
- Writing outputs and optionally uploading them using the base utilities

---

## 📦 Image Structure

A plugin image typically consists of:

- A compiled binary or script
- An extended schema (`schema-extension.json`)
- A Dockerfile that uses a multi-stage build to copy artifacts into the base image

Example structure:

```bash
my-plugin/
├── Dockerfile
├── schema-extension.json
├── main.go  # or .csproj / Main.java / etc.
```

---

## 🐳 Dockerfile Example

```Dockerfile
FROM golang:1.21 AS build
WORKDIR /app
COPY . .
RUN go build -o myapp main.go

FROM ffrd/base:latest
COPY --from=build /app/myapp /usr/local/bin/myapp
COPY schema-extension.json /app/schema-extension.json
```

---

## 🔧 Runtime Expectations

When your plugin runs, it should:

1. Accept one or more filenames as CLI args
2. Resolve their paths using env vars like `DST_<NAME>`
3. Read from those files
4. Write results to a known location
5. Use the `upload` CLI if needed to persist outputs

---

## 🛠️ Example Plugin Entrypoint (Python)

```python
import os, sys

for name in sys.argv[1:]:
    path = os.environ.get(f"DST_{name.upper()}")
    if not path:
        print(f"Missing env var: DST_{name.upper()}", file=sys.stderr)
        sys.exit(1)

    with open(path) as f:
        print(f.read())
```

---

## ✅ Validation

Your plugin must define `schema-extension.json` and include:

```json
{
  "type": "object",
  "properties": {
    "program": { "type": "string", "enum": ["myapp"] },
    "files": {
      "type": "array",
      "items": { "type": "string" },
      "description": "List of required file names"
    }
  },
  "required": ["program", "files"]
}
```

---

## 🚀 Execution Flow

```bash
docker run my-plugin \
  --config '{
    "program": "myapp",
    "downloads": [...],
    "files": ["input1"]
  }' \
  myapp input1
```

The base image downloads files, sets `DST_INPUT1=/tmp/...`, and your app reads that file.

---

Next: [Examples](plugin.md)

Back to: [Base Image Specification](base.md)

