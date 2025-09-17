import json
import jsonschema2md
from pathlib import Path

parser = jsonschema2md.Parser(examples_as_yaml=False, show_examples="all", domain=".")

scehma_root = Path(__file__).parent

for scehma in Path(scehma_root).rglob("*.json"):
    print(f"Processing {scehma}")

    with open(scehma, "r") as json_file:
        md_lines = parser.parse_schema(json.load(json_file))

    out_path = scehma.with_suffix(".md")
    print(out_path)

    with open(out_path, "w") as md_file:
        md_file.writelines(md_lines)
