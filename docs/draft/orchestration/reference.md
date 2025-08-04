## 📚 Reference

### Argo Workflows Implementation

This reference implementation demonstrates how Argo Workflows can satisfy the FFRD orchestration requirements. Argo Workflows is provided as one example of a compliant orchestration system, but other systems may be used as long as they meet the specification requirements.

#### Implementation Overview

The reference implementation uses Argo Workflows running on Kubernetes to provide:

- DAG-based workflow execution with explicit task dependencies
- Container execution with shared volume access
- Parallel task execution with parameterization
- Shared volume management for data exchange between tasks
- Basic logging and monitoring capabilities

#### Example Workflow Structure

The following example demonstrates a basic FFRD workflow pattern with parallel processing and data collection:

```yaml
# This is a simplified example showing the orchestration pattern
# Full FFRD workflows would use FFRD-compliant containers and configurations

apiVersion: argoproj.io/v1alpha1
kind: Workflow
metadata:
  generateName: dag-example-
spec:
  entrypoint: main
  volumeClaimTemplates: # Create a shared volume for the workflow
  - metadata:
      name: workdir
    spec:
      accessModes: [ "ReadWriteOnce" ]
      resources:
        requests:
          storage: 1Gi
  templates:
  - name: main
    dag:
      tasks:
      - name: generate-number
        template: generate-number
      - name: process-numbers
        dependencies: [generate-number]
        template: process-numbers
      - name: sum-results
        dependencies: [process-numbers]
        template: sum-results

  - name: generate-number
    container:
      image: alpine:3.18
      command: [sh, -c]
      args: ["echo 5 > /work/number.txt"]
      volumeMounts:
      - name: workdir
        mountPath: /work

  - name: process-numbers
    parallelism: 2 # Run two steps at a time
    steps:
    - - name: process-number
        template: process-number
        withItems: # Iterate over this list of numbers
        - 1
        - 2
        - 3
        - 4
        arguments:
          parameters:
          - name: item
            value: "{{ '{{item}}' }}" # Pass the item from the list to the process-number template

  - name: process-number
    inputs:
      parameters:
      - name: item
    container:
      image: alpine:3.18
      command: [sh, -c]
      args:
      - |
        num=$(cat /work/number.txt)
        result=$((num + {{ '{{inputs.parameters.item}}' }}))
        echo $result > /work/result-{{ '{{inputs.parameters.item}}' }}.txt
      volumeMounts:
      - name: workdir
        mountPath: /work

  - name: sum-results
    container:
      image: alpine:3.18
      command: [sh, -c]
      args:
      - |
        sum=0
        for file in /work/result-*.txt; do
          sum=$((sum + $(cat $file)))
        done
        echo "Total sum: $sum"
      volumeMounts:
      - name: workdir
        mountPath: /work
```

#### Key Implementation Features

##### DAG Structure

- Uses Argo's DAG template to define explicit task dependencies (`dependencies: [generate-number]`)
- Demonstrates parallel execution through steps with `withItems` parameterization
- Shows sequential workflow phases (generate → process → collect)

##### Container Execution

- Executes standard containers (Alpine Linux) as a pattern for FFRD containers
- Demonstrates passing command line arguments to containers
- Shows volume mounting for data access across all tasks

##### Data Sharing

- Uses persistent volume claims (`volumeClaimTemplates`) for shared storage
- Consistent volume mounting (`/work`) across all workflow tasks
- Demonstrates file-based data exchange between workflow steps

##### Parameterization

- Shows parameter passing with `withItems` for parallel task execution
- Demonstrates template parameter usage with `inputs.parameters.item`
- Illustrates how to iterate over lists to create multiple parallel tasks

#### Deployment Requirements

##### Infrastructure

- Kubernetes cluster
- Argo Workflows
- Container runtime (Docker, containerd, or CRI-O)
- Persistent storage provisioner

##### Configuration

- Argo Workflows controller installation
- RBAC configuration for workflow execution
- Storage class configuration for volume provisioning
- Container registry access credentials

#### Usage Examples

##### Validate Workflow

```bash
# Validate the workflow definition
argo lint reference.yaml
```

##### Submit Workflow

```bash
# Submit the workflow to Argo
argo submit reference.yaml
```

##### Monitor Execution

```bash
# List all workflows
argo list

# Watch workflow execution (use actual workflow name from list)
argo get dag-example-abc123

# View workflow logs
argo logs dag-example-abc123
```

##### Access Results

```bash
# View workflow status and results
argo get dag-example-abc123
```

#### Alternative Implementations

While this reference uses Argo Workflows, other orchestration systems can satisfy FFRD requirements:

- **Apache Airflow**: Python-based DAG orchestration with extensive integrations
- **Prefect**: Modern workflow orchestration with dynamic DAG generation
- **Kubeflow Pipelines**: ML-focused orchestration with container-native execution
- **Temporal**: Durable execution framework with strong consistency guarantees
- **Custom Solutions**: Purpose-built orchestration systems meeting FFRD specifications

The key requirement is that any chosen system must satisfy all requirements outlined in the FFRD orchestration specification, regardless of the underlying implementation technology.

This reference implementation serves as a concrete example of how to satisfy FFRD orchestration requirements.
