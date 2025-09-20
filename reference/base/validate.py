#!/usr/bin/env python3
"""
JSON Schema Validator for RAS simulation schemas
Supports JSON Schema Draft 2020-12 with latest jsonschema librarys
"""

import argparse
import json
import sys
from pathlib import Path

import jsonschema
from jsonschema import ValidationError, validate


def load_json_from_string(json_string):
    """Load JSON from a string"""
    try:
        return json.loads(json_string)
    except Exception as e:
        print(f"Error parsing JSON string: {e}")
        sys.exit(1)


def load_schemas(schema_dir):
    """Load all schemas from the specified directory"""
    schema_dir = Path(schema_dir)

    if not schema_dir.exists():
        print(f"Schema directory {schema_dir} does not exist")
        sys.exit(1)

    schemas = {}

    for schema_file in schema_dir.glob("*.json"):
        schema = json.loads(schema_file.read_text())
        # Use the schema's $id if present, otherwise use relative path
        schema_id = schema.get("$id", f"./{schema_file.name}")
        schemas[schema_id] = schema
        print(f"Loaded schema: {schema_id}")

    return schemas


def validate_instance(schema, instance, schemas=None):
    """Validate instance against schema using the latest jsonschema library"""
    all_errors = []

    if schemas:
        # Create a simple custom resolver
        from referencing import Registry, Resource

        # Create resources from all schemas
        resources = []
        for schema_id, schema_def in schemas.items():
            try:
                # Create resource with proper specification detection
                resource = Resource.from_contents(schema_def)
                resources.append((schema_id, resource))
            except Exception as e:
                print(f"Warning: Could not create resource for {schema_id}: {e}")

        # Create registry
        registry = Registry().with_resources(resources)

        # Validate with registry and collect all errors
        validator = jsonschema.Draft202012Validator(schema, registry=registry)
        errors = validator.iter_errors(instance)
        all_errors.extend(errors)
    else:
        # Simple validation without cross-references
        validator = jsonschema.Draft202012Validator(schema)
        errors = validator.iter_errors(instance)
        all_errors.extend(errors)

    if all_errors:
        return False, all_errors
    else:
        return True, []


def print_validation_errors(errors):
    """Print validation errors in a readable format"""
    for error in errors:
        if isinstance(error, ValidationError):
            print(f"❌ Validation Error:")
            print(f"  Path: {' -> '.join(str(p) for p in error.absolute_path)}")
            print(f"  Message: {error.message}")
            if error.schema_path:
                print(f"  Schema path: {' -> '.join(str(p) for p in error.schema_path)}")
            print()
        else:
            print(f"❌ Error: {error}")


def main():
    parser = argparse.ArgumentParser(description="Validate JSON instance against schema")
    parser.add_argument("--schema", "-s", required=True, help="Path to main schema file")
    parser.add_argument("--instance", "-i", required=True, help="JSON instance as a string (must be valid JSON)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Load schemas
    schemas_dir = "/schemas"
    schema_file = f"{schemas_dir}/{args.schema}"
    if not Path(schema_file).exists():
        print(f"Schema file {schema_file} not found")
        print(f"Available schemas in {schemas_dir}:")
        for f in Path(schemas_dir).glob("*.json"):
            print(f" - {f.name}")
        sys.exit(1)
    schema = json.loads(Path(schema_file).read_text())

    # Load all schemas
    schemas = load_schemas(schemas_dir)

    # Parse instance from string
    instance = load_json_from_string(args.instance)

    if args.verbose:
        print(f"Schema: {schema_file}")
        print(f"Instance (as string): {args.instance}")
        print("Validating...")

    # Validate
    valid, errors = validate_instance(schema, instance, schemas)

    if valid:
        print("✅ Validation PASSED")
        sys.exit(0)
    else:
        print("❌ Validation FAILED")
        print_validation_errors(errors)
        sys.exit(1)


if __name__ == "__main__":
    main()
