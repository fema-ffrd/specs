# 📝 Base Image

## Overview
This specification describes the requirements for a containerized tool that validates configuration files against a JSON schema and supports uploading/downloading files to/from Amazon S3.

## Requirements

### 1. Schema Validation
- Accept a configuration file and a JSON schema as input.
- Validate the configuration file using the provided schema.
- Output validation results (success/failure and errors).

### 2. S3 File Operations
- **Download**: Retrieve files from a specified S3 bucket/key to a local path.
- **Upload**: Send local files to a specified S3 bucket/key.
- Use AWS credentials from environment variables or configuration files.

### 3. Containerization
- Base image: `python:3.11-slim`
- Include Python scripts for validation, upload, and download.
- Expose scripts as executable commands in the container.

### 4. Usage
- Entrypoint: Validation script (`validate.py`)
- Additional commands: `download.py`, `upload.py`, `download_from_config.py`

### 5. Dependencies
- Python packages: `boto3`, `python-dotenv`, `jsonschema`, `referencing>=0.30.0`
- System package: `jq`

## Example Commands
```bash
docker run --rm -v $(pwd):/data validate /data/config.json /schemas/base_schema.json
docker run --rm upload s3://bucket/key /data/file.txt
docker run --rm download s3://bucket/key /data/file.txt
```