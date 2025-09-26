#!/usr/bin/env python3
"""
Configuration Parser with ATTR: and ENV: substitution support.
Parses configuration files and resolves attribute and environment variable references.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any, Dict, List, Optional


def convert_keys_to_snake_case(data: dict) -> dict:
    """Recursively convert dictionary keys from hyphen-case to snake_case."""
    if not isinstance(data, dict):
        return data
    new_data = {}
    for key, value in data.items():
        new_key = key.replace("-", "_")
        if isinstance(value, dict):
            new_data[new_key] = convert_keys_to_snake_case(value)
        elif isinstance(value, list):
            new_data[new_key] = [convert_keys_to_snake_case(item) for item in value]
        else:
            new_data[new_key] = value
    return new_data


@dataclass
class GenericPaths:
    """Generic paths container that can hold any path fields."""

    _data: Dict[str, Any]

    def __init__(self, **kwargs):
        self._data = kwargs

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            return super().__getattribute__(name)
        return self._data.get(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            if not hasattr(self, "_data"):
                super().__setattr__("_data", {})
            self._data[name] = value

    def __iter__(self):
        return iter(self._data.items())

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

    def get(self, key: str, default=None):
        return self._data.get(key, default)


@dataclass
class Input:
    name: str
    paths: GenericPaths
    store_name: str
    store_root: str
    store_type: Optional[str] = None  # Added store_type

    def __post_init__(self):
        if isinstance(self.paths, dict):
            self.paths = GenericPaths(**convert_keys_to_snake_case(self.paths))


@dataclass
class Output:
    name: str
    paths: GenericPaths
    store_name: str
    store_root: str
    store_type: Optional[str] = None  # Added store_type

    def __post_init__(self):
        if isinstance(self.paths, dict):
            self.paths = GenericPaths(**convert_keys_to_snake_case(self.paths))

    def create_local_output_paths(self, local_root: str, local_prefix: str = None) -> dict:
        """
        Create local output paths based on the given local source directory.

        Args:
            local_root (str): The base directory for local output paths.

        Returns:
            dict: A dictionary mapping output file types to their local paths.
        """
        local_paths = {}
        for field_name, file_path in self.paths.items():
            if file_path and local_prefix:
                file_name = Path(file_path).name
                local_paths[field_name] = f"{local_root}/{local_prefix}/{file_name}"
            elif file_path:
                file_name = Path(file_path).name
                local_paths[field_name] = f"{local_root}/{file_name}"
        return local_paths


@dataclass
class StoreParams:
    root: str


@dataclass
class Store:
    name: str
    store_type: str
    params: StoreParams

    def __post_init__(self):
        if isinstance(self.params, dict):
            self.params = StoreParams(**convert_keys_to_snake_case(self.params))


@dataclass
class GenericAttributes:
    """Generic attributes container that can hold any attribute fields."""

    _data: Dict[str, Any]

    def __init__(self, **kwargs):
        self._data = kwargs

    def __getattr__(self, name: str) -> Any:
        if name.startswith("_"):
            return super().__getattribute__(name)
        return self._data.get(name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name.startswith("_"):
            super().__setattr__(name, value)
        else:
            if not hasattr(self, "_data"):
                super().__setattr__("_data", {})
            self._data[name] = value

    def __iter__(self):
        return iter(self._data.items())

    def keys(self):
        return self._data.keys()

    def items(self):
        return self._data.items()

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    @property
    def __dict__(self):
        return self._data


@dataclass
class Config:
    name: str
    type: str
    attributes: GenericAttributes
    inputs: List[Input]
    outputs: List[Output]
    stores: List[Store]

    def __post_init__(self):
        # Convert keys in all nested dictionaries to snake_case
        if isinstance(self.attributes, dict):
            self.attributes = GenericAttributes(**convert_keys_to_snake_case(self.attributes))
        elif not isinstance(self.attributes, GenericAttributes):
            # Handle case where attributes might be passed as an object with __dict__
            self.attributes = GenericAttributes(
                **convert_keys_to_snake_case(self.attributes.__dict__ if hasattr(self.attributes, "__dict__") else {})
            )
        self.stores = [
            Store(**convert_keys_to_snake_case(store_item)) if isinstance(store_item, dict) else store_item
            for store_item in self.stores
        ]

        # Initialize inputs and outputs
        self.inputs = [self._initialize_item(input_item, Input) for input_item in self.inputs]
        self.outputs = [self._initialize_item(output_item, Output) for output_item in self.outputs]

        # Automatically substitute attributes after initialization
        self.substitute_attributes()

    def _initialize_item(self, item, item_class):
        """Generic initializer for Input and Output objects."""
        if isinstance(item, dict):
            item = convert_keys_to_snake_case(item)
            store_name = item.get("store_name")
            store_root = None
            store_type = None

            # Find the corresponding store and set store_root and store_type
            for store in self.stores:
                if store.name == store_name:
                    store_root = store.params.root
                    store_type = store.store_type
                    break

            if not store_root:  # Ensure store_root is set
                raise ValueError(f"Store root not found for '{item.get('name')}' with store_name '{store_name}'")

            # Add store_root and store_type to the item dictionary
            item["store_root"] = store_root
            item["store_type"] = store_type

            # Create the item object
            item = item_class(**item)

        return item

    def substitute_attributes(self):
        """Substitute {ATTR:<name>} placeholders in inputs and outputs with values from attributes."""
        attr_dict = self.attributes.__dict__

        def substitute_placeholders(value: Optional[str]) -> Optional[str]:
            """Replace {ATTR:<name>} placeholders in a string with values from attributes."""
            if not isinstance(value, str):
                return value
            return re.sub(r"\{ATTR:([a-zA-Z_][a-zA-Z0-9_]*)\}", lambda m: attr_dict.get(m.group(1), m.group(0)), value)

        def substitute_paths(paths_obj):
            """Substitute placeholders in all fields of a paths object."""
            if isinstance(paths_obj, GenericPaths):
                for field_name, field_value in paths_obj.items():
                    if isinstance(field_value, str):
                        setattr(paths_obj, field_name, substitute_placeholders(field_value))

        # Substitute placeholders in inputs
        for input_item in self.inputs:
            substitute_paths(input_item.paths)

        # Substitute placeholders in outputs
        for output_item in self.outputs:
            substitute_paths(output_item.paths)

    def get_item_by_name(self, name: str, items: List, item_class) -> Optional[Any]:
        """Retrieve an Input or Output by its name."""
        for item in items:
            if item.name == name:
                # Find the corresponding store for this item
                for store in self.stores:
                    if store.name == item.store_name:
                        item.store_root = store.params.root
                        item.store_type = store.store_type
                        # Set the path and store_root for all fields in paths
                        if isinstance(item.paths, GenericPaths):
                            for field_name, field_value in item.paths.items():
                                if isinstance(field_value, str):
                                    setattr(item.paths, field_name, field_value)
                        return item
        return None

    def get_input_by_name(self, input_name: str) -> Optional[Input]:
        """Retrieve an input by its name."""
        return self.get_item_by_name(input_name, self.inputs, Input)

    def get_output_by_name(self, output_name: str) -> Optional[Output]:
        """Retrieve an output by its name."""
        return self.get_item_by_name(output_name, self.outputs, Output)

    def resolve(self) -> Dict[str, Any]:
        """
        Resolve all ATTR: and ENV: substitutions and return the configuration as JSON.

        Returns:
            Dict[str, Any]: The resolved configuration with all substitutions made.

        Raises:
            ValueError: If any ATTR: or ENV: references cannot be resolved.
        """
        missing_attrs = []
        missing_envs = []

        def resolve_substitutions(value: Any, path: str = "") -> Any:
            """
            Recursively resolve ATTR: and ENV: substitutions in any data structure.

            Args:
                value: The value to process (can be string, dict, list, or other types)
                path: Current path in the data structure for error reporting

            Returns:
                The value with all substitutions made
            """
            if isinstance(value, str):
                # Find all ATTR: and ENV: patterns
                attr_pattern = r"\{ATTR:([a-zA-Z_][a-zA-Z0-9_]*)\}"
                env_pattern = r"\{ENV:([a-zA-Z_][a-zA-Z0-9_]*)\}"

                # Check for missing ATTR references
                attr_matches = re.findall(attr_pattern, value)
                for attr_name in attr_matches:
                    if not hasattr(self.attributes, attr_name) or getattr(self.attributes, attr_name) is None:
                        missing_attrs.append(f"ATTR:{attr_name} at {path}")

                # Check for missing ENV references
                env_matches = re.findall(env_pattern, value)
                for env_name in env_matches:
                    if env_name not in os.environ:
                        missing_envs.append(f"ENV:{env_name} at {path}")

                # Perform substitutions
                attr_dict = self.attributes._data if hasattr(self.attributes, "_data") else self.attributes.__dict__

                # Substitute ATTR: references
                resolved_value = re.sub(
                    attr_pattern, lambda m: str(attr_dict.get(m.group(1), f"{{ATTR:{m.group(1)}}}")), value
                )

                # Substitute ENV: references
                resolved_value = re.sub(
                    env_pattern, lambda m: os.environ.get(m.group(1), f"{{ENV:{m.group(1)}}}"), resolved_value
                )

                return resolved_value

            elif isinstance(value, dict):
                return {k: resolve_substitutions(v, f"{path}.{k}" if path else k) for k, v in value.items()}

            elif isinstance(value, list):
                return [resolve_substitutions(item, f"{path}[{i}]") for i, item in enumerate(value)]

            else:
                return value

        # Convert the config to a dictionary representation
        config_dict = self._to_dict()

        # Resolve all substitutions
        resolved_config = resolve_substitutions(config_dict, "config")

        # Check for any missing references and raise error if found
        errors = []
        if missing_attrs:
            errors.append(f"Missing ATTR references: {', '.join(missing_attrs)}")
        if missing_envs:
            errors.append(f"Missing ENV references: {', '.join(missing_envs)}")

        if errors:
            raise ValueError("; ".join(errors))

        return resolved_config

    def _to_dict(self) -> Dict[str, Any]:
        """
        Convert the Config object to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation of the config
        """

        def convert_object(obj):
            """Convert various object types to dictionaries."""
            if hasattr(obj, "_data"):
                # Handle GenericPaths and GenericAttributes
                return obj._data
            elif hasattr(obj, "__dict__"):
                # Handle regular dataclass objects
                result = {}
                for key, value in obj.__dict__.items():
                    if not key.startswith("_"):
                        result[key] = convert_object(value)
                return result
            elif isinstance(obj, list):
                return [convert_object(item) for item in obj]
            elif isinstance(obj, dict):
                return {k: convert_object(v) for k, v in obj.items()}
            else:
                return obj

        return convert_object(self)


def main():
    """
    Main function to parse and resolve configuration files from command line.
    """
    parser = argparse.ArgumentParser(
        description="Parse and resolve configuration files with ATTR: and ENV: substitutions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Resolve config from JSON file
  python parser.py config.json

  # Resolve config from JSON string 
  python parser.py '{"name": "test", "type": "sim", "attributes": {...}, ...}'

  # Pretty print the resolved JSON
  python parser.py config.json --pretty

  # Show verbose output
  python parser.py config.json --verbose
        """,
    )

    parser.add_argument("config", help="Configuration file path or JSON string to parse and resolve")

    parser.add_argument("--pretty", "-p", action="store_true", help="Pretty print the resolved JSON output")

    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output with debugging information")

    args = parser.parse_args()

    # Load configuration data
    config_data = None

    if Path(args.config).exists():
        # Load from file
        if args.verbose:
            print(f"Loading configuration from file: {args.config}", file=sys.stderr)

        try:
            with open(args.config, "r") as f:
                config_data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in file {args.config}: {e}", file=sys.stderr)
            sys.exit(1)
        except IOError as e:
            print(f"Error: Cannot read file {args.config}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Parse as JSON string
        if args.verbose:
            print("Parsing configuration from JSON string", file=sys.stderr)

        try:
            config_data = json.loads(args.config)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON string: {e}", file=sys.stderr)
            sys.exit(1)

    # Create Config object
    if args.verbose:
        print("Creating configuration object...", file=sys.stderr)

    try:
        config = Config(**config_data)
    except Exception as e:
        print(f"Error: Failed to create configuration object: {e}", file=sys.stderr)
        sys.exit(1)

    # Resolve the configuration
    if args.verbose:
        print("Resolving ATTR: and ENV: substitutions...", file=sys.stderr)

    try:
        resolved_config = config.resolve()
    except ValueError as e:
        print(f"Error: Configuration resolution failed: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Unexpected error during resolution: {e}", file=sys.stderr)
        sys.exit(1)

    # Output the resolved configuration
    if args.verbose:
        print("Resolution successful! Outputting resolved configuration:", file=sys.stderr)

    try:
        if args.pretty:
            print(json.dumps(resolved_config, indent=2))
        else:
            print(json.dumps(resolved_config))
    except Exception as e:
        print(f"Error: Failed to output JSON: {e}", file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print("✅ Parser completed successfully", file=sys.stderr)


if __name__ == "__main__":
    main()
