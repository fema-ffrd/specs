# HEC-HMS Simulation

## 📐 Standard

### Purpose
To provide a reproducible, containerized environment for running HEC-HMS hydrologic models and custom compute workflows.

### Scope
This standard applies to all workflows requiring:

- Automated execution of HEC-HMS models.
- Use of custom Java compute modules with HEC-HMS.
- Containerization for portability and consistency.

### Guidelines
1. **Containerization**: All HEC-HMS binaries, libraries, and custom compute modules must be packaged in a container image.
2. **Automation**: Model execution should be performed via a shell script (`run_hms.sh`).
3. **Reproducibility**: The container must provide all dependencies for running HEC-HMS and custom Java modules.
4. **File Organization**: Simulation files and results should be placed in `/data` or `/app`.
5. **Documentation**: Usage instructions and example commands must be provided.

### Best Practices
- Use official sources for HEC-HMS binaries.
- Include all required system libraries and dependencies.
- Log model execution steps for traceability.