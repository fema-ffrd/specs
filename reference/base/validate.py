#!/usr/bin/env python3

import json
import sys
from pathlib import Path

from jsonschema import Draft7Validator, validate
from referencing import Registry, Resource

SCHEMAS_DIR = "/schemas"


def usage():
    print("Usage:")
    print("  validate '<json_config_string>'")
    sys.exit(1)


def load_json_string(json_str):
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON string.\nReason: {e}")
        sys.exit(1)


def build_registry():
    registry = {}
    for path in Path(SCHEMAS_DIR).glob("*.json"):
        try:
            content = json.loads(path.read_text())
            resource = Resource.from_contents(content)
            # Use $id if available, otherwise fallback to filename
            if "$id" in content:
                registry[content["$id"]] = resource
            registry[path.name] = resource
        except Exception as e:
            print(f"❌ Failed to load schema {path.name}: {e}")
            sys.exit(1)

    return Registry().with_resources(registry.items())


def validate_section(name, data, registry):
    schema_filename = f"{name}.json"

    try:
        resource = registry.get(schema_filename)
    except Exception:
        print(f"⚠️ No schema found for section '{name}' (expected: {schema_filename})")
        return True  # Soft-fail

    try:
        schema = resource.contents
        validator = Draft7Validator(schema, registry=registry)
        validator.validate(data)
        print(f"✅ Section '{name}' passed validation.")
        return True
    except Exception as e:
        print(f"❌ Validation errors in section '{name}':\n  - {e}")
        return False


def main():
    if len(sys.argv) != 2:
        usage()

    config = load_json_string(sys.argv[1])
    if not isinstance(config, dict):
        print("❌ Top-level config must be a JSON object.")
        sys.exit(1)

    registry = build_registry()

    success = True
    for section_name, section_data in config.items():
        ok = validate_section(section_name, section_data, registry)
        success = success and ok

    if success:
        print("🎉 All sections passed validation.")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
