## 📚 Reference

This reference implementation provides a containerized environment for running HEC-RAS models on Linux.

### Container Details

- **Base Image**: `registry.access.redhat.com/ubi8/ubi:8.5`
- **Prod Image**: `ffrd_base`
- **Installed Tools**: `wget`, `unzip`, `jq`
- **HEC-RAS Binaries**: Downloaded and extracted from the official USACE site.
- **File Structure**:
  - `/ras/libs`: HEC-RAS libraries
  - `/ras/v61`: HEC-RAS executables
  - `/sim`: Working directory for simulation files and results

### Usage

#### Run a HEC-RAS Model

```bash
docker run --platform linux/amd64 --rm -v ./data:/mnt $IMAGE "$(cat examples/ras-unsteady-payload-FS.json)"
```

This assumes the required model data is mounted at /data locally (relative to the Dockerfile),  running the HEC-RAS model with files described in the `ras-unsteady-payload-FS.json` example. Please note properties will need to be updated.

### Entrypoint

The default entrypoint is:

```dockerfile
ENTRYPOINT ["/entrypoint.sh"]
```

which will validate the input against the schema before running other processes.

### Source Files

- `Dockerfile`
- `entrypoint.sh`
- `run_unsteady.py`

- HEC-RAS binaries and libraries (downloaded during build)

See the Dockerfile for installation and setup details.
