# Data Schemas

*Shared schema definitions for Paths, DataPaths, and DataSource (Inputs / Outputs) by action schemas.*

## Definitions

- <a id="%24defs/Paths"></a>**`Paths`** *(object)*: Named path templates used by inputs/outputs. May include a 'default' path. Placeholders like {ATTR::model-name} are resolved from the action's attributes. Can contain additional properties.
  - <a id="%24defs/Paths/additionalProperties"></a>**Additional properties** *(string)*: Path template string.
  - <a id="%24defs/Paths/properties/default"></a>**`default`** *(string)*: Default/fallback path template.

    Examples:
    ```json
    "{ATTR::scenario}/{ATTR::base-hydrology-directory}/{ATTR::model-name}/{ATTR::control-name}.control"
    ```

    ```json
    "{ATTR::scenario}/{ATTR::base-hydrology-directory}/{ATTR::model-name}/{ATTR::model-name}.dss"
    ```

- <a id="%24defs/DataPaths"></a>**`DataPaths`** *(object)*: Mapping of domain keys to selectors/locations inside files (e.g., DSS pathname or HDF internal path). Can contain additional properties.
  - <a id="%24defs/DataPaths/additionalProperties"></a>**Additional properties** *(string, number, boolean, or array)*

  Examples:
  ```json
  {
      "DSS": "//BASIN/LOCATION/VAR/1DAY/OBS",
      "HDF": "/Results/subgroup/dataset"
  }
  ```

- <a id="%24defs/DataSource"></a>**`DataSource`** *(object)*: Cannot contain additional properties.
  - <a id="%24defs/DataSource/properties/name"></a>**`name`** *(string, required)*: Logical input name.

    Examples:
    ```json
    "source"
    ```

  - <a id="%24defs/DataSource/properties/paths"></a>**`paths`** *(required)*: Named path templates for locating input files/objects. Refer to *[#/$defs/Paths](#%24defs/Paths)*.
  - <a id="%24defs/DataSource/properties/data_paths"></a>**`data_paths`**: Map of domain keys to in-file selectors (optional unless required by the specific action). Refer to *[#/$defs/DataPaths](#%24defs/DataPaths)*.
  - <a id="%24defs/DataSource/properties/store"></a>**`store`** *(required)*: Store for this input. Refer to *[./store.json](./store.md#)*.
