"""
Example unit tests demonstrating mocking multiple AWS services together.

This module shows how to effectively use Moto's mock_aws decorator
to test code that interacts with multiple AWS services in an integrated manner.
"""

import json
import uuid
from datetime import datetime
from typing import Any

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws


class DataLakeProcessor:
    """Example processor that works with both S3 and DynamoDB."""

    def __init__(self, s3_bucket: str, dynamodb_table: str, region: str = "us-east-1") -> None:
        """Initialize processor with bucket and table names."""
        self.s3_bucket = s3_bucket
        self.dynamodb_table = dynamodb_table
        self.region = region

        self.s3_client = boto3.client("s3", region_name=region)
        self.dynamodb = boto3.resource("dynamodb", region_name=region)
        self.table = self.dynamodb.Table(dynamodb_table)

    def process_data(self, data: dict[str, Any], dataset_id: str) -> bool:
        """
        Process and store data in S3 and record metadata in DynamoDB.

        Args:
            data: The data to process and store
            dataset_id: Unique identifier for this dataset

        Returns:
            True if successful, False otherwise
        """
        try:
            # Generate filename and metadata
            timestamp = datetime.utcnow().isoformat()
            file_key = f"datasets/{dataset_id}/{timestamp}.json"
            record_id = str(uuid.uuid4())

            # Store data in S3
            self.s3_client.put_object(
                Bucket=self.s3_bucket,
                Key=file_key,
                Body=json.dumps(data),
                ContentType="application/json",
            )

            # Store metadata in DynamoDB
            self.table.put_item(
                Item={
                    "record_id": record_id,
                    "dataset_id": dataset_id,
                    "timestamp": timestamp,
                    "file_location": f"s3://{self.s3_bucket}/{file_key}",
                    "record_count": len(data) if isinstance(data, list) else 1,
                    "status": "PROCESSED",
                }
            )

            return True
        except (ClientError, Exception):
            return False

    def get_dataset_records(self, dataset_id: str) -> list[dict[str, Any]]:
        """
        Retrieve all records for a dataset.

        Args:
            dataset_id: The dataset ID to query for

        Returns:
            List of dataset records
        """
        try:
            response = self.table.query(
                KeyConditionExpression="dataset_id = :dataset_id",
                ExpressionAttributeValues={":dataset_id": dataset_id},
            )
            return response.get("Items", [])
        except ClientError:
            return []

    def retrieve_dataset_file(self, file_path: str) -> dict[str, Any] | None:
        """
        Retrieve a dataset file from S3.

        Args:
            file_path: The S3 path in format s3://bucket/key

        Returns:
            The file contents as a dictionary or None on failure
        """
        try:
            # Parse S3 path
            if file_path.startswith("s3://"):
                parts = file_path[5:].split("/", 1)
                bucket = parts[0]
                key = parts[1] if len(parts) > 1 else ""
            else:
                return None

            # Get file from S3
            response = self.s3_client.get_object(Bucket=bucket, Key=key)
            content = response["Body"].read().decode("utf-8")
            return json.loads(content)
        except (ClientError, json.JSONDecodeError):
            return None


