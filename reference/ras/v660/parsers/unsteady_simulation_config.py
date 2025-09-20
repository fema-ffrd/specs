from dataclasses import dataclass, fields
from typing import List, Optional
import re
from pathlib import Path


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
class InputPaths:
    b_file: Optional[str] = None
    o_file: Optional[str] = None
    tmp_hdf: Optional[str] = None
    x_file: Optional[str] = None


@dataclass
class OutputPaths:
    hdf_output: Optional[str] = None
    rasoutput_log: Optional[str] = None


@dataclass
class Input:
    name: str
    paths: InputPaths
    store_name: str
    store_root: str
    store_type: Optional[str] = None  # Added store_type

    def __post_init__(self):
        if isinstance(self.paths, dict):
            self.paths = InputPaths(**convert_keys_to_snake_case(self.paths))


@dataclass
class Output:
    name: str
    paths: OutputPaths
    store_name: str
    store_root: str
    store_type: Optional[str] = None  # Added store_type

    def __post_init__(self):
        if isinstance(self.paths, dict):
            self.paths = OutputPaths(**convert_keys_to_snake_case(self.paths))

    def create_local_output_paths(self, local_root: str, local_prefix: str = None) -> dict:
        """
        Create local output paths based on the given local source directory.

        Args:
            local_root (str): The base directory for local output paths.

        Returns:
            dict: A dictionary mapping output file types to their local paths.
        """
        local_paths = {}
        for field in fields(self.paths):
            file_path = getattr(self.paths, field.name)
            if file_path and local_prefix:
                file_name = Path(file_path).name
                local_paths[field.name] = f"{local_root}/{local_prefix}/{file_name}"
            elif file_path:
                file_name = Path(file_path).name
                local_paths[field.name] = f"{local_root}/{file_name}"
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
class Attributes:
    geom: str
    plan: str
    modelPrefix: str
    base_hydraulics_directory: str
    outputdir: str


@dataclass
class Config:
    name: str
    type: str
    attributes: Attributes
    inputs: List[Input]
    outputs: List[Output]
    stores: List[Store]

    def __post_init__(self):
        # Convert keys in all nested dictionaries to snake_case
        self.attributes = Attributes(**convert_keys_to_snake_case(self.attributes))
        self.stores = [
            Store(**convert_keys_to_snake_case(store_item)) if isinstance(store_item, dict) else store_item
            for store_item in self.stores
        ]

        # Initialize inputs and outputs
        self.inputs = [self._initialize_item(input_item, Input, InputPaths) for input_item in self.inputs]
        self.outputs = [self._initialize_item(output_item, Output, OutputPaths) for output_item in self.outputs]

        # Automatically substitute attributes after initialization
        self.substitute_attributes()

    def _initialize_item(self, item, item_class, paths_class):
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
            for field in fields(paths_obj):
                field_value = getattr(paths_obj, field.name)
                if isinstance(field_value, str):
                    setattr(paths_obj, field.name, substitute_placeholders(field_value))

        # Substitute placeholders in inputs
        for input_item in self.inputs:
            substitute_paths(input_item.paths)

        # Substitute placeholders in outputs
        for output_item in self.outputs:
            substitute_paths(output_item.paths)

    def get_item_by_name(self, name: str, items: List, item_class) -> Optional:
        """Retrieve an Input or Output by its name."""
        for item in items:
            if item.name == name:
                # Find the corresponding store for this item
                for store in self.stores:
                    if store.name == item.store_name:
                        item.store_root = store.params.root
                        item.store_type = store.store_type
                        # Set the path and store_root for all fields in paths
                        for field in fields(item.paths):
                            field_value = getattr(item.paths, field.name)
                            if isinstance(field_value, str):
                                setattr(item.paths, field.name, field_value)
                        return item
        return None

    def get_input_by_name(self, input_name: str) -> Optional[Input]:
        """Retrieve an input by its name."""
        return self.get_item_by_name(input_name, self.inputs, Input)

    def get_output_by_name(self, output_name: str) -> Optional[Output]:
        """Retrieve an output by its name."""
        return self.get_item_by_name(output_name, self.outputs, Output)
