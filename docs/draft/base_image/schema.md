## 🗃️ Schema

This page includes the complete configuration schema used by the base image to validate plugin execution parameters.

It is provided as a reference for plugin authors and base image reimplementers.

### 🔍 JSON Schemas

{% include "draft/base_image/action.md" %}

```json
{% include "../../../reference/base/schemas/action.json" %}
```

{% include "draft/base_image/data.md" %}

```json
{% include "../../../reference/base/schemas/data.json" %}
```

{% include "draft/base_image/store.md" %}

```json
{% include "../../../reference/base/schemas/store.json" %}
```

### 🧾 Notes

For more information on schema extensions, see the Base Image Specification.
