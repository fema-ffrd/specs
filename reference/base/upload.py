#!/usr/bin/env python3

import os
import sys
import boto3
import botocore
from pathlib import Path

def usage():
    print("Usage:")
    print("  upload <s3://bucket/key> --name <logical_name>")
    print("  upload <s3://bucket/key> --path <file_path>")
    sys.exit(1)

def upload_file(source, s3_uri):
    if not Path(source).is_file():
        print(f"Error: File not found: {source}")
        sys.exit(1)

    if not s3_uri.startswith("s3://"):
        print(f"Error: Invalid S3 URI: {s3_uri}")
        sys.exit(1)

    bucket, key = s3_uri[5:].split('/', 1)
    s3 = boto3.client("s3")

    try:
        s3.upload_file(source, bucket, key)
        print(f"✅ Uploaded {source} → {s3_uri}")
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ Upload failed: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) < 4:
        usage()

    s3_uri = sys.argv[1]
    flag = sys.argv[2]
    value = sys.argv[3]

    if flag == "--name":
        env_key = f"DST_{value.upper()}"
        source = os.environ.get(env_key)
        if not source:
            print(f"Missing environment variable: {env_key}")
            sys.exit(1)
    elif flag == "--path":
        source = value
    else:
        usage()

    upload_file(source, s3_uri)

if __name__ == "__main__":
    main()
