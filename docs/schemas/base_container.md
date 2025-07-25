# 📑 Base Container Schema Reference

This page includes the complete configuration schema used by the base image to validate plugin execution parameters.

It is provided as a reference for plugin authors and base image reimplementers.

## 🔍 JSON Schema (Raw View)

~~~json
{% include "schemas/base_container.json" %}
~~~


## 🧾 Notes

- The schema is based on [JSON Schema Draft 7](https://json-schema.org/draft-07/schema)
- This file defines the required structure for `--config` passed to the container
- Extensions can be added in `schema-extension.json` and merged during image build

For more information on schema extensions, see the Base Image Specification.

