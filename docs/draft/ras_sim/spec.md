## 📝 Specification

### Overview

This specification describes requirements for a containerized environment to run HEC-RAS models on Linux.

### Requirements

#### 1. Container Base

- Use `registry.access.redhat.com/ubi8/ubi:8.5` as the base image.

#### 2. HEC-RAS Installation

- Download HEC-RAS Linux distribution from the official USACE website.
- Unzip and install all required libraries and binaries.

#### 3. File Structure

- Place HEC-RAS libraries in `/ras/libs`.
- Place HEC-RAS executables in `/ras/v61`.
- Create `/sim` directory for simulation files and results.

#### 4. Execution

- Provide a shell script (`run-model.sh`) to automate model execution.
- Set the container entrypoint to `/sim/run-model.sh`.

#### 5. Dependencies

- Install `jq` for potential JSON processing.
- Ensure all required system libraries are present.

### Example Usage

```bash
docker run --rm -v $(pwd):/sim ras-reference
```

This command runs the model using files mounted in `/sim`.
