"""
Example unit tests demonstrating S3 mocking with Moto's latest mock_aws decorator.

This module shows how to effectively use Moto's mock_aws decorator
to test code that interacts with AWS S3.
"""

import json
from io import BytesIO
from typing import Any

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws


class TestS3Operations:
    """Test suite demonstrating S3 operations with moto's mock_aws decorator."""

    @mock_aws
    def test_create_bucket(self) -> None:
        """Test creating an S3 bucket."""
        # Arrange
        s3_client = boto3.client("s3", region_name="us-east-1")
        bucket_name = "test-bucket"

        # Act
        response = s3_client.create_bucket(Bucket=bucket_name)

        # Assert
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

        # Verify bucket exists
        buckets = s3_client.list_buckets()
        assert len(buckets["Buckets"]) == 1
        assert buckets["Buckets"][0]["Name"] == bucket_name

    @mock_aws
    def test_put_and_get_object(self) -> None:
        """Test putting and retrieving an object from S3."""
        # Arrange
        s3_client = boto3.client("s3", region_name="us-east-1")
        bucket_name = "test-bucket"
        key = "test-key"
        test_data = {"key1": "value1", "key2": "value2"}

        # Create bucket
        s3_client.create_bucket(Bucket=bucket_name)

        # Act - Put object
        s3_client.put_object(Bucket=bucket_name, Key=key, Body=json.dumps(test_data))

        # Act - Get object
        response = s3_client.get_object(Bucket=bucket_name, Key=key)
        content = json.loads(response["Body"].read().decode("utf-8"))

        # Assert
        assert content == test_data
        assert response["ResponseMetadata"]["HTTPStatusCode"] == 200

    @mock_aws
    def test_delete_object(self) -> None:
        """Test deleting an object from S3."""
        # Arrange
        s3_client = boto3.client("s3", region_name="us-east-1")
        bucket_name = "test-bucket"
        key = "test-key"

        # Create bucket and object
        s3_client.create_bucket(Bucket=bucket_name)
        s3_client.put_object(Bucket=bucket_name, Key=key, Body="test content")

        # Verify object exists
        objects = s3_client.list_objects_v2(Bucket=bucket_name)
        assert "Contents" in objects
        assert len(objects["Contents"]) == 1

        # Act
        s3_client.delete_object(Bucket=bucket_name, Key=key)

        # Assert
        objects = s3_client.list_objects_v2(Bucket=bucket_name)
        assert "Contents" not in objects  # No objects left

    @mock_aws
    def test_bucket_versioning(self) -> None:
        """Test configuring and retrieving bucket versioning."""
        # Arrange
        s3_client = boto3.client("s3", region_name="us-east-1")
        bucket_name = "versioned-bucket"

        # Create bucket
        s3_client.create_bucket(Bucket=bucket_name)

        # Act - Enable versioning
        s3_client.put_bucket_versioning(
            Bucket=bucket_name, VersioningConfiguration={"Status": "Enabled"}
        )

        # Assert
        response = s3_client.get_bucket_versioning(Bucket=bucket_name)
        assert "Status" in response
        assert response["Status"] == "Enabled"

    @mock_aws
    def test_upload_fileobj(self) -> None:
        """Test uploading a file-like object to S3."""
        # Arrange
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_resource = boto3.resource("s3", region_name="us-east-1")
        bucket_name = "fileobj-bucket"
        key = "test-fileobj"

        # Create file-like object
        test_data = b"This is test data for file upload"
        fileobj = BytesIO(test_data)

        # Create bucket
        s3_client.create_bucket(Bucket=bucket_name)

        # Act
        s3_client.upload_fileobj(fileobj, bucket_name, key)

        # Assert - Using resource interface to demonstrate different approaches
        obj = s3_resource.Object(bucket_name, key)
        content = obj.get()["Body"].read()
        assert content == test_data

    @mock_aws
    def test_presigned_url(self) -> None:
        """Test generating and using a presigned URL."""
        # Arrange
        s3_client = boto3.client("s3", region_name="us-east-1")
        bucket_name = "presigned-bucket"
        key = "presigned-key"

        # Create bucket and object
        s3_client.create_bucket(Bucket=bucket_name)
        s3_client.put_object(Bucket=bucket_name, Key=key, Body="test content")

        # Act - Generate presigned URL
        url = s3_client.generate_presigned_url(
            "get_object", Params={"Bucket": bucket_name, "Key": key}, ExpiresIn=3600
        )

        # Assert URL was generated
        assert url is not None
        assert bucket_name in url
        assert key in url

    @mock_aws
    def test_object_tagging(self) -> None:
        """Test adding and retrieving tags for an S3 object."""
        # Arrange
        s3_client = boto3.client("s3", region_name="us-east-1")
        bucket_name = "tag-bucket"
        key = "tagged-object"
        tags = {"Project": "DataEngineering", "Environment": "Test", "Confidential": "False"}

        # Create bucket and object
        s3_client.create_bucket(Bucket=bucket_name)
        s3_client.put_object(Bucket=bucket_name, Key=key, Body="content")

        # Act - Put tags
        tag_set = [{"Key": k, "Value": v} for k, v in tags.items()]
        s3_client.put_object_tagging(Bucket=bucket_name, Key=key, Tagging={"TagSet": tag_set})

        # Act - Get tags
        response = s3_client.get_object_tagging(Bucket=bucket_name, Key=key)

        # Assert
        assert "TagSet" in response
        retrieved_tags = {tag["Key"]: tag["Value"] for tag in response["TagSet"]}
        assert retrieved_tags == tags

    @mock_aws
    def test_error_handling(self) -> None:
        """Test proper error handling for missing buckets/objects."""
        # Arrange
        s3_client = boto3.client("s3", region_name="us-east-1")
        nonexistent_bucket = "nonexistent-bucket"
        nonexistent_key = "nonexistent-key"

        # Act & Assert - Missing bucket
        with pytest.raises(ClientError) as excinfo:
            s3_client.get_object(Bucket=nonexistent_bucket, Key=nonexistent_key)
        assert "NoSuchBucket" in str(excinfo.value)

        # Create a bucket but try to access a missing object
        s3_client.create_bucket(Bucket="existing-bucket")

        # Act & Assert - Missing object
        with pytest.raises(ClientError) as excinfo:
            s3_client.get_object(Bucket="existing-bucket", Key=nonexistent_key)
        assert "NoSuchKey" in str(excinfo.value)


