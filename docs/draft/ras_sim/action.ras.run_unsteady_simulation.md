# unsteady-simulation

Schema for an unsteady HEC-RAS simulation action. Combines action metadata, attribute substitutions, input data sources, outputs, and store configuration.

## References

This schema extends or references the following base schemas:

- [action.json](../base_image/action.md)
- [data.json](../base_image/data.md)

### Properties

| Property | Type | Description | Required |
|----------|------|-------------|----------|
| name | string | Logical name for this action (e.g., step name in a workflow). | Yes |
| type | string | Action type identifier (tool/operator name). In future versions may be an enum supporting named types such as `link`, `utils`, `extract`, and `run` | Yes |
| description | string | Human-readable summary of the action. | No |
| attributes | object | Primitive attributes used for template substitution in path strings (accessible via {ATTR::...}). | Yes |
| inputs | array | Input data sources required for the unsteady simulation. | Yes |
| outputs | array | Output data sources produced by the unsteady simulation. | Yes |
| stores | array | List of storage configurations for this action. | Yes |

#### attributes Properties

| Property | Type | Description | Required |
|----------|------|-------------|----------|
| geom | string | Geometry identifier suffix (e.g. '01'). | Yes |
| plan | string | Plan identifier (e.g. '01'). | Yes |
| modelPrefix | string | Model prefix used in file names (e.g. 'lavon'). | Yes |
| base-hydraulics-directory | string | Base directory for hydraulics files. | Yes |
| base-system-response-directory | string | Base directory for system-response outputs. | No |
| outputdir | string | Top-level output directory name. | Yes |
| scenario | string | Scenario name or folder (e.g. 'conformance'). | No |
| CC_EVENT_IDENTIFIER | string | Alternate / placeholder for testing ENV vars. | No |

