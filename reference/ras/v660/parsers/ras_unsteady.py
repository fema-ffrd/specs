from dataclasses import dataclass, fields
from typing import List, Optional
import re


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

    def __post_init__(self):
        if isinstance(self.paths, dict):
            self.paths = InputPaths(**convert_keys_to_snake_case(self.paths))


@dataclass
class Output:
    name: str
    paths: OutputPaths
    store_name: str

    def __post_init__(self):
        if isinstance(self.paths, dict):
            self.paths = OutputPaths(**convert_keys_to_snake_case(self.paths))


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
    store: Store

    def __post_init__(self):
        # Convert keys in all nested dictionaries to snake_case
        self.attributes = Attributes(**convert_keys_to_snake_case(self.attributes))
        self.inputs = [
            Input(**convert_keys_to_snake_case(input_item)) if isinstance(input_item, dict) else input_item
            for input_item in self.inputs
        ]
        self.outputs = [
            Output(**convert_keys_to_snake_case(output_item)) if isinstance(output_item, dict) else output_item
            for output_item in self.outputs
        ]
        self.store = Store(**convert_keys_to_snake_case(self.store))

        # Automatically substitute attributes after initialization
        self.substitute_attributes()

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

    def get_input_by_name(self, input_name: str) -> Optional[Input]:
        """Retrieve an input by its name."""
        for input_item in self.inputs:
            if input_item.name == input_name:
                return input_item
        return None

    def get_output_by_name(self, output_name: str) -> Optional[Output]:
        """Retrieve an output by its name."""
        for output_item in self.outputs:
            if output_item.name == output_name:
                return output_item
        return None
