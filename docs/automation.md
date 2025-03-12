# Automation with Autosys Integration

This guide explains how to use the Reference Python Project with Autosys for job automation and
scheduling.

## Overview

[Autosys](https://www.broadcom.com/products/mainframe/workload-automation/autosys) is an enterprise
job scheduling and workload automation system. This project provides tools and utilities to make
Python applications work seamlessly with Autosys scheduling.

## Key Features

Our Autosys integration provides:

1. **Standardized CLI Interface** - Commands designed for automation environments
1. **Structured Logging** - JSON logging with Autosys job IDs and execution tracking
1. **Exit Code Management** - Clear, consistent exit codes for job control
1. **Status File Generation** - Creates status files for job monitoring
1. **JIL File Generation** - Utilities to programmatically create Autosys job definitions
1. **Dependency Handling** - Tools for checking and managing job dependencies

## Getting Started

### Prerequisites

To use the Autosys integration:

1. Ensure you have Python 3.11, 3.12, or 3.13 installed
1. Install this package with `pip install reference-python-project`
1. Set up environment variables for Autosys (can be done with `rpp setup`)

### Environment Variables

The following environment variables are recognized:

| Variable               | Description               | Example                        |
| ---------------------- | ------------------------- | ------------------------------ |
| `AUTOSYS_JOB_ID`       | Current Autosys job ID    | `ETL_DAILY_JOB_001`            |
| `AUTOSYS_EXECUTION_ID` | Current execution ID      | `exec_20231101_001`            |
| `AUTOSYS_STATUS_FILE`  | Path to write status info | `/path/to/status/job_001.json` |
| `AUTOSYS_LOG_FILE`     | Path to write logs        | `/path/to/logs/job_001.log`    |
| `AUTOSYS_LOG_LEVEL`    | Logging level             | `INFO`                         |

## CLI Commands for Automation

### Running Jobs

```bash
# Run a job with parameters
rpp automation run-job etl_process --param "source=s3://bucket/data" --param "target=processed" --output-format json

# Run a job with specific status file
rpp automation run-job etl_process --status-file /path/to/status/etl_status.json
```

### Checking Dependencies

```bash
# Check if dependencies are met
rpp automation check-dependencies data_validation_job

# Check with JSON output
rpp automation check-dependencies data_validation_job --output-format json
```

### Reporting Status

```bash
# Check status of a job
rpp automation report-status ETL_DAILY_JOB_001 --status-file /path/to/status.json
```

## Creating Autosys JIL Definitions

Our `autosys` utility module provides functions to programmatically create Autosys JIL files:

```python
from reference_python_project.utils.autosys import create_jil_definition, JobType

# Create a simple command job
jil = create_jil_definition(
    job_name="data_process_001",
    command="python /path/to/script.py --param value",
    machine="data-proc-server",
    description="Process daily data files",
    start_times=["20:00"],
    std_out_file="/path/to/logs/job.stdout",
    std_err_file="/path/to/logs/job.stderr"
)

# Write to a file
with open("job_definition.jil", "w") as f:
    f.write(jil)
```

### Creating Job Boxes and Chains

```python
from reference_python_project.utils.autosys import create_job_box, create_dependency_chain

# Create a job box
box_jil = create_job_box(
    box_name="ETL_PROCESS_BOX",
    job_names=["extract_job", "transform_job", "load_job"],
    start_times=["01:00"],
    machine="etl-server"
)

# Create a dependency chain
chain_jil = create_dependency_chain(
    job_names=["validate_data", "process_data", "export_results"],
    command="python /path/to/script.py",
    machine="data-server"
)
```

### Creating Python Jobs

```python
from reference_python_project.utils.autosys import generate_python_job

# Create a Python job with virtual environment
python_jil = generate_python_job(
    job_name="ml_prediction_job",
    script_path="/path/to/predict.py",
    arguments=["--model", "production", "--batch-size", "1000"],
    virtual_env="/path/to/venv",
    machine="ml-server",
    start_times=["06:00"],
    max_run_alarm=120  # 2 hours max runtime
)
```

## Best Practices

### 1. Use Non-Interactive Mode

Always design jobs to run in non-interactive mode with defaults for required parameters. Any CLI
command used with Autosys should never require user input.

```bash
# Good: Provides defaults or environment variable fallbacks
rpp automation run-job process_data --non-interactive

# Bad: Might prompt for input
rpp process_data
```

### 2. Handle Exit Codes Properly

Ensure your scripts use appropriate exit codes that Autosys can understand:

- `0`: Success
- `1`: Configuration error
- `2`: Runtime error
- `3`: Dependency error
- `4`: Permission error
- `5`: Network error
- etc.

### 3. Use Structured Logging

Enable JSON format logging for better integration with log aggregation systems:

```bash
rpp automation run-job data_job --output-format json --log-file /path/to/logs/job.log
```

### 4. Create Status Files

Always create status files for job monitoring:

```bash
export AUTOSYS_STATUS_FILE=/path/to/status/job_001.json
rpp automation run-job data_process
```

### 5. Check Dependencies Before Running

Use the dependency check feature to verify prerequisites before starting jobs:

```bash
rpp automation check-dependencies data_transform
if [ $? -eq 0 ]; then
    rpp automation run-job data_transform
fi
```

## Troubleshooting

### Common Issues

1. **Job Fails with Exit Code 1**

   - This typically indicates a configuration error
   - Check environment variables and command line parameters

1. **Status File Not Created**

   - Verify the directory exists and has write permissions
   - Check if AUTOSYS_STATUS_FILE is set correctly

1. **Missing Job Information in Logs**

   - Ensure AUTOSYS_JOB_ID and AUTOSYS_EXECUTION_ID are set
   - Verify logging is configured correctly with automation_mode=True

### Debugging Jobs

For debugging Autosys jobs:

1. Run with verbose logging:

   ```bash
   rpp automation run-job problem_job --verbose
   ```

1. Check the status file for detailed error information:

   ```bash
   rpp automation report-status problem_job --status-file /path/to/status.json
   ```

## Examples

### Complete ETL Workflow Example

```python
from reference_python_project.utils.autosys import create_job_box, create_daily_job

# Create main ETL box
etl_box = create_job_box(
    box_name="DAILY_ETL_BOX",
    job_names=[
        "extract_data",
        "validate_data",
        "transform_data",
        "load_data",
        "verify_results"
    ],
    start_times=["01:00"],
    calendar="WORKDAYS",
    description="Daily ETL Process",
    machine="etl-server",
    owner="etl_user"
)

# Create extract job
extract_job = create_daily_job(
    job_name="extract_data",
    command="python /path/to/extract.py --source prod --output /data/raw",
    start_time="01:15",
    days_of_week=["mon", "tue", "wed", "thu", "fri"],
    box_name="DAILY_ETL_BOX",
    max_run_alarm=30,
    std_out_file="/logs/extract.log"
)

# Write to JIL file
with open("etl_workflow.jil", "w") as f:
    f.write("\n".join(etl_box))
    f.write("\n")
    f.write(extract_job)
    # Add additional jobs...
```

## Additional Resources

- [Autosys Job Information Language (JIL) Reference](https://techdocs.broadcom.com/us/en/ca-enterprise-software/intelligent-automation/workload-automation-ae-and-workload-control-center/11-3-6-SP8/reference/ae-job-information-language.html)
- [Workload Automation Best Practices](https://www.broadcom.com/products/mainframe/workload-automation/autosys)
