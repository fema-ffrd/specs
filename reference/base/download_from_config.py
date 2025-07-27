#!/usr/bin/env python3

import json
import subprocess
import sys


def usage():
    print("Usage:")
    print("  download-from-config '<json_config_string>'")
    sys.exit(1)


def load_json_string(json_str):
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON string.")
        print(f"Reason: {e}")
        sys.exit(1)


def validate_with_subprocess(config_str):
    result = subprocess.run(["/usr/local/bin/validate", config_str], capture_output=True, text=True)

    print(result.stdout)
    if result.returncode != 0:
        print("❌ Config validation failed. Aborting download.")
        print(result.stderr.strip())
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
    if len(sys.argv) != 2:
        usage()

    config_str = sys.argv[1]
    config = load_json_string(config_str)

    # ✅ Validate using the already-installed script
    validate_with_subprocess(config_str)

    # Try top-level first, then one level down
    base_schema = config.get("base_schema")
    if not base_schema:
        # Check one level down
        for v in config.values():
            if isinstance(v, dict) and "base_schema" in v:
                base_schema = v["base_schema"]
                break

    downloads = base_schema.get("s3Downloads", []) if base_schema else []
    if not downloads:
        print("⚠️ No downloads found in config.")
        sys.exit(0)

    items = [{"name": d["name"], "source": d["s3Uri"], "destination": d["destinationPath"]} for d in downloads]

    download_files(items)


if __name__ == "__main__":
    main()
