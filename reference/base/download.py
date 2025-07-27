#!/usr/bin/env python3

import os
import re
import subprocess
import sys

import boto3
import botocore

import subprocess
import sys



def usage():
    print("Usage:")
    print("  download <name> <s3://bucket/key> <destination_path>")
    sys.exit(1)


def download_s3(source, destination, name=None):
    if not source.startswith("s3://"):
        print(f"Error: S3 URI must start with s3:// — got {source}")
        sys.exit(1)

    parts = source[5:].split("/", 1)
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
            print(f"✅ Downloaded {name}: {source} → {destination}")
        else:
            print(f"✅ Downloaded {source} → {destination}")
    except botocore.exceptions.BotoCoreError as e:
        print(f"❌ Download failed: {source} → {destination}")
        print(f"Reason: {str(e)}")
        sys.exit(1)




def download_files(downloads):
    for item in downloads:
        source = item["source"]
        destination = item["destination"]
        name = item.get("name")
        if not name:
            print(f"❌ Missing 'name' field in download item: {item}")
            sys.exit(1)

        print(f"➡️  Downloading {name} from {source} to {destination}")
        result = subprocess.run(["/usr/local/bin/download", name, source, destination], capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ Download failed for {name}: {source} → {destination}")
            print(f"STDERR: {result.stderr.strip()}")
            sys.exit(1)
        else:
            print(f"✅ Downloaded {name}: {source} → {destination}")


def main():
    if len(sys.argv) == 4:
        name = sys.argv[1]
        source = sys.argv[2]
        destination = sys.argv[3]
        download_s3(source, destination, name)
        sys.exit(0)

    usage()


if __name__ == "__main__":
    main()
