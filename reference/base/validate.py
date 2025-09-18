#!/usr/bin/env python3
"""
JSON Schema Validator for RAS simulation schemas
Supports JSON Schema Draft 2020-12 with latest jsonschema librarys
"""

import argparse
import json
import os
import sys
from pathlib import Path

import jsonschema
from jsonschema import ValidationError, validate


def load_json(file_path):
    """Load JSON from file"""
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        sys.exit(1)


def load_schemas(schema_dir=None):
    """Load all schemas from directory, defaulting to local schemas directory"""
    if schema_dir is None:
        # Default to schemas directory in current working directory
        schema_dir = Path.cwd() / "schemas"
    else:
        schema_dir = Path(schema_dir)

    if not schema_dir.exists():
        print(f"Schema directory {schema_dir} does not exist")
        sys.exit(1)

    schemas = {}

    for schema_file in schema_dir.glob("*.json"):
        schema = load_json(schema_file)
        # Use the schema's $id if present, otherwise use relative path
        schema_id = schema.get("$id", f"./{schema_file.name}")
        schemas[schema_id] = schema
        print(f"Loaded schema: {schema_id}")

    return schemas


def validate_instance(schema, instance, schemas=None):
    """Validate instance against schema using the latest jsonschema library"""
    try:
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

            # Validate with registry
            jsonschema.validate(instance, schema, registry=registry)
        else:
            # Simple validation without cross-references
            jsonschema.validate(instance, schema)

        return True, []

    except ValidationError as e:
        return False, [e]
    except Exception as e:
        # Fall back to simple validation if registry fails
        try:
            jsonschema.validate(instance, schema)
            return True, []
        except ValidationError as ve:
            return False, [ve]
        except Exception as ee:
            return False, [f"Validation error: {ee}"]


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
    parser.add_argument(
        "--schema", "-s", help="Path to main schema file (defaults to schemas/action.ras.run_unsteady_simulation.json)"
    )
    parser.add_argument("--instance", "-i", help="Path to JSON instance file (defaults to example-config.json)")
    parser.add_argument("--schemas-dir", "-d", help="Directory containing all schema files (defaults to ./schemas)")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument(
        "--build-mode", "-b", action="store_true", help="Build mode: use default paths and exit with appropriate codes"
    )
    # Add support for JSON content as positional argument (for Docker usage)
    parser.add_argument("json_content", nargs="?", help="JSON content to validate (for Docker container usage)")

    args = parser.parse_args()

    # Handle Docker container usage (JSON content passed as argument)
    if args.json_content:
        try:
            # Parse JSON content from argument
            instance = json.loads(args.json_content)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON content: {e}")
            sys.exit(1)

        # Use default schema paths for Docker container
        schema_file = "/schemas/action.ras.run_unsteady_simulation.json"
        schemas_dir = "/schemas"

        if not Path(schema_file).exists():
            print(f"Schema file {schema_file} not found in container")
            sys.exit(1)

        print(f"🔍 Docker mode: Validating JSON content against {schema_file}")

        # Load main schema
        schema = load_json(schema_file)

        # Load all schemas
        schemas = load_schemas(schemas_dir)

        print("Validating...")

    else:
        # Regular command-line usage
        # Set defaults for build mode or when not specified
        schema_file = args.schema or "schemas/action.ras.run_unsteady_simulation.json"
        instance_file = args.instance or "example-config.json"
        schemas_dir = args.schemas_dir  # Can be None, will default in load_schemas()

        # Check if we're in the right directory (should have schemas/ and example-config.json)
        if not Path("schemas").exists() or not Path("example-config.json").exists():
            if not args.build_mode:
                print("Warning: Expected to be run from a directory containing 'schemas/' and 'example-config.json'")
            # Don't exit in build mode, let it continue and fail gracefully

        if args.verbose or args.build_mode:
            print(f"Schema: {schema_file}")
            print(f"Instance: {instance_file}")
            if schemas_dir:
                print(f"Schemas directory: {schemas_dir}")
            else:
                print(f"Schemas directory: ./schemas (default)")
            print()

        # Load main schema
        if not Path(schema_file).exists():
            print(f"Schema file {schema_file} not found")
            sys.exit(1)
        schema = load_json(schema_file)

        # Load all schemas
        schemas = load_schemas(schemas_dir)

        # Load instance
        if not Path(instance_file).exists():
            print(f"Instance file {instance_file} not found")
            sys.exit(1)
        instance = load_json(instance_file)

        if args.verbose or args.build_mode:
            print("Validating...")

    # Validate (common for both modes)
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