class TestDataLakeProcessor:
    """Tests for DataLakeProcessor with multiple AWS services."""

    @mock_aws
    def test_data_processing_flow(self) -> None:
        """Test the complete data processing flow."""
        # Arrange
        # Create S3 bucket
        s3_client = boto3.client("s3", region_name="us-east-1")
        bucket_name = "test-data-lake"
        s3_client.create_bucket(Bucket=bucket_name)

        # Create DynamoDB table
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table_name = "test-records"

        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "record_id", "KeyType": "HASH"},  # Partition key
                {"AttributeName": "dataset_id", "KeyType": "RANGE"},  # Sort key
            ],
            AttributeDefinitions=[
                {"AttributeName": "record_id", "AttributeType": "S"},
                {"AttributeName": "dataset_id", "AttributeType": "S"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        # Create a secondary index for retrieving by dataset_id
        table.update(
            AttributeDefinitions=[{"AttributeName": "dataset_id", "AttributeType": "S"}],
            GlobalSecondaryIndexUpdates=[
                {
                    "Create": {
                        "IndexName": "dataset_id-index",
                        "KeySchema": [{"AttributeName": "dataset_id", "KeyType": "HASH"}],
                        "Projection": {"ProjectionType": "ALL"},
                        "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                    }
                }
            ],
        )

        # Initialize processor
        processor = DataLakeProcessor(bucket_name, table_name)

        # Test data
        dataset_id = "test-dataset-001"
        test_data = [
            {"id": 1, "name": "Item 1", "value": 100},
            {"id": 2, "name": "Item 2", "value": 200},
            {"id": 3, "name": "Item 3", "value": 300},
        ]

        # Act - Process data
        result = processor.process_data(test_data, dataset_id)

        # Assert
        assert result is True

        # Verify data was stored in DynamoDB
        records = processor.get_dataset_records(dataset_id)
        assert len(records) == 1
        record = records[0]
        assert record["dataset_id"] == dataset_id
        assert record["record_count"] == 3
        assert record["status"] == "PROCESSED"

        # Verify we can retrieve the file
        file_path = record["file_location"]
        assert file_path.startswith(f"s3://{bucket_name}/datasets/{dataset_id}")

        file_content = processor.retrieve_dataset_file(file_path)
        assert file_content == test_data


class TestWithFixtures:
    """Test with fixtures to create and tear down resources."""

    @pytest.fixture()
    def aws_clients(self) -> Any:
        """Set up AWS clients for testing."""
        with mock_aws():
            # Create S3 bucket
            s3 = boto3.client("s3", region_name="us-east-1")
            s3.create_bucket(Bucket="test-bucket")

            # Create DynamoDB table
            dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
            table = dynamodb.create_table(
                TableName="test-table",
                KeySchema=[
                    {"AttributeName": "record_id", "KeyType": "HASH"},
                    {"AttributeName": "dataset_id", "KeyType": "RANGE"},
                ],
                AttributeDefinitions=[
                    {"AttributeName": "record_id", "AttributeType": "S"},
                    {"AttributeName": "dataset_id", "AttributeType": "S"},
                ],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )

            # Wait for the table to be created
            table.meta.client.get_waiter("table_exists").wait(TableName="test-table")

            yield {"s3": s3, "dynamodb_table": table}

    def test_combined_services(self, aws_clients: dict[str, Any]) -> None:
        """Test multiple AWS services together."""
        # Use the clients from the fixture
        s3 = aws_clients["s3"]
        table = aws_clients["dynamodb_table"]

        # Test data
        test_key = "test/file.json"
        test_data = {"key": "value"}
        record_id = str(uuid.uuid4())
        dataset_id = "test-dataset"

        # Upload data to S3
        s3.put_object(Bucket="test-bucket", Key=test_key, Body=json.dumps(test_data))

        # Store metadata in DynamoDB
        table.put_item(
            Item={
                "record_id": record_id,
                "dataset_id": dataset_id,
                "file_path": f"s3://test-bucket/{test_key}",
            }
        )

        # Retrieve data
        s3_response = s3.get_object(Bucket="test-bucket", Key=test_key)
        s3_content = json.loads(s3_response["Body"].read().decode("utf-8"))

        dynamo_response = table.get_item(Key={"record_id": record_id, "dataset_id": dataset_id})

        # Assert
        assert s3_content == test_data
        assert "Item" in dynamo_response
        assert dynamo_response["Item"]["file_path"] == f"s3://test-bucket/{test_key}"


def test_multiple_services_simple() -> None:
    """Simple test showing multiple services with mock_aws."""
    with mock_aws():
        # Create S3 bucket
        s3 = boto3.client("s3", region_name="us-east-1")
        s3.create_bucket(Bucket="my-test-bucket")

        # Upload a file to S3
        s3.put_object(Bucket="my-test-bucket", Key="test.json", Body=json.dumps({"test": "data"}))

        # Create DynamoDB table
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table = dynamodb.create_table(
            TableName="my-test-table",
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        # Store an item
        table.put_item(Item={"id": "test-id", "s3_ref": "s3://my-test-bucket/test.json"})

        # Retrieve the item
        response = table.get_item(Key={"id": "test-id"})

        # Assert
        assert response["Item"]["s3_ref"] == "s3://my-test-bucket/test.json"

        # Get S3 file referenced in the item
        s3_key = response["Item"]["s3_ref"].replace("s3://my-test-bucket/", "")
        s3_response = s3.get_object(Bucket="my-test-bucket", Key=s3_key)
        content = json.loads(s3_response["Body"].read().decode("utf-8"))

        assert content == {"test": "data"}
