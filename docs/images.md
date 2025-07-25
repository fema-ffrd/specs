# Base & Plugin Image Specification

This specification defines the behavior, conventions, and schema expectations for **base** and **plugin** container images used in the FFRD pipeline.

---

## 🔧 Base Image

### Overview

The base image provides reusable logic for:

- Downloading files from S3
- Uploading files to S3
- Validating configuration JSON against a schema
- Executing downstream plugins

---

### 🔐 Environment Variables

| Variable       | Description                            |
| -------------- | -------------------------------------- |
| `SRC_<NAME>`   | S3 source URI (e.g. `s3://bucket/key`) |
| `DST_<NAME>`   | Local path the file is downloaded to   |
| `.env.runtime` | File auto-generated for subprocesses   |

These are set automatically after downloads are processed.

---

### 📅 Download Tool

CLI tool: `download`

```bash
download all
download <name> <s3://bucket/key> <destination_path>
```

#### Env-based download:

```env
SRC_LOG=s3://bucket/path/to/log.json
DST_LOG=/tmp/log.json
```

These must be present in the environment to support `download all`.

---

### 📤 Upload Tool

CLI tool: `upload`

```bash
upload <s3://bucket/key> --name <logical_name>
upload <s3://bucket/key> --path <file_path>
```

Validates that the file exists and is accessible.

---

### ⚖️ Entrypoint Behavior

The base image entrypoint (`entrypoint.py`) performs:

- Loads `.env`
- Validates `--config` against JSON schema
- Downloads files
- Writes runtime `.env.runtime` file
- Runs the target program (e.g., `myapp`)

Example:

```bash
docker run my-image \
  --config '{"downloads": [...], "program": "myapp", "files": ["log"]}' \
  myapp log
```

---

## 🔌 Plugin Images

Plugin images build on the base and include a custom binary and optional schema extension.

---

### 📄 JSON Schema Extension

Plugins must extend the base schema with:

```json
{
  "type": "object",
  "required": ["program", "files"],
  "properties": {
    "program": {
      "type": "string",
      "enum": ["myapp"],
      "description": "Program to run"
    },
    "files": {
      "type": "array",
      "items": { "type": "string" },
      "description": "Names of files required"
    }
  }
}
```

---

### ⚙️ Runtime Behavior

The plugin binary (e.g., `myapp`) must:

- Accept file names as arguments:
  ```bash
  myapp log summary
  ```
- Lookup corresponding `DST_<NAME>` env vars
- Read and process the contents of those files

Help usage should be supported:

```bash
myapp --help
```

---

## 📦 Layer Responsibilities

| Layer        | Tool / Component | Purpose                     |
| ------------ | ---------------- | --------------------------- |
| Base Image   | `download`       | File fetch via S3           |
| Base Image   | `upload`         | File write to S3            |
| Base Image   | `entrypoint.py`  | Validation, downloads, exec |
| Plugin Image | `myapp` binary   | Custom logic                |
| Both         | `.env.runtime`   | Exposes env vars to plugin  |

---

## 📊 Example Configuration

```json
{
  "downloads": [
    {
      "name": "trinity_log",
      "source": "s3://bucket/log.json",
      "destination": "/tmp/log.json"
    }
  ],
  "program": "myapp",
  "files": ["trinity_log"]
}
```

---

## 📝 Contributing

All plugin authors should validate their schema against the base using:

```bash
jq -s '.[0] * .[1]' base-schema.json plugin-schema.json > merged.json
```

---

## 🔗 Related

- [`download.py`](../tools/download.py)
- [`entrypoint.py`](../entrypoint.py)
- Base schema: `config-schema.json`

