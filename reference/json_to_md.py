import json
from pathlib import Path


def resolve_schema_references(schema_data, base_schemas_path):
    """Resolve $ref references to base schemas"""
    resolved_refs = []  # Track resolved references

    def _resolve_recursive(data):
        if isinstance(data, dict):
            if "$ref" in data:
                ref_path = data["$ref"]
                if ref_path.startswith("./"):
                    # Local reference - try to resolve from base schemas
                    schema_file = ref_path.split("#")[0].lstrip("./")
                    schema_path = base_schemas_path / schema_file

                    if schema_path.exists():
                        resolved_refs.append(f"[{schema_file}](../base_image/{schema_file.replace('.json', '.md')})")
                        with open(schema_path, "r") as f:
                            ref_schema = json.load(f)

                        # Handle fragment references like #/$defs/Action
                        if "#" in ref_path:
                            fragment = ref_path.split("#")[1]
                            if fragment.startswith("/$defs/"):
                                def_name = fragment.split("/")[-1]
                                if "$defs" in ref_schema and def_name in ref_schema["$defs"]:
                                    return ref_schema["$defs"][def_name]
                        return ref_schema
                    else:
                        # Reference not found, return as-is with note
                        return {"description": f"Reference not found: {ref_path}", "type": "object"}

            # Recursively resolve references in nested objects
            resolved = {}
            for key, value in data.items():
                resolved[key] = _resolve_recursive(value)
            return resolved

        elif isinstance(data, list):
            return [_resolve_recursive(item) for item in data]

        return data

    resolved_data = _resolve_recursive(schema_data)
    return resolved_data, resolved_refs


def merge_allof_schemas(schema_data):
    """Merge allOf schemas into a single schema"""
    if "allOf" not in schema_data:
        return schema_data

    merged = {}
    for subschema in schema_data["allOf"]:
        for key, value in subschema.items():
            if key == "properties":
                if "properties" not in merged:
                    merged["properties"] = {}
                merged["properties"].update(value)
            elif key == "required":
                if "required" not in merged:
                    merged["required"] = []
                merged["required"].extend(value)
            else:
                merged[key] = value

    # Add any top-level properties not in allOf
    for key, value in schema_data.items():
        if key != "allOf":
            if key == "properties" and "properties" in merged:
                merged["properties"].update(value)
            elif key == "required" and "required" in merged:
                merged["required"].extend(value)
            else:
                merged[key] = value

    return merged


def process_properties_section(properties, required_props, level="Properties"):
    """Process a properties section and return markdown lines"""
    lines = []
    property_examples = {}  # Store examples separately

    lines.append(f"### {level}\n\n")
    lines.append("| Property | Type | Description | Required |\n")
    lines.append("|----------|------|-------------|----------|\n")

    for prop_name, prop_schema in properties.items():
        prop_type = prop_schema.get("type", "object")
        if isinstance(prop_type, list):
            prop_type = ", ".join(prop_type)
        prop_desc = prop_schema.get("description", "")
        is_required = "Yes" if prop_name in required_props else "No"

        # Store examples for later display
        examples = prop_schema.get("examples", [])
        if examples:
            property_examples[prop_name] = examples

        # Handle enum types
        if "enum" in prop_schema:
            prop_type = f"enum: {', '.join(prop_schema['enum'])}"

        lines.append(f"| {prop_name} | {prop_type} | {prop_desc} | {is_required} |\n")

    lines.append("\n")

    # Add examples section if any properties have examples
    if property_examples:
        lines.append("#### Property Examples\n\n")
        for prop_name, examples in property_examples.items():
            if len(examples) == 1:
                lines.append(f"- **{prop_name}**: `{examples[0]}`\n")
            else:
                examples_str = ", ".join([f"`{ex}`" for ex in examples])
                lines.append(f"- **{prop_name}**: {examples_str}\n")
        lines.append("\n")

    # Process nested properties for object types
    for prop_name, prop_schema in properties.items():
        if prop_schema.get("type") == "object" and "properties" in prop_schema:
            lines.append(f"#### {prop_name} Properties\n\n")
            lines.append("| Property | Type | Description | Required |\n")
            lines.append("|----------|------|-------------|----------|\n")
            nested_required = prop_schema.get("required", [])
            nested_examples = {}

            for nested_prop_name, nested_prop_schema in prop_schema["properties"].items():
                nested_prop_type = nested_prop_schema.get("type", "object")
                if isinstance(nested_prop_type, list):
                    nested_prop_type = ", ".join(nested_prop_type)
                nested_prop_desc = nested_prop_schema.get("description", "")
                nested_is_required = "Yes" if nested_prop_name in nested_required else "No"

                # Store nested examples
                examples = nested_prop_schema.get("examples", [])
                if examples:
                    nested_examples[nested_prop_name] = examples

                # Handle enum types
                if "enum" in nested_prop_schema:
                    nested_prop_type = f"enum: {', '.join(nested_prop_schema['enum'])}"

                lines.append(
                    f"| {nested_prop_name} | {nested_prop_type} | {nested_prop_desc} | {nested_is_required} |\n"
                )

            lines.append("\n")

            # Add nested examples if any
            if nested_examples:
                lines.append(f"##### {prop_name} Examples\n\n")
                for nested_prop_name, examples in nested_examples.items():
                    if len(examples) == 1:
                        lines.append(f"- **{nested_prop_name}**: `{examples[0]}`\n")
                    else:
                        examples_str = ", ".join([f"`{ex}`" for ex in examples])
                        lines.append(f"- **{nested_prop_name}**: {examples_str}\n")
                lines.append("\n")

    return lines


