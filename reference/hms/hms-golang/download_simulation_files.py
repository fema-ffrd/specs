#!/usr/bin/env python3

import json
import os
import sys
import subprocess

DOWNLOAD = "/usr/local/bin/download"
LOCAL_DIR = "/mnt"

def usage():
    print("Usage: download_simulation_files.py '<json_config_string>'")
    sys.exit(1)

def main():
    if len(sys.argv) != 2:
        usage()
    config_str = sys.argv[1]
    try:
        config = json.loads(config_str)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON string.")
        print(f"Reason: {e}")
        sys.exit(1)

    # Find S3 stores
    s3_stores = {s['name']: s for s in config.get('stores', []) if s.get('store_type') == 'S3'}
    if not s3_stores:
        print("No S3 stores found in config.")
        sys.exit(0)

    # Download all S3 input files using subprocess
    for input_item in config.get('inputs', []):
        store_name = input_item.get('store_name')
        store = s3_stores.get(store_name)
        if not store:
            continue
        root = store['params']['root']
        for key, rel_path in input_item.get('paths', {}).items():
            if not rel_path:
                continue
            s3_uri = f"s3://{root}/{rel_path}"
            local_path = os.path.join(LOCAL_DIR, rel_path)
            print(f"➡️  Downloading {input_item['name']}:{key} from {s3_uri} to {local_path}")
            result = subprocess.run([DOWNLOAD, key, s3_uri, local_path], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Download failed for {input_item['name']}:{key}: {s3_uri} → {local_path}")
                print(f"STDERR: {result.stderr.strip()}")
                sys.exit(1)
            else:
                print(f"✅ Downloaded {input_item['name']}:{key}: {s3_uri} → {local_path}")

if __name__ == "__main__":
    main()
