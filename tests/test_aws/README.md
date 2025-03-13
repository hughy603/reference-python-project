# AWS Mocking Tests

This directory contains tests for AWS service interactions using the moto library.

## Overview

The tests in this directory demonstrate how to mock AWS services for unit testing without making
actual API calls to AWS. This approach offers several advantages:

1. **Fast** - Tests run quickly without network calls
1. **Offline** - Tests work without internet access
1. **Consistent** - Tests produce deterministic results
1. **Safe** - No risk of modifying actual AWS resources or incurring costs

## Test Files

- `test_aws_mocking_example.py` - Basic examples of mocking S3, DynamoDB, SQS, and SSM
- `test_aws_mocking_enhanced.py` - Advanced examples covering more AWS services and complex
  scenarios
- `test_aws_secrets_rotation.py` - Tests specifically for AWS Secrets Manager rotation
- `test_aws.py` - General AWS service integration tests

## Using moto for AWS Mocking

Moto provides decorators and context managers for mocking AWS services. Here are patterns you can
follow:

### Decorator Pattern

```python
from moto import mock_s3

@mock_s3
def test_s3_operations():
    # Create a boto3 client or resource
    s3 = boto3.client('s3', region_name='us-east-1')

    # Perform operations against the mocked service
    s3.create_bucket(Bucket='test-bucket')

    # Test assertions
    response = s3.list_buckets()
    assert 'test-bucket' in [b['Name'] for b in response['Buckets']]
```

### Context Manager Pattern

```python
def test_multiple_aws_services():
    with mock_s3(), mock_dynamodb():
        # S3 operations
        s3 = boto3.client('s3', region_name='us-east-1')
        s3.create_bucket(Bucket='test-bucket')

        # DynamoDB operations
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(...)

        # Test assertions...
```

### Fixture Pattern

```python
@pytest.fixture
def aws_resources():
    with mock_s3(), mock_sqs():
        # Set up resources
        s3_client = boto3.client('s3', region_name='us-east-1')
        bucket_name = 'test-bucket'
        s3_client.create_bucket(Bucket=bucket_name)

        sqs = boto3.resource('sqs', region_name='us-east-1')
        queue = sqs.create_queue(QueueName='test-queue')

        # Yield the resources
        yield {
            's3': s3_client,
            'bucket': bucket_name,
            'queue': queue
        }

def test_with_fixture(aws_resources):
    # Use the mocked resources
    aws_resources['s3'].put_object(
        Bucket=aws_resources['bucket'],
        Key='test.txt',
        Body='test content'
    )

    # Test assertions...
```

## Best Practices

1. **Always specify region_name** - Include `region_name='us-east-1'` when creating
   clients/resources
1. **Explicitly create resources** - Create all AWS resources your test needs (buckets, tables,
   etc.)
1. **Test error cases** - Use `pytest.raises` to verify correct error handling
1. **Use fixtures for complex setups** - Create pytest fixtures for reusable environments
1. **Understand moto limitations** - Some AWS features may not be fully supported

## Supported AWS Services

Moto supports mocking many AWS services including:

- S3
- DynamoDB
- SQS
- SNS
- Lambda
- IAM
- CloudWatch
- EventBridge
- Step Functions
- Secrets Manager
- SSM Parameter Store
- SES
- KMS
- and many more

Check the [moto documentation](https://github.com/spulec/moto) for the complete list and
implementation details.

## Additional Documentation

- [Moto GitHub Repository](https://github.com/spulec/moto)
- [AWS SDK for Python (Boto3)](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
- [pytest Documentation](https://docs.pytest.org/)
