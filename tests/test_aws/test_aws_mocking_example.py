"""
Example tests demonstrating how to mock AWS services using moto for testing.

This module shows various techniques for mocking AWS services in tests to
avoid making actual AWS API calls during testing, which makes tests:
1. Faster (no network calls)
2. Independent (no external dependencies)
3. Consistent (tests work offline)
4. Safe (won't accidentally modify real resources)
"""

import json

import boto3
import pytest
from moto import mock_dynamodb, mock_s3, mock_sqs, mock_ssm


class TestS3Mocking:
    """Examples of mocking AWS S3 service."""

    @mock_s3
    def test_create_bucket_and_put_object(self):
        """Test creating an S3 bucket and adding an object."""
        # Create a connection to S3
        s3_client = boto3.client("s3", region_name="us-east-1")

        # Create the bucket
        bucket_name = "test-bucket"
        s3_client.create_bucket(Bucket=bucket_name)

        # Verify the bucket was created
        response = s3_client.list_buckets()
        buckets = [bucket["Name"] for bucket in response["Buckets"]]
        assert bucket_name in buckets

        # Put an object in the bucket
        object_key = "test-object.json"
        object_data = {"test_key": "test_value"}
        s3_client.put_object(Bucket=bucket_name, Key=object_key, Body=json.dumps(object_data))

        # Get the object and verify its contents
        response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        content = json.loads(response["Body"].read().decode("utf-8"))
        assert content == object_data

    @mock_s3
    def test_s3_bucket_versioning(self):
        """Test S3 bucket versioning functionality."""
        # Create a connection to S3
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_resource = boto3.resource("s3", region_name="us-east-1")

        # Create the bucket
        bucket_name = "versioned-bucket"
        s3_client.create_bucket(Bucket=bucket_name)

        # Enable versioning
        s3_client.put_bucket_versioning(
            Bucket=bucket_name, VersioningConfiguration={"Status": "Enabled"}
        )

        # Verify versioning is enabled
        response = s3_client.get_bucket_versioning(Bucket=bucket_name)
        assert response["Status"] == "Enabled"

        # Upload multiple versions of the same file
        object_key = "data.txt"

        # First version
        response1 = s3_client.put_object(Bucket=bucket_name, Key=object_key, Body="Version 1")
        version_id1 = response1["VersionId"]

        # Second version
        response2 = s3_client.put_object(Bucket=bucket_name, Key=object_key, Body="Version 2")
        version_id2 = response2["VersionId"]

        # Get the latest version (should be version 2)
        latest = s3_client.get_object(Bucket=bucket_name, Key=object_key)
        assert latest["Body"].read().decode("utf-8") == "Version 2"

        # Get version 1 specifically
        v1 = s3_client.get_object(Bucket=bucket_name, Key=object_key, VersionId=version_id1)
        assert v1["Body"].read().decode("utf-8") == "Version 1"


