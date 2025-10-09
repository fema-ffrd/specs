# Orchestration Workflow Compiler

Compiles JSON workflow definitions with validation. Currently supports compilation to Argo workflow YAML.

## Schema

See `schemas/workflow.json` for the workflow schema definition.

## Usage

### Build

```bash
# Build from the reference directory (not from orchestration/argo)
cd reference
docker build -t workflow-compiler -f orchestration/argo/Dockerfile .
```

### Run from stdin

```bash
cat examples/hms-ras-workflow.json | docker run -i workflow-compiler
```

### Run with JSON argument

```bash
docker run -i workflow-compiler '{"workflow_name": "test", ...}'
```

### Save output

```bash
cat examples/hms-ras-workflow.json | docker run -i workflow-compiler > workflow.yaml
```
