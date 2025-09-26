# Action

A generic action (e.g. model simulatuion, data or transformation step) with typed inputs/outputs, parameterized paths, and optional operator parameters. See specific action schemas for specialized actions, attrubutes, and parameters.

## References

This schema extends or references the following base schemas:

- [data.json](../base_image/data.md)
- [store.json](../base_image/store.md)

## Action

### Properties

| Property    | Type   | Description                                                                                                                                         | Required |
| ----------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------- | -------- |
| name        | string | Logical name for this action (e.g., step name in a workflow).                                                                                       | Yes      |
| type        | string | Action type identifier (tool/operator name). In future versions may be an enum supporting named types such as `link`, `utils`, `extract`, and `run` | Yes      |
| description | string | Human-readable summary of the action.                                                                                                               | No       |
| attributes  | object | Primitive attributes used for template substitution in path strings.                                                                                | Yes      |
| inputs      | array  | One or more inputs.                                                                                                                                 | No       |
| outputs     | array  | One or more outputs.                                                                                                                                | No       |
| stores      | array  | List of storage configurations for this action.                                                                                                     | No       |
