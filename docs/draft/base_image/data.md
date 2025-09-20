# Data Schemas

Shared schema definitions for Paths, DataPaths, and DataSource (Inputs / Outputs) by action schemas.

## Paths

Named path templates used by inputs/outputs. May include a 'default' path. Placeholders like {ATTR::model-name} are resolved from the action's attributes.

### Properties

| Property | Type | Description | Required |
|----------|------|-------------|----------|
| default | string | Default/fallback path template. | No |

#### Property Examples

- **default**: `{ATTR::scenario}/{ATTR::base-hydrology-directory}/{ATTR::model-name}/{ATTR::control-name}.control`, `{ATTR::scenario}/{ATTR::base-hydrology-directory}/{ATTR::model-name}/{ATTR::model-name}.dss`

## DataPaths

Mapping of domain keys to selectors/locations inside files (e.g., DSS pathname or HDF internal path).

### Examples

#### Example 1

```json
{
  "DSS": "//BASIN/LOCATION/VAR/1DAY/OBS",
  "HDF": "/Results/subgroup/dataset"
}
```

## DataSource

### Properties

| Property | Type | Description | Required |
|----------|------|-------------|----------|
| name | string | Logical input name. | Yes |
| paths | object | Named path templates for locating input files/objects. | Yes |
| data_paths | object | Map of domain keys to in-file selectors (optional unless required by the specific action). | No |
| store | object | Inline store config for this data source. | No |
| store_name | string | Reference to a named top-level store in the action. | No |

#### Property Examples

- **name**: `source`

