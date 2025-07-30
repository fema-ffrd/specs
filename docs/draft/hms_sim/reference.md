## 📚 Reference

This reference implementation provides a containerized environment for running HEC-HMS models and custom compute modules.

### Container Details

- **Build Stage**: Uses `gradle:7.3.1-jdk17` to build custom Java modules.
- **Production Stage**: Uses `python:3.11-slim` and installs required system libraries.
- **HEC-HMS Binaries**: Downloaded and extracted from the official USACE site.
- **Custom Compute Module**: Built as `hms-compute.jar` and placed in `/HEC-HMS-4.11/lib`.
- **Sample Data**: Unzipped to `/data` for testing and demonstration.

### Usage

#### Run a HEC-HMS Model
```bash
docker run --rm -v $(pwd):/data hms-reference /app/run_hms.sh
```
This will execute `/app/run_hms.sh` inside the container, running the HEC-HMS model with files in `/data`.

### Entrypoint
The default entrypoint is:
```dockerfile
ENTRYPOINT ["/app/run_hms.sh"]
```

### Source Files
- `Dockerfile`
- `run_hms.sh`
- `hms_schema.json`
- Custom Java sources (`src/`)
- Gradle build files (`build.gradle`, `gradlew`)
- HEC-HMS binaries and libraries (downloaded during build)

See the Dockerfile for installation and setup details.