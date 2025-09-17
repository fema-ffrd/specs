# Action

*A generic action (e.g. model simulatuion, data or transformation step) with typed inputs/outputs, parameterized paths, and optional operator parameters. See specific action schemas for specialized actions, attrubutes, and parameters.*

## Properties

- <a id="properties/name"></a>**`name`** *(string, required)*: Logical name for this action (e.g., step name in a workflow).
- <a id="properties/type"></a>**`type`** *(string, required)*: Action type identifier (tool/operator name). In future versions may be an enum supporting named types such as `link`, `utils`, `extract`, and `run`.
- <a id="properties/description"></a>**`description`** *(string)*: Human-readable summary of the action.
- <a id="properties/attributes"></a>**`attributes`** *(object, required)*: Primitive attributes used for template substitution in path strings. Can contain additional properties.
  - <a id="properties/attributes/additionalProperties"></a>**Additional properties** *(string, number, or boolean)*
- <a id="properties/inputs"></a>**`inputs`** *(array)*: One or more inputs.
  - <a id="properties/inputs/items"></a>**Items**: Refer to *[./data.json#/$defs/DataSource](./data.md#/%24defs/DataSource)*.
- <a id="properties/outputs"></a>**`outputs`** *(array)*: One or more outputs. Length must be at least 1.
  - <a id="properties/outputs/items"></a>**Items**: Refer to *[./data.json#/$defs/DataSource](./data.md#/%24defs/DataSource)*.
## Examples

  ```json
  {
      "name": "dss_to_hdf",
      "type": "link",
      "description": "Export selected data from HMS output in DSS format to RAS input in HDF files",
      "attributes": {
          "model-name": "trinity",
          "plan": "01",
          "hydrology-simulation": "SST"
      },
      "inputs": [
          {
              "name": "source",
              "paths": {
                  "default": "/model/{ATTR::model-name}/{ATTR::hydrology-simulation}.dss"
              },
              "data_paths": {
                  "east-fork_s090": "//east-fork_s090/FLOW-BASE//1Hour/RUN:SST/"
              },
              "store": {
                  "name": "FFRD",
                  "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                  "store_type": "S3",
                  "profile": "FFRD",
                  "params": {
                      "root": "model-library/ffrd-trinity"
                  }
              }
          }
      ],
      "outputs": [
          {
              "name": "destination",
              "paths": {
                  "default": "/model/{ATTR::model-name}/lavon.p{ATTR::plan}.hdf"
              },
              "data_paths": {
                  "east-fork_s090": "Event Conditions/Unsteady/Boundary Conditions/Flow Hydrographs/2D: lavon BCLine: bc_east-fork_s090_base"
              },
              "store": {
                  "name": "FFRD",
                  "id": "6ba7b810-9dad-11d1-80b4-00c04fd430c8",
                  "store_type": "S3",
                  "profile": "FFRD",
                  "params": {
                      "root": "model-library/ffrd-trinity"
                  }
              }
          }
      ]
  }
  ```

