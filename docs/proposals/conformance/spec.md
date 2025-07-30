## 📝 Specification

### Overview
This specification describes requirements for a containerized environment to run both HEC-HMS and HEC-RAS models, with schema validation and environment management.

### Requirements

#### 1. Container Base
- Use upstream containers (`hms-ffrd`, `ras-ffrd`, `ffrd_base`) for model artifacts and base environment.

#### 2. Model Artifacts
- Copy HEC-HMS binaries, libraries, and compute jar from `hms-ffrd`.
- Copy HEC-RAS binaries and libraries from `ras-ffrd`.
- Include execution scripts for both models (`run_hms.sh`, `run-model.sh`).

#### 3. Schema Validation
- Include JSON schemas for HMS and RAS (`hms_schema.json`, `ras_schema.json`).
- Validate configuration files against these schemas before execution.

#### 4. Environment Management
- Load environment variables from `.env.runtime` at container startup.

#### 5. Execution
- Provide a unified entrypoint script (`entrypoint_conformance.sh`) to manage model selection and execution.
- Expose RAS model runner as `/usr/local/bin/run-ras-model`.

#### 6. Dependencies
- Install required system libraries: `wget`, `unzip`, `libxrender1`, `libxtst6`, `libxi6`, `libfreetype6`, `libgfortran5`, `libfontconfig1`.

### Example Usage
```bash
docker run --rm -v $(pwd):/data conformance-reference /usr/local/bin/entrypoint_conformance.sh --model hms --config /data/hms_config.json
docker run --rm -v $(pwd):/data conformance-reference /usr/local/bin/entrypoint_conformance.sh --model ras --config /data/ras_config.json
```