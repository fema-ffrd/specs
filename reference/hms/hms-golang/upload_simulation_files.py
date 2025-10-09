#!/usr/bin/env python3

import json
import os
import sys
import subprocess

UPLOAD = "/usr/local/bin/upload"
LOCAL_DIR = "/mnt"

def usage():
    print("Usage: upload_simulation_files.py '<json_config_string>'")
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

    # Upload all S3 output files using subprocess
    for output_item in config.get('outputs', []):
        store_name = output_item.get('store_name')
        store = s3_stores.get(store_name)
        if not store:
            continue
        root = store['params']['root']
        for key, rel_path in output_item.get('paths', {}).items():
            if not rel_path:
                continue
            s3_uri = f"s3://{root}/{rel_path}"
            local_path = os.path.join(LOCAL_DIR, rel_path)
            print(f"⬆️  Uploading {output_item['name']}:{key} from {local_path} to {s3_uri}")
            result = subprocess.run([UPLOAD, s3_uri, '--path', local_path], capture_output=True, text=True)
            if result.returncode != 0:
                print(f"❌ Upload failed for {output_item['name']}:{key}: {local_path} → {s3_uri}")
                print(f"STDERR: {result.stderr.strip()}")
                sys.exit(1)
            else:
                print(f"✅ Uploaded {output_item['name']}:{key}: {local_path} → {s3_uri}")

if __name__ == "__main__":
    main()
