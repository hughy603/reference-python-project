"""
Comprehensive Testing Examples for AWS Services

This file demonstrates testing strategies for various AWS services:
1. Unit testing with mocks (using unittest.mock and moto)
2. Integration testing with LocalStack
3. Snapshot testing for infrastructure
4. Pytest fixtures for AWS resource management

Usage:
    # Run all tests
    pytest examples/aws_services_testing.py -v

    # Run only unit tests
    pytest examples/aws_services_testing.py::TestS3Operations -v

    # Run tests with coverage
    pytest examples/aws_services_testing.py --cov=src
"""

import json
import os
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

import boto3

# For mocking AWS services
import moto
import pytest

# Import the code we'll be testing
from src.enterprise_data_engineering.common_utils.aws_helpers import (
    DynamoDBOperations,
    S3Operations,
)

#################################################
# Unit Tests with Mocks
#################################################


@moto.mock_s3
class TestS3Operations(unittest.TestCase):
    """Example unit tests for S3 operations using moto library."""

    def setUp(self):
        """Set up test environment."""
        # Create a mock S3 bucket
        self.bucket_name = "test-bucket"
        self.s3_client = boto3.client("s3", region_name="us-east-1")
        self.s3_client.create_bucket(Bucket=self.bucket_name)

        # Initialize the S3 operations object with our test bucket
        self.s3_ops = S3Operations(bucket_name=self.bucket_name)

        # Create some test files
        self.test_data = {"key1": "value1", "key2": "value2"}
        self.s3_client.put_object(
            Bucket=self.bucket_name, Key="test_data.json", Body=json.dumps(self.test_data)
        )

    def test_upload_json(self):
        """Test uploading JSON data to S3."""
        # Prepare test data
        data = {"test": "data", "timestamp": str(datetime.now())}
        key = "test_upload.json"

        # Upload to S3
        result = self.s3_ops.upload_json(data, key)

        # Verify upload was successful
        self.assertTrue(result)

        # Verify file exists in S3
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
        content = json.loads(response["Body"].read().decode("utf-8"))

        # Verify content matches what we uploaded
        self.assertEqual(content, data)

    def test_download_json(self):
        """Test downloading JSON data from S3."""
        # Download existing file
        data = self.s3_ops.download_json("test_data.json")

        # Verify content matches what we expect
        self.assertEqual(data, self.test_data)

    def test_list_objects(self):
        """Test listing objects in an S3 bucket."""
        # Upload additional files
        self.s3_client.put_object(
            Bucket=self.bucket_name, Key="folder1/test1.json", Body=json.dumps({"file": "test1"})
        )
        self.s3_client.put_object(
            Bucket=self.bucket_name, Key="folder1/test2.json", Body=json.dumps({"file": "test2"})
        )

        # List objects in folder1
        objects = self.s3_ops.list_objects(prefix="folder1/")

        # Verify we get the expected objects
        self.assertEqual(len(objects), 2)
        self.assertTrue("folder1/test1.json" in objects)
        self.assertTrue("folder1/test2.json" in objects)

    def test_file_exists(self):
        """Test checking if a file exists in S3."""
        # Check for existing file
        exists = self.s3_ops.file_exists("test_data.json")
        self.assertTrue(exists)

        # Check for non-existent file
        exists = self.s3_ops.file_exists("does_not_exist.json")
        self.assertFalse(exists)


