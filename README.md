# specs
FEMA FFRD Specifications. IN PROGRESS.

https://fema-ffrd.github.io/specs/

## Setup

### Dev Container Setup (Optional)
1. Open this repository in VS Code
2. When prompted, click "Reopen in Container" or use the Command Palette (Ctrl+Shift+P) and select "Dev Containers: Reopen in Container"
3. The container will automatically set up the environment and install dependencies

#### What Gets Installed

The setup includes:

- **Base**: Debian 12 (bookworm) container
- **Docker**: Docker-outside-of-Docker for running k3s
- **kubectl**: Kubernetes CLI
- **argo**: Argo Workflows CLI v3.7.0
- **k3s**: Lightweight Kubernetes cluster
- **Argo Workflows**: v3.7.0 installed in the cluster

```
┌─────────────────────────────────────-┐
│             DevContainer             │
│  ┌─────────────┐  ┌───────────────┐  │
│  │    argo     │  │    kubectl    │  │
│  │     CLI     │  │      CLI      │  │
│  └─────────────┘  └───────────────┘  │
│                                      │
│  ┌─────────────────────────────────┐ │
│  │          Docker Host            │ │
│  │  ┌─────────────────────────────┐│ │
│  │  │      k3s Container          ││ │
│  │  │  ┌─────────────────────────┐││ │
│  │  │  │   Argo Workflows        │││ │
│  │  │  └─────────────────────────┘││ │
│  │  └─────────────────────────────┘│ │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────-┘
```

#### Useful Commands

Once setup is complete, you can use these commands:

```bash
# Validate workflow files
argo lint reference/orchestration/argo/reference.yaml

# Submit workflow files
argo submit reference/orchestration/argo/reference.yaml

# Watch the workflow execution
argo submit --watch reference/orchestration/argo/reference.yaml

# List all workflows
argo list

# View logs for a specific workflow
argo logs <workflow-name>
```

#### Useful Links

- Explore the [reference workflow](./reference/orchestration/argo/reference.yaml)
- Read the [Argo Workflows documentation](https://argo-workflows.readthedocs.io/)

### Documentation Setup
1. Create a Python virtual environment.
```
$ python -m venv venv-specs
$ source ./venv-specs/bin/activate
(venv-specs) $
```
2. Install project dependencies.
```
(venv-specs) $ pip install .
```
3. Run the local `mkdocs` server.
```
(venv-specs) $ mkdocs serve
```