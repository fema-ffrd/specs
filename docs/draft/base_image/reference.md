## 📚 Reference

This reference implementation is provided as a Docker container. It includes Python scripts for validating configuration files and performing S3 uploads/downloads.

### Container Details

- **Base Image**: `python:3.11-slim`
- **Installed Packages**: `boto3`, `python-dotenv`, `jsonschema`, `referencing>=0.30.0`, `jq`
- **Scripts**:
  - `/usr/local/bin/validate`: Validates configuration files against a schema.
  - `/usr/local/bin/upload`: Uploads files to S3.
  - `/usr/local/bin/download`: Downloads files from S3.
  - `/usr/local/bin/download_from_config`: Downloads files as specified in a config.

### Usage

#### Validate a Configuration File

```bash
docker run --rm -v $(pwd):/data specs-reference-base /usr/local/bin/validate /data/config.json /schemas/base_schema.json
```

#### Upload a File to S3

```bash
docker run --rm specs-reference-base /usr/local/bin/upload s3://bucket/key /data/file.txt
```

#### Download a File from S3

```bash
docker run --rm specs-reference-base /usr/local/bin/download s3://bucket/key /data/file.txt
```

### Entrypoint

The default entrypoint is the validation script:

```dockerfile
ENTRYPOINT ["/usr/local/bin/validate"]
```

## Source Files

- `Dockerfile`
- `validate.py`
- `upload.py`
- `download.py`
- `download_from_config.py`
- `base_schema.json`

See the Dockerfile for installation and setup details.
