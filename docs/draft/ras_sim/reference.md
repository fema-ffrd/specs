## 📚 Reference

This reference implementation provides a containerized environment for running HEC-RAS models on Linux.

### Container Details

- **Base Image**: `registry.access.redhat.com/ubi8/ubi:8.5`
- **Installed Tools**: `wget`, `unzip`, `jq`
- **HEC-RAS Binaries**: Downloaded and extracted from the official USACE site.
- **File Structure**:
  - `/ras/libs`: HEC-RAS libraries
  - `/ras/v61`: HEC-RAS executables
  - `/sim`: Working directory for simulation files and results

### Usage

#### Run a HEC-RAS Model

```bash
docker run --rm -v $(pwd):/sim ras-reference
```

This will execute `/sim/run-model.sh` inside the container, running the HEC-RAS model with files in `/sim`.

### Entrypoint

The default entrypoint is:

```dockerfile
ENTRYPOINT ["/sim/run-model.sh"]
```

### Source Files

- `Dockerfile`
- `run-model.sh`
- HEC-RAS binaries and libraries (downloaded during build)

See the Dockerfile for installation and setup details.
