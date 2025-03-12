# Enterprise Data Engineering Examples

This directory contains example code and implementations to demonstrate best practices and usage
patterns.

## Contents

- [AWS Lambda Functions](#aws-lambda-functions)
- [AWS Glue ETL Jobs](#aws-glue-etl-jobs)
- [Real-Time Data Processing with Kinesis](#real-time-data-processing-with-kinesis)
- [Comprehensive AWS Service Testing](#comprehensive-aws-service-testing)
- [Quickstart Example](#quickstart-example)

## AWS Lambda Functions

The `lambda_functions/` directory contains example AWS Lambda implementations with both Python and
TypeScript examples. These demonstrations show best practices for:

- Error handling
- Environment configuration
- AWS service integrations
- Local testing without Docker

See [lambda_functions/README.md](lambda_functions/README.md) for details on each example.

## AWS Glue ETL Jobs

The `glue_job_example.py` file demonstrates an AWS Glue PySpark job with the following features:

- Reading data from S3
- Processing with PySpark transformations
- Writing results back to S3 with partitioning
- Local testing capabilities
- Error handling and logging

To run the example locally:

```bash
python scripts/run_glue_job_local.py \
    --job-file examples/glue_job_example.py \
    --job-args '{"--JOB_NAME":"test_job","--input_path":"s3://test-bucket/input","--output_path":"s3://test-bucket/output"}' \
    --mock-s3
```

## Real-Time Data Processing with Kinesis

The `kinesis_streaming_example.py` file demonstrates real-time data processing with AWS Kinesis:

- Data generation and production to Kinesis streams
- Stream consumption with AWS Lambda
- Multi-destination data storage (S3, DynamoDB)
- Alerting and monitoring patterns
- Local testing with LocalStack

To run the producer example:

```bash
python examples/kinesis_streaming_example.py \
    --stream-name test-stream \
    --region us-east-1 \
    --continuous \
    --interval 5
```

For detailed documentation, see the [Kinesis Streaming Guide](../docs/KINESIS_STREAMING.md).

## Comprehensive AWS Service Testing

The `aws_services_testing.py` file provides extensive examples of testing AWS services:

- Unit testing with Moto mock AWS services
- Integration testing with LocalStack
- Snapshot testing for infrastructure templates
- AWS Lambda function testing

The file demonstrates testing patterns for:

- S3 operations
- DynamoDB operations
- Lambda functions
- CloudFormation templates

To run the tests:

```bash
# Run all tests
pytest examples/aws_services_testing.py

# Run specific test class
pytest examples/aws_services_testing.py::TestS3Operations
```

For detailed documentation on testing strategies, see the [Testing Guide](../docs/TESTING.md).

## Quickstart Example

The `quickstart_example.py` provides a simple entry point to understand the core functionality of
this project. It demonstrates:

- Basic AWS client configuration
- Error handling patterns
- Configuration management
- Logging best practices

To run the quickstart:

```bash
python examples/quickstart_example.py
```

## Using These Examples

Each example is designed to be:

1. **Self-contained**: Can be run independently with minimal setup
1. **Well-documented**: Contains inline comments explaining key concepts
1. **Production-ready**: Implements best practices for error handling, logging, and security
1. **Testable**: Includes unit and integration tests

## Next Steps

After exploring these examples, you can:

1. Use them as templates for your own implementations
1. Modify them to fit your specific requirements
1. Integrate them into your existing workflows
1. Check the corresponding documentation for each example in the `docs/` directory