def json_schema_to_markdown(schema_data, schema_name, base_schemas_path):
    """Convert JSON schema to basic markdown documentation"""
    lines = []

    # Resolve references first and track them
    schema_data, resolved_refs = resolve_schema_references(schema_data, base_schemas_path)

    # Handle allOf schemas
    schema_data = merge_allof_schemas(schema_data)

    # Header
    title = schema_data.get("title", schema_name)
    lines.append(f"# {title}\n\n")

    # Description
    if "description" in schema_data:
        lines.append(f"{schema_data['description']}\n\n")

    # Add references section if there are any resolved references
    if resolved_refs:
        lines.append("## References\n\n")
        lines.append("This schema extends or references the following base schemas:\n\n")
        # Remove duplicates while preserving order
        seen = set()
        unique_refs = []
        for ref in resolved_refs:
            if ref not in seen:
                seen.add(ref)
                unique_refs.append(ref)

        for ref in unique_refs:
            lines.append(f"- {ref}\n")
        lines.append("\n")

    # Process $defs if they exist
    if "$defs" in schema_data:
        for def_name, def_schema in schema_data["$defs"].items():
            lines.append(f"## {def_name}\n\n")

            if "description" in def_schema:
                lines.append(f"{def_schema['description']}\n\n")

            if "properties" in def_schema:
                required_props = def_schema.get("required", [])
                lines.extend(process_properties_section(def_schema["properties"], required_props))

            # Add schema-level examples if they exist
            if "examples" in def_schema:
                lines.append("### Examples\n\n")
                for i, example in enumerate(def_schema["examples"], 1):
                    lines.append(f"#### Example {i}\n\n")
                    lines.append("```json\n")
                    lines.append(json.dumps(example, indent=2))
                    lines.append("\n```\n\n")

    # Process top-level properties if they exist
    if "properties" in schema_data:
        required_props = schema_data.get("required", [])
        lines.extend(process_properties_section(schema_data["properties"], required_props))

        # Add top-level examples if they exist
        if "examples" in schema_data:
            lines.append("## Examples\n\n")
            for i, example in enumerate(schema_data["examples"], 1):
                lines.append(f"### Example {i}\n\n")
                lines.append("```json\n")
                lines.append(json.dumps(example, indent=2))
                lines.append("\n```\n\n")

    return lines


def process_schema_directories(schema_doc_pairs, base_schemas_path):
    """Process multiple schema/doc directory pairs"""

    for schema_dir, doc_dir in schema_doc_pairs:
        print(f"\nProcessing schema directory: {schema_dir}")
        print(f"Output directory: {doc_dir}")

        # Ensure output directory exists
        doc_dir.mkdir(parents=True, exist_ok=True)

        for schema in Path(schema_dir).glob("*.json"):
            print(f"Processing {schema}")

            try:
                with open(schema, "r") as json_file:
                    schema_data = json.load(json_file)

                md_lines = json_schema_to_markdown(schema_data, schema.stem, base_schemas_path)

                # Output to the documentation directory
                out_path = doc_dir / schema.with_suffix(".md").name
                print(f"Writing to {out_path}")

                with open(out_path, "w") as md_file:
                    md_file.writelines(md_lines)

                print(f"Successfully processed {schema.name}")

            except Exception as e:
                print(f"Error processing {schema.name}: {e}")
                print(f"Skipping {schema.name} and continuing with next file...")
                continue

    print("Processing complete!")


# Base schemas directory for resolving references
base_schemas_path = Path(__file__).parent.parent / "reference" / "base" / "schemas"

# Define schema/doc directory pairs
workspace_root = Path(__file__).parent.parent
schema_doc_pairs = [
    (workspace_root / "reference" / "base" / "schemas", workspace_root / "docs" / "draft" / "base_image"),
    (workspace_root / "reference" / "ras" / "v660" / "schemas", workspace_root / "docs" / "draft" / "ras_sim"),
]

# Process all schema/doc pairs
process_schema_directories(schema_doc_pairs, base_schemas_path)
