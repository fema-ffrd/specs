# unsteady-simulation

*Schema for an unsteady HEC-RAS simulation action. Combines action metadata, attribute substitutions, input data sources, outputs, and store configuration.*

## Properties

- <a id="properties/attributes"></a>**`attributes`** *(object, required)*: Primitive attributes used for template substitution in path strings (accessible via {ATTR::...}). Can contain additional properties.
  - <a id="properties/attributes/additionalProperties"></a>**Additional properties** *(string, number, or boolean)*
  - <a id="properties/attributes/properties/geom"></a>**`geom`** *(string, required)*: Geometry identifier suffix (e.g. '01').
  - <a id="properties/attributes/properties/plan"></a>**`plan`** *(string, required)*: Plan identifier (e.g. '01').
  - <a id="properties/attributes/properties/modelPrefix"></a>**`modelPrefix`** *(string, required)*: Model prefix used in file names (e.g. 'lavon').
  - <a id="properties/attributes/properties/base-hydraulics-directory"></a>**`base-hydraulics-directory`** *(string, required)*: Base directory for hydraulics files.
  - <a id="properties/attributes/properties/base-system-response-directory"></a>**`base-system-response-directory`** *(string, required)*: Base directory for system-response outputs.
  - <a id="properties/attributes/properties/outputdir"></a>**`outputdir`** *(string, required)*: Top-level output directory name.
  - <a id="properties/attributes/properties/scenario"></a>**`scenario`** *(string, required)*: Scenario name or folder (e.g. 'conformance').
- <a id="properties/inputs"></a>**`inputs`** *(object, required)*: Input set of data_sources required for the unsteady simulation. Cannot contain additional properties.
  - <a id="properties/inputs/properties/data_sources"></a>**`data_sources`** *(array, required)*: An ordered list of input data sources. Each entry is validated against the shared DataSource definition. At least one entry must be the temporary HDF file (with name matching '.*\.tmp\.hdf$'). Length must be at least 1. Contains schema must be matched at least 1 times.
    - <a id="properties/inputs/properties/data_sources/items"></a>**Items**: Refer to *[#/$defs/DataSource](#%24defs/DataSource)*.
    - <a id="properties/inputs/properties/data_sources/contains"></a>**Contains** *(object)*
      - <a id="properties/inputs/properties/data_sources/contains/properties/name"></a>**`name`**: Must match pattern: `.*\.tmp\.hdf$` ([Test](https://regexr.com/?expression=.%2A%5C.tmp%5C.hdf%24)).
      - <a id="properties/inputs/properties/data_sources/contains/properties/paths"></a>**`paths`** *(object, required)*: Can contain additional properties.
        - <a id="properties/inputs/properties/data_sources/contains/properties/paths/properties/b_file"></a>**`b_file`** *(string, required)*: Path to the HEC-RAS boundary condition file (.b##).
        - <a id="properties/inputs/properties/data_sources/contains/properties/paths/properties/o_file"></a>**`o_file`** *(string, required)*: Path to HEC-RAS file (.o##).
        - <a id="properties/inputs/properties/data_sources/contains/properties/paths/properties/tmp_hdf"></a>**`tmp_hdf`** *(string, required)*: Path to the HEC-RAS temporary HDF file (.tmp.hdf) used for the unsteady simulation.
        - <a id="properties/inputs/properties/data_sources/contains/properties/paths/properties/x_file"></a>**`x_file`** *(string, required)*: Path to the HEC-RAS file (.x##).

    Examples:
    ```json
    {
        "name": "tmp.hdf",
        "paths": {
            "b_file": "{ATTR::scenario}/{ATTR::base-hydraulics-directory}/{ATTR::modelPrefix}/{ATTR::modelPrefix}.b{ATTR::geom}",
            "o_file": "{ATTR::scenario}/{ATTR::base-hydraulics-directory}/{ATTR::modelPrefix}/{ATTR::modelPrefix}.ic.o{ATTR::plan}",
            "tmp_hdf": "{ATTR::scenario}/{ATTR::outputdir}/event-data/{ENV::CC_EVENT_IDENTIFIER}/{ATTR::base-hydraulics-directory}/{ATTR::modelPrefix}/{ATTR::modelPrefix}.p{ATTR::plan}.tmp.hdf",
            "x_file": "{ATTR::scenario}/{ATTR::base-hydraulics-directory}/{ATTR::modelPrefix}/{ATTR::modelPrefix}.x{ATTR::plan}"
        },
        "store_name": "FFRD"
    }
    ```

    ```json
    {
        "name": "failure_elevations.json",
        "paths": {
            "failure_elevations": "{ATTR::scenario}/{ATTR::outputdir}/event-data/{ENV::CC_EVENT_IDENTIFIER}/{ATTR::base-system-response-directory}/failure_elevations.json"
        },
        "store_name": "FFRD"
    }
    ```

- <a id="properties/outputs"></a>**`outputs`** *(object, required)*: Output data configuration that includes the specific set of data_sources produced by the unsteady simulation. Cannot contain additional properties.
  - <a id="properties/outputs/properties/data_sources"></a>**`data_sources`** *(array, required)*: An ordered list of output data. Each entry is validated against the shared DataSource definition. Length must be at least 2.
    - **All of**
      - <a id="properties/outputs/properties/data_sources/allOf/0"></a>: Contains schema must be matched at least 1 times.
        - <a id="properties/outputs/properties/data_sources/allOf/0/contains"></a>**Contains** *(object)*
          - <a id="properties/outputs/properties/data_sources/allOf/0/contains/properties/name"></a>**`name`**: Must be: `"hdf_output"`.
      - <a id="properties/outputs/properties/data_sources/allOf/1"></a>: Contains schema must be matched at least 1 times.
        - <a id="properties/outputs/properties/data_sources/allOf/1/contains"></a>**Contains** *(object)*
          - <a id="properties/outputs/properties/data_sources/allOf/1/contains/properties/name"></a>**`name`**: Must be: `"rasoutput_log"`.
    - <a id="properties/outputs/properties/data_sources/items"></a>**Items**: Refer to *[#/$defs/DataSource](#%24defs/DataSource)*.

    Examples:
    ```json
    {
        "name": "hdf_output",
        "paths": {
            "hdf_output": "{ATTR::scenario}/{ATTR::outputdir}/event-data/{ENV::CC_EVENT_IDENTIFIER}/{ATTR::base-hydraulics-directory}/{ATTR::modelPrefix}/{ATTR::modelPrefix}.p{ATTR::plan}.hdf"
        },
        "store_name": "FFRD"
    }
    ```

    ```json
    {
        "name": "rasoutput_log",
        "paths": {
            "rasoutput_log": "{ATTR::scenario}/{ATTR::outputdir}/event-data/{ENV::CC_EVENT_IDENTIFIER}/{ATTR::base-hydraulics-directory}/{ATTR::modelPrefix}/rasoutput.log"
        },
        "store_name": "FFRD"
    }
    ```

- <a id="properties/store"></a>**`store`** *(required)*: Refer to *[#/$defs/Store](#%24defs/Store)*.
## Definitions

- <a id="%24defs/Action"></a>**`Action`**: Refer to *[./action.json#/$defs/Action](./action.md#/%24defs/Action)*.
- <a id="%24defs/Store"></a>**`Store`**: Refer to *[./store.json#/$defs/Store](./store.md#/%24defs/Store)*.
- <a id="%24defs/DataSource"></a>**`DataSource`**: Refer to *[./data.json#/$defs/DataSource](./data.md#/%24defs/DataSource)*.
