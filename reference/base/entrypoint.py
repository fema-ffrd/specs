#!/usr/bin/env python3

import os
import sys
import json
import argparse
import subprocess
import shutil
from jsonschema import validate, ValidationError
from dotenv import load_dotenv, find_dotenv

SCHEMA_PATH = "/app/config-schema.json"
RUNTIME_ENV_PATH = "/tmp/.env.runtime"

def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', required=True, help='JSON config string')
    parser.add_argument('cmd', nargs=argparse.REMAINDER, help='Command to run')
    return parser.parse_args()

def write_runtime_env_var(key, value):
    with open(RUNTIME_ENV_PATH, "a") as f:
        f.write(f'export {key}="{value}"\n')
    print(f"New env var {key}={value}")

def download_files(downloads):
    # Clear previous runtime env file
    if os.path.exists(RUNTIME_ENV_PATH):
        os.remove(RUNTIME_ENV_PATH)

    for item in downloads:
        source = item['source']
        destination = item['destination']
        name = item.get('name')
        if not name:
            print(f"Missing 'name' field in download item: {item}")
            sys.exit(1)

        result = subprocess.run(['download', name, source, destination])
        if result.returncode != 0:
            print(f"Download failed for {source}")
            sys.exit(1)

        env_src = f"SRC_{name.upper()}"
        env_dst = f"DST_{name.upper()}"

        os.environ[env_src] = source
        os.environ[env_dst] = destination

        write_runtime_env_var(env_src, source)
        write_runtime_env_var(env_dst, destination)

def main():
    if "--help" in sys.argv or "-h" in sys.argv or len(sys.argv) == 1:
        print("Usage:")
        print("  docker run --rm <image> --config '<json>' <program> [args]")
        print("  --config       JSON configuration with downloads and execution details")
        print("  <program>      Executable to run (e.g., myapp)")
        print("  [args]         Arguments passed to the program")
        print("\nConfiguration schema:\n")

        try:
            schema = load_schema()
            print(json.dumps(schema, indent=2))
        except Exception as e:
            print(f"Error loading schema: {e}")
        sys.exit(0)

    # Load .env if present
    env_path = find_dotenv()
    if env_path:
        print(f"Loading environment variables from {env_path}", flush=True)
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        print("No .env file found. Skipping.", flush=True)

    args = parse_args()

    try:
        config = json.loads(args.config)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}")
        sys.exit(1)

    try:
        schema = load_schema()
        validate(instance=config, schema=schema)
    except ValidationError as e:
        print(f"Validation failed: {e}")
        sys.exit(1)

    if not args.cmd:
        print("No command specified.")
        sys.exit(1)

    if args.cmd[0] == "download":
        downloads = config.get("downloads", [])
        if not downloads:
            print("No downloads defined.")
            sys.exit(1)
        download_files(downloads)
        sys.exit(0)

    if shutil.which(args.cmd[0]) is None:
        print(f"Error: Command not found: {args.cmd[0]}")
        sys.exit(1)

    os.execvp(args.cmd[0], args.cmd)

if __name__ == '__main__':
    main()
