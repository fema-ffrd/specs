#!/usr/bin/env python3

import sys
import os
import boto3
import botocore
import re


def usage():
    print("Usage:")
    print("  download all  # uses SRC_<NAME> and DST_<NAME> env vars")
    print("  download <name> <s3://bucket/key> <destination_path>")
    sys.exit(1)


def download_one(source, destination, name=None):
    if not source.startswith("s3://"):
        print(f"Error: S3 URI must start with s3:// — got {source}")
        sys.exit(1)

    parts = source[5:].split('/', 1)
    if len(parts) != 2:
        print(f"Error: Invalid S3 URI format: {source}")
        sys.exit(1)

    bucket, key = parts
    s3 = boto3.client("s3")

    try:
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        s3.download_file(bucket, key, destination)
        sys.stdout.flush()
        if name:
            print(f"Downloaded {name}: {source} → {destination}")
        else:
            print(f"Downloaded {source} → {destination}")
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ Download failed: {source} → {destination}")
        print(f"Reason: {str(e)}")
        sys.exit(1)


def download_all_from_env():
    pattern = re.compile(r'^SRC_(.+)$')
    files = {}

    for key, source in os.environ.items():
        match = pattern.match(key)
        if match:
            name = match.group(1)
            dest_key = f"DST_{name}"
            destination = os.environ.get(dest_key)
            if not destination:
                print(f"Missing {dest_key} for download name: {name}")
                sys.exit(1)
            files[name] = (source, destination)

    if not files:
        print("No SRC_* environment variables found.")
        sys.exit(1)

    for name, (source, destination) in sorted(files.items()):
        print(f"Downloading {name}: {source} → {destination}")
        download_one(source, destination, name)


def main():
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] == "all"):
        download_all_from_env()
        return

    if len(sys.argv) == 4:
        name = sys.argv[1]
        source = sys.argv[2]
        destination = sys.argv[3]
        download_one(source, destination, name)
        return

    usage()


if __name__ == "__main__":
    main()