@moto.mock_dynamodb
class TestDynamoDBOperations(unittest.TestCase):
    """Example unit tests for DynamoDB operations using moto library."""

    def setUp(self):
        """Set up test environment."""
        # Create a mock DynamoDB table
        self.table_name = "test-table"
        self.dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        # Create the table with a simple key schema
        self.table = self.dynamodb.create_table(
            TableName=self.table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        # Wait for table to be created
        self.table.meta.client.get_waiter("table_exists").wait(TableName=self.table_name)

        # Initialize DynamoDB operations
        self.dynamo_ops = DynamoDBOperations(table_name=self.table_name)

        # Add test data
        self.test_items = [
            {"id": "item1", "data": "value1", "number": 42},
            {"id": "item2", "data": "value2", "number": 43},
            {"id": "item3", "data": "value3", "number": 44},
        ]

        for item in self.test_items:
            self.table.put_item(Item=item)

    def test_put_item(self):
        """Test putting an item in DynamoDB."""
        # Create a new item
        new_item = {"id": "item4", "data": "value4", "number": 45}

        # Put the item
        result = self.dynamo_ops.put_item(new_item)

        # Verify the put was successful
        self.assertTrue(result)

        # Verify the item exists in the table
        response = self.table.get_item(Key={"id": "item4"})
        self.assertTrue("Item" in response)
        self.assertEqual(response["Item"], new_item)

    def test_get_item(self):
        """Test getting an item from DynamoDB."""
        # Get an existing item
        item = self.dynamo_ops.get_item({"id": "item1"})

        # Verify we got the expected item
        self.assertEqual(item["id"], "item1")
        self.assertEqual(item["data"], "value1")
        self.assertEqual(item["number"], 42)

    def test_query_items(self):
        """Test querying items from DynamoDB."""
        # This is a simplified example as actual querying would require a GSI
        # For this test, we'll scan with a filter instead
        items = self.dynamo_ops.scan_items(
            filter_expression="number > :n", expression_values={":n": 43}
        )

        # Verify we got the expected items
        self.assertEqual(len(items), 2)
        self.assertTrue(any(item["id"] == "item2" for item in items))
        self.assertTrue(any(item["id"] == "item3" for item in items))

    def test_update_item(self):
        """Test updating an item in DynamoDB."""
        # Update an existing item
        update_result = self.dynamo_ops.update_item(
            key={"id": "item1"},
            update_expression="SET #data = :new_data, #num = :new_num",
            expression_names={"#data": "data", "#num": "number"},
            expression_values={":new_data": "updated_value", ":new_num": 99},
        )

        # Verify the update was successful
        self.assertTrue(update_result)

        # Get the updated item
        updated_item = self.dynamo_ops.get_item({"id": "item1"})

        # Verify the item was updated correctly
        self.assertEqual(updated_item["data"], "updated_value")
        self.assertEqual(updated_item["number"], 99)


#################################################
# Integration Tests with LocalStack
#################################################


class TestIntegrationWithLocalstack:
    """
    Integration tests using LocalStack.

    These tests require LocalStack to be running locally:
    docker run -d -p 4566:4566 -p 4571:4571 localstack/localstack
    """

    @pytest.fixture(scope="class")
    def s3_client(self):
        """Create an S3 client connected to LocalStack."""
        return boto3.client(
            "s3",
            endpoint_url="http://localhost:4566",
            region_name="us-east-1",
            aws_access_key_id="test",
            aws_secret_access_key="test",
        )

    @pytest.fixture(scope="class")
    def dynamodb_client(self):
        """Create a DynamoDB client connected to LocalStack."""
        return boto3.client(
            "dynamodb",
            endpoint_url="http://localhost:4566",
            region_name="us-east-1",
            aws_access_key_id="test",
            aws_secret_access_key="test",
        )

    @pytest.fixture(scope="class")
    def lambda_client(self):
        """Create a Lambda client connected to LocalStack."""
        return boto3.client(
            "lambda",
            endpoint_url="http://localhost:4566",
            region_name="us-east-1",
            aws_access_key_id="test",
            aws_secret_access_key="test",
        )

    @pytest.fixture(scope="class")
    def s3_test_bucket(self, s3_client):
        """Create a test S3 bucket in LocalStack."""
        bucket_name = "integration-test-bucket"

        try:
            s3_client.head_bucket(Bucket=bucket_name)
        except:
            s3_client.create_bucket(Bucket=bucket_name)

        return bucket_name

    @pytest.fixture(scope="class")
    def dynamodb_test_table(self, dynamodb_client):
        """Create a test DynamoDB table in LocalStack."""
        table_name = "integration-test-table"

        try:
            dynamodb_client.describe_table(TableName=table_name)
        except:
            dynamodb_client.create_table(
                TableName=table_name,
                KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
                AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
                ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
            )

        return table_name

    def test_s3_integration(self, s3_client, s3_test_bucket):
        """Test S3 operations with LocalStack."""
        # Initialize S3 operations with our test bucket
        s3_ops = S3Operations(bucket_name=s3_test_bucket, endpoint_url="http://localhost:4566")

        # Upload a test file
        test_data = {"test": "integration"}
        key = "integration_test.json"

        s3_ops.upload_json(test_data, key)

        # Verify the file exists
        assert s3_ops.file_exists(key)

        # Download and verify content
        downloaded_data = s3_ops.download_json(key)
        assert downloaded_data == test_data

    def test_dynamodb_integration(self, dynamodb_client, dynamodb_test_table):
        """Test DynamoDB operations with LocalStack."""
        # Initialize DynamoDB operations with our test table
        dynamo_ops = DynamoDBOperations(
            table_name=dynamodb_test_table, endpoint_url="http://localhost:4566"
        )

        # Put a test item
        test_item = {"id": "int-test", "data": "integration-test"}
        dynamo_ops.put_item(test_item)

        # Get and verify the item
        retrieved_item = dynamo_ops.get_item({"id": "int-test"})
        assert retrieved_item["id"] == "int-test"
        assert retrieved_item["data"] == "integration-test"


#################################################
# Snapshot Testing for Infrastructure
#################################################


@pytest.mark.snapshot
class TestInfrastructureSnapshots:
    """Example of snapshot testing for infrastructure configurations."""

    @pytest.fixture
    def cloudformation_template(self):
        """Load a CloudFormation template for testing."""
        template_path = os.path.join(
            os.path.dirname(__file__), "../infrastructure/cloudformation/s3-bucket.yml"
        )

        if os.path.exists(template_path):
            with open(template_path) as f:
                return f.read()
        else:
            # Return a sample template for testing if the actual one doesn't exist
            return """
            AWSTemplateFormatVersion: '2010-09-09'
            Description: S3 Bucket CloudFormation Template

            Resources:
              DataBucket:
                Type: AWS::S3::Bucket
                Properties:
                  BucketName: !Sub "${AWS::StackName}-data-bucket"
                  VersioningConfiguration:
                    Status: Enabled
                  BucketEncryption:
                    ServerSideEncryptionConfiguration:
                      - ServerSideEncryptionByDefault:
                          SSEAlgorithm: AES256
            """

    def test_cloudformation_template_snapshot(self, cloudformation_template, snapshot):
        """Test that CloudFormation template matches snapshot."""
        # This is a pseudo-implementation as we don't have the actual snapshot library
        # In a real project, you would use a snapshot testing library like syrupy

        # Parse the template to normalize it
        try:
            import yaml

            template_dict = yaml.safe_load(cloudformation_template)

            # Check specific properties instead of the whole template
            resources = template_dict.get("Resources", {})

            # Verify expected resources exist
            assert "DataBucket" in resources

            # Verify specific properties
            data_bucket = resources["DataBucket"]
            assert data_bucket["Type"] == "AWS::S3::Bucket"
            assert "BucketEncryption" in data_bucket["Properties"]

            # In real snapshot testing, you would do:
            # assert template_dict == snapshot
        except ImportError:
            # If yaml module is not available, do a simpler check
            assert "AWS::S3::Bucket" in cloudformation_template
            assert "BucketEncryption" in cloudformation_template


#################################################
# Testing Lambda Functions
#################################################


class TestLambdaFunctions:
    """Example tests for AWS Lambda functions."""

    def setup_method(self):
        """Set up for each test method."""
        # Mock the AWS Lambda environment variables
        os.environ["AWS_REGION"] = "us-east-1"
        os.environ["OUTPUT_BUCKET"] = "test-output-bucket"
        os.environ["DYNAMODB_TABLE"] = "test-table"

    @patch("boto3.client")
    def test_lambda_handler_success(self, mock_boto_client):
        """Test the Lambda handler function with a successful event."""
        from examples.lambda_functions.data_processor.lambda_function import lambda_handler

        # Setup mock S3 client
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        # Create a test event
        test_event = {
            "Records": [
                {"s3": {"bucket": {"name": "test-bucket"}, "object": {"key": "test/data.json"}}}
            ]
        }

        # Mock S3 get_object response
        mock_s3.get_object.return_value = {
            "Body": MagicMock(
                read=MagicMock(return_value=json.dumps({"id": "test", "value": 42}).encode("utf-8"))
            )
        }

        # Call the lambda handler
        response = lambda_handler(test_event, {})

        # Verify the response
        assert response["statusCode"] == 200
        assert "processed" in response

        # Verify S3 interactions
        mock_s3.get_object.assert_called_once_with(Bucket="test-bucket", Key="test/data.json")

        # Verify put_object was called with processed data
        assert mock_s3.put_object.called

    @patch("boto3.client")
    def test_lambda_handler_error(self, mock_boto_client):
        """Test the Lambda handler function with an error case."""
        from examples.lambda_functions.data_processor.lambda_function import lambda_handler

        # Setup mock S3 client that raises an exception
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.get_object.side_effect = Exception("Test error")

        # Create a test event
        test_event = {
            "Records": [
                {"s3": {"bucket": {"name": "test-bucket"}, "object": {"key": "test/data.json"}}}
            ]
        }

        # Call the lambda handler
        response = lambda_handler(test_event, {})

        # Verify the error response
        assert response["statusCode"] == 500
        assert "error" in response


if __name__ == "__main__":
    unittest.main()
