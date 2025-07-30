# HEC-RAS Simulation

## 📐 Standard

### Purpose
To provide a consistent, reproducible environment for running HEC-RAS models on Linux using containerization.

### Scope
This standard applies to all workflows requiring automated execution of HEC-RAS models, including:

- Preparation of simulation environments.
- Execution of HEC-RAS binaries in a container.
- Use of Red Hat UBI base images for compatibility and security.

### Guidelines
1. **Containerization**: HEC-RAS binaries and required libraries must be packaged in a container image.
2. **Automation**: Model execution should be automated via a shell script (`run-model.sh`).
3. **Reproducibility**: The container must provide all dependencies for running HEC-RAS without manual setup.
4. **File Organization**: Simulation files should be placed in `/sim` and results should be written there.
5. **Documentation**: Usage instructions and example commands must be provided.

### Best Practices
- Use official sources for HEC-RAS binaries.
- Ensure all required libraries are included.
- Log model execution steps for traceability.