# Example of a fixture-based approach
class TestS3WithFixtures:
    """Test S3 operations using pytest fixtures with Moto."""

    @pytest.fixture()
    def s3_client(self) -> Any:
        """Create a mocked S3 client."""
        with mock_aws():
            yield boto3.client("s3", region_name="us-east-1")

    @pytest.fixture()
    def test_bucket(self, s3_client: Any) -> str:
        """Create a test bucket for use in tests."""
        bucket_name = "fixture-test-bucket"
        s3_client.create_bucket(Bucket=bucket_name)
        return bucket_name

    def test_list_objects_with_fixture(self, s3_client: Any, test_bucket: str) -> None:
        """Test listing objects using fixtures."""
        # Arrange
        for i in range(3):
            key = f"test-key-{i}"
            s3_client.put_object(Bucket=test_bucket, Key=key, Body=f"content-{i}")

        # Act
        response = s3_client.list_objects_v2(Bucket=test_bucket)

        # Assert
        assert "Contents" in response
        assert len(response["Contents"]) == 3
        assert all(obj["Key"].startswith("test-key-") for obj in response["Contents"])


# Example of a real-world business function using S3
def upload_data_to_s3(data: dict[str, Any], bucket: str, key: str) -> bool:
    """
    Upload structured data to S3 as JSON.

    Args:
        data: The data to upload
        bucket: The target S3 bucket
        key: The target S3 key

    Returns:
        bool: True if successful
    """
    try:
        s3_client = boto3.client("s3")
        s3_client.put_object(
            Bucket=bucket, Key=key, Body=json.dumps(data), ContentType="application/json"
        )
        return True
    except ClientError:
        return False


# Test for the business function
class TestBusinessFunctions:
    """Test real-world business functions."""

    @mock_aws
    def test_upload_data_to_s3(self) -> None:
        """Test the upload_data_to_s3 function with mocked S3."""
        # Arrange
        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket="business-bucket")
        test_data = {"business_id": 123, "metrics": {"sales": 10000}}

        # Act
        result = upload_data_to_s3(test_data, "business-bucket", "reports/daily.json")

        # Assert
        assert result is True

        # Verify the uploaded content
        response = s3_client.get_object(Bucket="business-bucket", Key="reports/daily.json")
        content = json.loads(response["Body"].read().decode("utf-8"))
        assert content == test_data
