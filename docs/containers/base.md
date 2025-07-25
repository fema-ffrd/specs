# 🔧 Base Image Specification

The **FFRD Base Image** is a **specification**, not just an implementation. It defines a set of features, interfaces, and conventions that enable consistent, schema-driven containerized workflows.

This spec **can be implemented using any language, runtime, or base container**, as long as it:

- Includes a help menu by default with usage information
- Validates configuration against JSON Schema
- Exposes configuration vars as env vars
- Supports downloading files from S3 using env var names or path
- Supports uploading outputs to S3 using env var names or path

---

## 🧹 Required Features

### ✅ JSON Schema Validation

The base image must validate the `--config` JSON using a [JSON Schema Draft 7](https://json-schema.org/draft-07/schema) file (`config-schema.json`).

Developers can extend the schema by providing a `new-schema.json` file, which should be merged at image build time (e.g., using `jq -s '.[0] * .[1]'`).

---

### 📅 File Downloads

Your implementation must support a `download` command with two modes:

```bash
download all
# or
download <name> <s3://bucket/key> <destination>
```

These commands should rely on environment variables with the following format:

```env
SRC_<NAME>=s3://bucket/key
DST_<NAME>=/tmp/file.ext
```

Calling `download all` should read these env vars and download files accordingly.

---

### 📄 File Uploads

Your base image must provide an `upload` command with this interface:

```bash
upload <s3://bucket/key> --name result_file.ext
upload <s3://bucket/key> --path /tmp/results/output.tif
```

It should upload the named file or the file at the specified path to S3.

---

### 🌱 Runtime Environment

After downloads are complete, your base image must write a file `.env.runtime` with lines like:

```env
SRC_<NAME>=s3://bucket/key
DST_<NAME>=/tmp/file.ext
```

The image's entrypoint should `source` this file before executing the plugin command.

---

## 🚦 Entrypoint Specification

The image must include a shell entrypoint (e.g., `entrypoint.sh`) that performs the following:

1. Loads `/app/.env` if present
2. Invokes a script (e.g., `entrypoint.py`) to:
   - Validate `--config`
   - Perform downloads
   - Export runtime env vars to `.env.runtime`
3. Sources `.env.runtime`
4. Runs the user-specified program and arguments

This guarantees a clean, consistent handoff to the plugin layer.

---

## 🧪 Example Execution

```bash
docker run my-plugin \
  --config '{
    "downloads": [
      {"name": "log", "source": "s3://bucket/log.json", "destination": "/tmp/log.json"}
    ],
    "program": "myapp",
    "files": ["log"]
  }' \
  myapp log
```

Your plugin will find `DST_LOG=/tmp/log.json` already set.

---

## 🛠️ Alternative Implementations

While an official implementation is provided using Python, developers may reimplement the spec using any language or framework that
can be containerized to support the base image specification. What matters is **conformance to the interface and behavior**, not the underlying tech stack.

---

Next: [Plugin Image Specification](plugin.md)

