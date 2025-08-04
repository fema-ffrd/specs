## 📚 Reference

This reference implementation provides a containerized environment for running both HEC-HMS and HEC-RAS models with schema validation and environment management.

## Container Details

- **Upstream Artifacts**: Uses `hms-ffrd` and `ras-ffrd` containers to source model binaries, libraries, and scripts.
- **Base Image**: Uses `ffrd_base` for the final runtime environment.
- **Schema Validation**: Includes `hms_schema.json` and `ras_schema.json` for validating model configuration files.
- **Environment Management**: Loads environment variables from `.env.runtime` at startup.
- **Entrypoint**: Uses `/usr/local/bin/entrypoint_conformance.sh` to select and run the appropriate model.

## Usage

### Run HEC-HMS Model

```bash
docker run --rm -v $(pwd):/data conformance-reference /usr/local/bin/entrypoint_conformance.sh --model hms --config /data/hms_config.json
```

### Run HEC-RAS Model

```bash
docker run --rm -v $(pwd):/data conformance-reference /usr/local/bin/entrypoint_conformance.sh --model ras --config /data/ras_config.json
```

## Entrypoint

The default entrypoint is:

```dockerfile
ENTRYPOINT ["/usr/local/bin/entrypoint_conformance.sh"]
```

## Source Files

- `Dockerfile`
- `entrypoint_conformance.sh`
- `run_hms.sh`
- `run-model.sh`
- `hms_schema.json`
- `ras_schema.json`
- `.env.runtime`

See the Dockerfile for installation and setup details.
