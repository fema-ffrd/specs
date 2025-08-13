# Logging

## 📐 Standard

### Overview

This specification describes logging requirements for all FFRD containers, ensuring that logs are consistent,
useful, and compatible with modern workflows.

## 📝 Specification

#### 1. Re-emit `stdout`/`stderr`

Containers must re-emit messages logged to `stdout`/`stderr` by the main process.

In some cases, the container may filter or aggregate superflous logs to `stdout`/`stderr`.
For example, the HEC-RAS 6.x Unsteady process is extremely "chatty", indicating its progress by
echoing each individual timestep to `stdout`/`stderr`. Logs from a HEC-RAS 6.x container will be more legible if messages
from the Unsteady process are filtered to increments of, e.g., 1%, 5%, or 10% progress.

#### 2. Tail and echo relevant log files

Containers must tail and re-emit messages logged to log files by the main process.

For example, in HEC-HMS v4.x, logs are saved in `*.log` and `*.out` files within the directory of a project.
A HEC-HMS v4.x container should echo messages saved to these files while a HEC-HMS model runs.

#### 3. Log message formatting

Containers must write log messages in a format which includes:

1. ISO timestamp
1. Level (e.g., `ERROR`, `WARNING`, `INFO`)
1. Path to the log file where the log message was written (not applicable to messages written to `stdout`/`stderr`)
1. The original log message

Example:

```
2025-08-04 20:12:32,958 - INFO - /app/HEC-HMS-4.12/samples/tenk/tenk.log - NOTE 10181:  Opened control specifications "Jan 96" at time 04Aug2025, 20:12:32.
2025-08-04 20:12:32,958 - INFO - /app/HEC-HMS-4.12/samples/tenk/tenk.log - NOTE 10616:  Data type "PER-AVER" is usually used for time intervals of 24 hours or longer.  Gage "TENK".
2025-08-04 20:12:32,959 - WARNING - /app/HEC-HMS-4.12/samples/tenk/tenk.log - WARNING 40503:  Missing precipitation set to zero for 129 of 129 grid cells at 18Jan1996, 17:00 for gridded subbasin "86".
2025-08-04 20:12:32,959 - WARNING - /app/HEC-HMS-4.12/samples/tenk/tenk.log - WARNING 40503:  Missing precipitation set to zero for 84 of 84 grid cells at 18Jan1996, 17:00 for gridded subbasin "85".
2025-08-04 20:12:32,959 - WARNING - /app/HEC-HMS-4.12/samples/tenk/tenk.log - WARNING 40503:  Missing precipitation set to zero for 78 of 78 grid cells at 18Jan1996, 17:00 for gridded subbasin "113".
2025-08-04 20:12:32,958 - INFO - /app/HEC-HMS-4.12/samples/tenk/Jan_96_storm.log - grid cells at 20Jan1996, 02:00 for gridded subbasin "127".
```

#### 4. JSON log message formatting

Containers must provide an option to emit log messages as JSON. JSON-formatted logs are valuable in modern logging
pipelines because they can be easily parsed, indexed, and queried by log aggregation systems. This enables filtering
by timestamp, severity level, model component, and file source, allowing teams to detect issues faster and build
dashboards or alerting mechanisms.

JSON log messages must abide by the following schema:

```json
{% include "../../reference/logs/logs-schema.json" %}
```

Example:

```json
{"timestamp": "2025-08-04T20:20:40.141323", "level": "WARNING", "source": "/app/HEC-HMS-4.12/samples/tenk/Jan_96_storm.log", "message": "WARNING 40503:  Missing precipitation set to zero for 86 of 86 grid cells at 20Jan1996, 22:00 for gridded subbasin \"127\"."}
{"timestamp": "2025-08-04T20:20:40.141370", "level": "INFO", "source": "/app/HEC-HMS-4.12/samples/tenk/Jan_96_storm.log", "message": "NOTE 15302:  Finished computing simulation run \"Jan 96 storm\" at time 04Aug2025, 20:20:39."}
{"timestamp": "2025-08-04T20:20:40.141409", "level": "INFO", "source": "/app/HEC-HMS-4.12/samples/tenk/Jan_96_storm.log", "message": "NOTE 15312:  The total runtime for this simulation is 00:01."}
```

#### 5. Return codes

Containers must exit with clear return codes indicating the success or failure of the primary process.
This enables automation and orchestration systems to make informed decisions -- such as whether to retry a failed
job, trigger a downstream task, or alert a human operator.

- `0`: Success
- `1`: Failure
