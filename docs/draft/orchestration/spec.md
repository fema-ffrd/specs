## 📝 Specification

### Overview
This specification defines the fundamental requirements for orchestration systems used within the FFRD initiative to execute complex flood risk analysis workflows. The system must provide DAG-based workflow execution, FFRD container integration, and essential operational capabilities. This specification does not prescribe specific implementation technologies.

### Requirements

#### 1. Workflow Structure

##### 1.1 Directed Acyclic Graph (DAG) Support
- **Graph Definition**: Workflows MUST be representable as directed acyclic graphs with explicit task dependencies
- **Task Dependencies**: System MUST support expressing dependencies between tasks (e.g., Task B depends on Task A completion)
- **Parallel Execution**: System MUST execute independent tasks concurrently when resources allow
- **Conditional Execution**: System MUST support conditional task execution based on upstream task results or external conditions

##### 1.2 Workflow Definition
- **Declarative Format**: Workflows MUST be defined in a human-readable, version-controllable format
- **Reproducibility**: Identical workflow definitions MUST produce deterministic execution behavior
- **Parameterization**: System MUST support parameterized workflows for different study areas, configurations, and datasets

#### 2. FFRD Container Integration

##### 2.1 Container Execution
- **FFRD Base Image**: System MUST execute containers built on FFRD base image specifications
- **HMS Containers**: System MUST execute HEC-HMS containers with appropriate Java runtime requirements
- **RAS Containers**: System MUST execute HEC-RAS containers with computational dependencies
- **Conformance Containers**: System MUST execute validation and conformance testing containers
- **Plugin Containers**: System MUST execute custom FFRD-compliant analysis containers

##### 2.2 Container Configuration
- **Configuration Files**: System MUST support passing JSON configuration files to containers as specified in FFRD standards
- **Environment Variables**: System MUST support setting required environment variables for FFRD containers
- **Command Line Arguments**: System MUST support passing command line arguments to containers
- **Exit Code Handling**: System MUST properly interpret container exit codes and handle success/failure states

#### 3. Volume Sharing and Data Management

##### 3.1 Shared Storage
- **Inter-task Data Sharing**: System MUST provide mechanisms for tasks to share data through persistent storage
- **Volume Persistence**: System MUST support volumes that persist beyond individual task execution
- **Storage Size Configuration**: System MUST allow specification of storage volume sizes (minimum 1GB, configurable up to hundreds of GB)

##### 3.2 Data Access Patterns
- **Read/Write Access**: System MUST support both read-only and read-write volume access modes
- **Multiple Mount Points**: System MUST support mounting volumes at different paths within containers
- **Data Isolation**: System MUST prevent unauthorized access to data between different workflow executions

#### 4. Resource Allocation

##### 4.1 Compute Resources
- **CPU Allocation**: System MUST support specifying CPU core requirements per task (minimum 0.1 cores, typical 1-8 cores)
- **Memory Allocation**: System MUST support specifying memory requirements per task (minimum 512MB, typical 1GB-32GB)
- **Resource Enforcement**: System MUST enforce specified resource limits to prevent resource contention

##### 4.2 Resource Constraints
- **Resource Isolation**: System MUST isolate resources between concurrent tasks
- **Resource Monitoring**: System MUST track actual resource usage against allocated limits
- **Resource Availability**: System MUST queue tasks when insufficient resources are available

#### 5. Logging and Observability

##### 5.1 Execution Logging
- **Container Logs**: System MUST capture and store all container stdout/stderr output
- **Workflow Progress**: System MUST provide visibility into workflow execution status and task completion
- **Log Association**: System MUST associate logs with specific workflow runs and individual tasks
- **Log Retention**: System MUST retain logs for completed workflows for a configurable period

##### 5.2 Monitoring
- **Task Status**: System MUST report status of workflow tasks (pending, running, completed, failed)
- **Workflow History**: System MUST maintain history of workflow executions

#### 6. Error Handling and Recovery

##### 6.1 Retry Mechanisms
- **Configurable Retry**: System MUST support configurable retry policies for failed tasks
- **Retry Limits**: System MUST support maximum retry attempt limits

##### 6.2 Failure Handling
- **Failure Isolation**: System MUST prevent individual task failures from stopping independent workflow branches
- **Partial Completion**: System MUST support completing successful workflow branches when other branches fail
- **Failure Reporting**: System MUST clearly report which tasks failed and provide failure details
- **Manual Recovery**: System MUST support manual intervention to recover from failures

#### 7. Integration Requirements

##### 7.1 Data Sources
- **S3 Integration**: System MUST support integration with S3-compatible object storage for input/output data
- **File System Access**: System MUST support mounting external file systems for data access
- **Network Access**: System MUST support controlled network access for containers requiring external connectivity

##### 7.2 Operational Integration
- **Workflow Submission**: System MUST provide mechanisms for submitting and executing workflows

#### 8. Security and Access Control

##### 8.1 Access Control
- **Authentication**: System MUST provide authentication mechanisms for workflow access
- **Authorization**: System MUST provide authorization controls for workflow execution
- **Credential Management**: System MUST provide secure mechanisms for handling sensitive data and credentials

### Operational Requirements

#### Performance Expectations
- **Concurrent Workflows**: System MUST support executing multiple independent workflows simultaneously
- **Multi-node Execution**: System MUST support executing workflows across multiple compute nodes

#### Reliability Requirements
- **System Availability**: System MUST provide high availability for workflow execution
- **Data Durability**: System MUST ensure durability of workflow outputs and execution logs
- **Recovery**: System MUST support recovery from system failures without losing workflow progress

#### Compliance Requirements
- **Audit Trail**: System MUST maintain complete audit trails of workflow executions
- **Data Governance**: System MUST support data governance requirements for FFRD data
- **Documentation**: System MUST provide documentation for operational procedures and troubleshooting

### Example Workflow Scenario

A typical FFRD workflow might include:

1. **Data Preparation**: Validate input configuration and download required datasets from S3
2. **Model Execution**: Run HEC-HMS hydrologic models with specified parameters
3. **Post-Processing**: Process model outputs and generate analysis results
4. **Validation**: Run conformance tests on outputs
5. **Data Upload**: Upload results to designated S3 locations

The orchestration system must execute these tasks in the correct dependency order, share data between tasks through persistent volumes, allocate appropriate compute resources, handle any task failures with retries, and provide complete logging and monitoring throughout the process.

This specification provides the essential requirements for FFRD workflow orchestration while allowing flexibility in implementation approach and technology choices.