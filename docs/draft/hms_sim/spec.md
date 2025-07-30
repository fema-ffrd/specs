## 📝 Specification

### Overview
This specification describes requirements for a containerized environment to run HEC-HMS models and custom compute modules.

### Requirements

#### 1. Container Base
- Use `gradle:7.3.1-jdk17` for building Java modules.
- Use `python:3.11-slim` for the production runtime.

#### 2. HEC-HMS Installation
- Download HEC-HMS Linux distribution from the official USACE website.
- Extract and install all required binaries and libraries.

#### 3. Custom Compute Module
- Build a custom Java module (`hms-compute.jar`) using Gradle.
- Place the jar in `/HEC-HMS-4.11/lib`.

#### 4. File Structure
- HEC-HMS libraries: `/HEC-HMS-4.11/lib`
- HEC-HMS executables: `/HEC-HMS-4.11`
- Sample data: `/data`
- Working directory: `/app`

#### 5. Execution
- Provide a shell script (`run_hms.sh`) to automate model execution.
- Set the container entrypoint to `/app/run_hms.sh`.

#### 6. Dependencies
- Install required system libraries: `libxrender1`, `libxtst6`, `libxi6`, `libfreetype6`, `libgfortran5`, `libfontconfig1`, `jq`, `unzip`.

#### 7. Schema
- Include a JSON schema (`hms_schema.json`) for validating model configuration files.

### Example Usage
```bash
docker run --rm -v $(pwd):/data hms-reference /app/run_hms.sh
```
This command runs the model using files mounted in `/data`.