#!/usr/bin/env python3
"""
AWS Glue Job Local Runner

This script allows developers to run AWS Glue ETL jobs locally on Windows without Docker.
It provides a simulated Glue environment for testing and debugging ETL code.

Usage:
    python run_glue_job_local.py --job-file path/to/glue_job.py
                                --job-args '{"--JOB_NAME":"test_job","--input_path":"s3://bucket/input"}'
                                --mock-s3
"""

import argparse
import json
import logging
import os
import sys
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("glue-local")


def setup_glue_context(use_mock: bool = False) -> tuple:
    """
    Sets up a local Glue context using PySpark.

    Args:
        use_mock: Whether to use moto to mock AWS services

    Returns:
        Tuple of (spark, glueContext, job)
    """
    from pyspark.conf import SparkConf
    from pyspark.context import SparkContext

    try:
        # Try to import from AWS Glue libraries
        from awsglue.context import GlueContext
        from awsglue.job import Job
        from awsglue.utils import getResolvedOptions
    except ImportError:
        logger.error(
            "AWS Glue libraries not found. Make sure you've installed AWS Glue Libraries:"
            "\npython -m pip install 'git+https://github.com/awslabs/aws-glue-libs.git@v4.0' --no-deps"
        )
        sys.exit(1)

    # Set up mocks if requested
    if use_mock:
        try:
            import boto3
            from moto import mock_glue, mock_iam, mock_s3

            # Start moto servers
            mock_s3_server = mock_s3()
            mock_glue_server = mock_glue()
            mock_iam_server = mock_iam()

            mock_s3_server.start()
            mock_glue_server.start()
            mock_iam_server.start()

            # Create test bucket if using mock
            s3 = boto3.client("s3", region_name="us-east-1")
            s3.create_bucket(Bucket="test-bucket")

            logger.info("Started mock AWS services (S3, Glue, IAM)")
        except ImportError:
            logger.warning("moto library not found, skipping mock AWS services")

    # Create a Spark configuration for local execution
    conf = SparkConf()
    conf.set("spark.app.name", "GlueLocalJob")
    conf.set("spark.master", "local[*]")
    conf.set("spark.sql.warehouse.dir", "file://" + os.path.join(os.getcwd(), "spark-warehouse"))
    conf.set(
        "spark.hadoop.fs.s3a.aws.credentials.provider",
        "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
    )
    conf.set("spark.sql.session.timeZone", "UTC")
    conf.set("spark.sql.sources.partitionOverwriteMode", "dynamic")

    # Create Spark context
    sc = SparkContext(conf=conf)

    # Suppress verbose Spark logging
    sc.setLogLevel("WARN")

    # Create Glue context
    glue_context = GlueContext(sc)
    spark = glue_context.spark_session

    # Create a job with a random job name
    job_name = f"local-job-{uuid.uuid4().hex[:8]}"
    job = Job(glue_context)
    job.init(job_name, {})

    logger.info(f"Created local Glue job environment with job name: {job_name}")

    return spark, glue_context, job


def parse_job_arguments(args_json: str) -> list[str]:
    """
    Parse JSON job arguments into sys.argv format.

    Args:
        args_json: JSON string of Glue job arguments

    Returns:
        List of arguments in sys.argv format
    """
    try:
        job_args = json.loads(args_json)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse job arguments JSON: {args_json}")
        return ["--JOB_NAME", "local-job"]

    # Convert to sys.argv format (flattened key-value pairs)
    argv_args = []
    for key, value in job_args.items():
        # Ensure keys start with --
        formatted_key = key if key.startswith("--") else f"--{key}"
        argv_args.extend([formatted_key, str(value)])

    return argv_args


def run_glue_job(job_file: str, job_args: list[str], use_mock: bool = False) -> None:
    """
    Run a Glue job locally by importing and running the script.

    Args:
        job_file: Path to the Glue job Python file
        job_args: List of job arguments in sys.argv format
        use_mock: Whether to use moto to mock AWS services
    """
    # Save original sys.argv and restore later
    original_argv = sys.argv.copy()
    original_path = sys.path.copy()

    try:
        # Set up job arguments
        sys.argv = ["glue_job.py"] + job_args

        # Add script directory to path for imports
        script_dir = os.path.dirname(os.path.abspath(job_file))
        if script_dir not in sys.path:
            sys.path.insert(0, script_dir)

        # Set up Glue environment variables
        os.environ["GLUE_JOB"] = "true"
        os.environ["IS_LOCAL"] = "true"

        # Setup the Glue context before importing
        setup_glue_context(use_mock)

        # Import and run the job file
        logger.info(f"Running Glue job: {job_file}")
        logger.info(f"With arguments: {job_args}")

        # Execute the Glue script
        with open(job_file) as f:
            job_code = f.read()
            exec(job_code, globals())

        logger.info("Glue job completed successfully")
    except Exception as e:
        logger.error(f"Error running Glue job: {e!s}")
        import traceback

        logger.error(traceback.format_exc())
        raise
    finally:
        # Clean up
        sys.argv = original_argv
        sys.path = original_path
        if use_mock:
            try:
                from moto import mock_glue, mock_iam, mock_s3

                mock_s3().stop()
                mock_glue().stop()
                mock_iam().stop()
                logger.info("Stopped mock AWS services")
            except ImportError:
                pass


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(description="AWS Glue Local Job Runner")
    parser.add_argument("--job-file", "-f", required=True, help="Glue job script file path")
    parser.add_argument(
        "--job-args",
        "-a",
        default="{}",
        help='JSON string of job arguments (e.g. \'{"--JOB_NAME":"test_job"}\')',
    )
    parser.add_argument("--mock-s3", "-m", action="store_true", help="Use moto to mock S3")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")

    return parser.parse_args()


def main() -> None:
    """Main execution function"""
    args = parse_arguments()

    # Set log level
    if args.verbose:
        logger.setLevel(logging.DEBUG)

    # Parse job arguments
    job_args = parse_job_arguments(args.job_args)

    # Run the job
    run_glue_job(args.job_file, job_args, args.mock_s3)


if __name__ == "__main__":
    main()