class TestDynamoDBMocking:
    """Examples of mocking AWS DynamoDB service."""

    @mock_dynamodb
    def test_create_table_and_put_item(self):
        """Test creating a DynamoDB table and adding an item."""
        # Create a connection to DynamoDB
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        # Create the table
        table_name = "test-table"
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        # Verify the table was created
        assert table.table_status == "ACTIVE"

        # Put an item in the table
        item = {"id": "test-id", "name": "test-name", "age": 30, "data": {"nested": "value"}}
        table.put_item(Item=item)

        # Get the item and verify its contents
        response = table.get_item(Key={"id": "test-id"})
        assert response["Item"] == item

    @mock_dynamodb
    def test_dynamodb_queries_and_scans(self):
        """Test DynamoDB queries and scans."""
        # Create a connection to DynamoDB
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        # Create a table with a Global Secondary Index
        table_name = "users-table"
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "user_id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "email", "AttributeType": "S"},
                {"AttributeName": "status", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "email-index",
                    "KeySchema": [{"AttributeName": "email", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                },
                {
                    "IndexName": "status-index",
                    "KeySchema": [{"AttributeName": "status", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                },
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        # Add items to the table
        users = [
            {
                "user_id": "user1",
                "email": "user1@example.com",
                "status": "active",
                "name": "User One",
            },
            {
                "user_id": "user2",
                "email": "user2@example.com",
                "status": "active",
                "name": "User Two",
            },
            {
                "user_id": "user3",
                "email": "user3@example.com",
                "status": "inactive",
                "name": "User Three",
            },
            {
                "user_id": "user4",
                "email": "user4@example.com",
                "status": "active",
                "name": "User Four",
            },
            {
                "user_id": "user5",
                "email": "user5@example.com",
                "status": "inactive",
                "name": "User Five",
            },
        ]

        for user in users:
            table.put_item(Item=user)

        # Test a query on the primary key
        response = table.query(
            KeyConditionExpression="user_id = :user_id",
            ExpressionAttributeValues={":user_id": "user1"},
        )
        assert len(response["Items"]) == 1
        assert response["Items"][0]["name"] == "User One"

        # Test a query on a GSI
        table_client = boto3.client("dynamodb", region_name="us-east-1")
        response = table_client.query(
            TableName=table_name,
            IndexName="status-index",
            KeyConditionExpression="#status = :status",
            ExpressionAttributeNames={"#status": "status"},
            ExpressionAttributeValues={":status": {"S": "active"}},
        )
        assert len(response["Items"]) == 3  # Should find 3 active users

        # Test a scan with a filter
        response = table.scan(
            FilterExpression="contains(email, :email_domain)",
            ExpressionAttributeValues={":email_domain": "example.com"},
        )
        assert len(response["Items"]) == 5  # All users have example.com emails


class TestSQSMocking:
    """Examples of mocking AWS SQS service."""

    @mock_sqs
    def test_create_queue_and_send_message(self):
        """Test creating an SQS queue and sending a message."""
        # Create a connection to SQS
        sqs = boto3.resource("sqs", region_name="us-east-1")

        # Create the queue
        queue_name = "test-queue"
        queue = sqs.create_queue(QueueName=queue_name)

        # Get the queue URL
        queue_url = queue.url

        # Send a message to the queue
        message_body = "Test message body"
        response = queue.send_message(MessageBody=message_body)

        # Verify the message was sent
        assert "MessageId" in response

        # Receive the message
        messages = queue.receive_messages(MaxNumberOfMessages=1)

        # Verify the message body
        assert len(messages) == 1
        assert messages[0].body == message_body

    @mock_sqs
    def test_sqs_batch_operations(self):
        """Test SQS batch send and receive operations."""
        # Create a connection to SQS
        sqs_client = boto3.client("sqs", region_name="us-east-1")

        # Create the queue
        queue_name = "batch-queue"
        response = sqs_client.create_queue(QueueName=queue_name)
        queue_url = response["QueueUrl"]

        # Send messages in batch
        messages = [
            {"Id": "msg1", "MessageBody": "Message 1"},
            {"Id": "msg2", "MessageBody": "Message 2"},
            {"Id": "msg3", "MessageBody": "Message 3"},
            {"Id": "msg4", "MessageBody": "Message 4"},
            {"Id": "msg5", "MessageBody": "Message 5"},
        ]

        response = sqs_client.send_message_batch(QueueUrl=queue_url, Entries=messages)

        # Verify all messages were sent successfully
        assert len(response["Successful"]) == 5

        # Receive messages in batch
        response = sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=10)

        # Verify all messages were received
        assert len(response["Messages"]) == 5


class TestSSMMocking:
    """Examples of mocking AWS SSM Parameter Store service."""

    @mock_ssm
    def test_put_and_get_parameter(self):
        """Test putting and getting SSM parameters."""
        # Create a connection to SSM
        ssm_client = boto3.client("ssm", region_name="us-east-1")

        # Put a string parameter
        param_name = "/test/string-param"
        param_value = "test-value"
        ssm_client.put_parameter(Name=param_name, Value=param_value, Type="String")

        # Put a secure string parameter
        secure_param_name = "/test/secure-param"
        secure_param_value = "secure-value"
        ssm_client.put_parameter(
            Name=secure_param_name,
            Value=secure_param_value,
            Type="SecureString",
            KeyId="alias/aws/ssm",
        )

        # Get the string parameter
        response = ssm_client.get_parameter(Name=param_name)
        assert response["Parameter"]["Value"] == param_value

        # Get the secure string parameter without decryption
        response = ssm_client.get_parameter(Name=secure_param_name, WithDecryption=False)
        # Note: Moto doesn't actually encrypt parameters, so this
        # doesn't behave exactly like AWS in this case
        assert response["Parameter"]["Value"] == secure_param_value

    @mock_ssm
    def test_get_parameters_by_path(self):
        """Test getting parameters by path prefix."""
        # Create a connection to SSM
        ssm_client = boto3.client("ssm", region_name="us-east-1")

        # Create a hierarchy of parameters
        parameters = [
            {"Name": "/app/dev/db/host", "Value": "dev-db.example.com", "Type": "String"},
            {"Name": "/app/dev/db/port", "Value": "3306", "Type": "String"},
            {"Name": "/app/dev/db/username", "Value": "devuser", "Type": "String"},
            {
                "Name": "/app/dev/db/password",
                "Value": "devpass",
                "Type": "SecureString",
                "KeyId": "alias/aws/ssm",
            },
            {"Name": "/app/prod/db/host", "Value": "prod-db.example.com", "Type": "String"},
            {"Name": "/app/prod/db/port", "Value": "3306", "Type": "String"},
            {"Name": "/app/prod/db/username", "Value": "produser", "Type": "String"},
            {
                "Name": "/app/prod/db/password",
                "Value": "prodpass",
                "Type": "SecureString",
                "KeyId": "alias/aws/ssm",
            },
        ]

        for param in parameters:
            ssm_client.put_parameter(
                Name=param["Name"],
                Value=param["Value"],
                Type=param["Type"],
                KeyId=param.get("KeyId", ""),
            )

        # Get all dev parameters
        response = ssm_client.get_parameters_by_path(Path="/app/dev", Recursive=True)

        assert len(response["Parameters"]) == 4
        # Convert list to dict for easier testing
        param_dict = {p["Name"]: p["Value"] for p in response["Parameters"]}
        assert param_dict["/app/dev/db/host"] == "dev-db.example.com"
        assert param_dict["/app/dev/db/username"] == "devuser"

        # Get only the prod db parameters
        response = ssm_client.get_parameters_by_path(Path="/app/prod/db", Recursive=True)

        assert len(response["Parameters"]) == 4
        param_dict = {p["Name"]: p["Value"] for p in response["Parameters"]}
        assert param_dict["/app/prod/db/host"] == "prod-db.example.com"


class TestCombiningMockDecorators:
    """Examples of combining multiple mock decorators."""

    @mock_s3
    @mock_sqs
    def test_s3_trigger_sqs(self):
        """Test simulating an S3 event triggering an SQS message."""
        # Create S3 bucket and SQS queue
        s3_client = boto3.client("s3", region_name="us-east-1")
        sqs_client = boto3.client("sqs", region_name="us-east-1")

        bucket_name = "source-bucket"
        queue_name = "notification-queue"

        # Create resources
        s3_client.create_bucket(Bucket=bucket_name)
        response = sqs_client.create_queue(QueueName=queue_name)
        queue_url = response["QueueUrl"]

        # Upload file to S3
        s3_client.put_object(Bucket=bucket_name, Key="test-file.txt", Body="Test content")

        # In a real system, S3 would trigger a Lambda or send an event.
        # Here we'll simulate by manually constructing and sending the event.
        s3_event = {
            "Records": [
                {
                    "eventVersion": "2.1",
                    "eventSource": "aws:s3",
                    "awsRegion": "us-east-1",
                    "eventTime": "2023-01-01T12:00:00.000Z",
                    "eventName": "ObjectCreated:Put",
                    "s3": {"bucket": {"name": bucket_name}, "object": {"key": "test-file.txt"}},
                }
            ]
        }

        # Send notification to SQS
        sqs_client.send_message(QueueUrl=queue_url, MessageBody=json.dumps(s3_event))

        # Receive and process the message
        response = sqs_client.receive_message(QueueUrl=queue_url, MaxNumberOfMessages=1)

        # Verify message
        assert "Messages" in response
        assert len(response["Messages"]) == 1

        message_body = json.loads(response["Messages"][0]["Body"])
        assert message_body["Records"][0]["eventSource"] == "aws:s3"
        assert message_body["Records"][0]["s3"]["bucket"]["name"] == bucket_name
        assert message_body["Records"][0]["s3"]["object"]["key"] == "test-file.txt"


# Example of using a fixture to set up mock AWS resources
@pytest.fixture
def mock_aws_resources():
    """Fixture that sets up common mock AWS resources for tests."""
    with mock_s3(), mock_dynamodb(), mock_sqs():
        # Set up S3
        s3_client = boto3.client("s3", region_name="us-east-1")
        bucket_name = "test-bucket"
        s3_client.create_bucket(Bucket=bucket_name)

        # Set up DynamoDB
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table_name = "test-table"
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        # Set up SQS
        sqs = boto3.resource("sqs", region_name="us-east-1")
        queue_name = "test-queue"
        queue = sqs.create_queue(QueueName=queue_name)

        # Return the resources
        yield {
            "s3_client": s3_client,
            "bucket_name": bucket_name,
            "dynamodb_table": table,
            "sqs_queue": queue,
        }


def test_using_fixture(mock_aws_resources):
    """Test using the mock AWS resources fixture."""
    # Use S3
    s3_client = mock_aws_resources["s3_client"]
    bucket_name = mock_aws_resources["bucket_name"]

    s3_client.put_object(Bucket=bucket_name, Key="test-key", Body="test-data")

    response = s3_client.get_object(Bucket=bucket_name, Key="test-key")
    assert response["Body"].read().decode("utf-8") == "test-data"

    # Use DynamoDB
    table = mock_aws_resources["dynamodb_table"]

    table.put_item(Item={"id": "item1", "data": "value1"})

    response = table.get_item(Key={"id": "item1"})
    assert response["Item"]["data"] == "value1"

    # Use SQS
    queue = mock_aws_resources["sqs_queue"]

    queue.send_message(MessageBody="test message")

    messages = queue.receive_messages()
    assert len(messages) == 1
    assert messages[0].body == "test message"
