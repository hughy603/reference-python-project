"""
Example AWS Glue PySpark Job

This is a sample Glue ETL job that demonstrates reading data from S3,
transforming it with PySpark, and writing results back to S3.

To run locally (without Docker):
    python scripts/run_glue_job_local.py \
        --job-file examples/glue_job_example.py \
        --job-args '{"--JOB_NAME":"test_job","--input_path":"s3://test-bucket/input","--output_path":"s3://test-bucket/output"}' \
        --mock-s3
"""

import os
import sys

from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from pyspark.sql.functions import col, current_timestamp, when

# Get job parameters
args = getResolvedOptions(sys.argv, ["JOB_NAME", "input_path", "output_path"])

# Initialize Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Log configuration
print(f"Starting job: {args['JOB_NAME']}")
print(f"Input path: {args['input_path']}")
print(f"Output path: {args['output_path']}")

# For local testing with mock S3, create sample data
if "IS_LOCAL" in os.environ:
    # Create sample data
    data = [
        {"id": 1, "name": "Alice", "department": "Engineering", "salary": 85000},
        {"id": 2, "name": "Bob", "department": "Engineering", "salary": 78000},
        {"id": 3, "name": "Charlie", "department": "Marketing", "salary": 72000},
        {"id": 4, "name": "Diana", "department": "Finance", "salary": 96000},
        {"id": 5, "name": "Eve", "department": "Finance", "salary": 105000},
    ]

    # Create DataFrame
    df = spark.createDataFrame(data)

    # Write to input location for testing
    df.write.mode("overwrite").parquet(args["input_path"])
    print("Created sample data in mock S3")

# Read data from S3
try:
    input_df = spark.read.parquet(args["input_path"])
    print(f"Read {input_df.count()} records from input")

    # Show sample data
    input_df.show(5, truncate=False)

    # Perform transformations
    output_df = input_df.withColumn("processed_date", current_timestamp()).withColumn(
        "salary_band",
        when(col("salary") < 80000, "Entry")
        .when(col("salary") < 100000, "Mid")
        .otherwise("Senior"),
    )

    # Write results back to S3
    output_df.write.mode("overwrite").partitionBy("department").parquet(args["output_path"])
    print(f"Wrote {output_df.count()} records to output")

except Exception as e:
    print(f"Error processing data: {e!s}")
    raise

# Complete the job
job.commit()
print("Job completed successfully")
