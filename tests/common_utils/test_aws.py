"""
Unit tests for AWS utilities module.
"""

import json
from unittest.mock import MagicMock, patch

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_s3, mock_secretsmanager

from enterprise_data_engineering.common_utils.aws import (
    create_secret,
    delete_secret,
    get_aws_session,
    get_secret,
    list_s3_objects,
    list_secrets,
    rotate_secret_immediately,
    setup_secret_rotation,
    update_secret,
)


class TestGetAwsSession:
    """Tests for the get_aws_session function."""

    def test_default_session(self):
        """Test creating a default AWS session."""
        session = get_aws_session()
        assert session is not None
        assert hasattr(session, "client")
        assert hasattr(session, "resource")

    def test_session_with_profile(self):
        """Test creating an AWS session with a profile."""
        with patch("boto3.Session") as mock_session:
            session = get_aws_session(profile_name="test-profile")
            mock_session.assert_called_once_with(profile_name="test-profile", region_name=None)

    def test_session_with_region(self):
        """Test creating an AWS session with a region."""
        with patch("boto3.Session") as mock_session:
            session = get_aws_session(region_name="us-west-2")
            mock_session.assert_called_once_with(profile_name=None, region_name="us-west-2")

    def test_session_with_profile_and_region(self):
        """Test creating an AWS session with both profile and region."""
        with patch("boto3.Session") as mock_session:
            session = get_aws_session(profile_name="test-profile", region_name="us-west-2")
            mock_session.assert_called_once_with(
                profile_name="test-profile", region_name="us-west-2"
            )


@mock_secretsmanager
class TestSecretsManager:
    """Tests for the Secrets Manager utility functions."""

    @pytest.fixture
    def setup_secret(self):
        """Create a test secret for use in tests."""
        client = boto3.client("secretsmanager", region_name="us-east-1")
        secret_value = {"username": "testuser", "password": "testpass"}
        client.create_secret(
            Name="test-secret",
            SecretString=json.dumps(secret_value),
            Description="Test secret for unit tests",
        )
        return {"name": "test-secret", "value": secret_value}

    def test_get_secret(self, setup_secret):
        """Test retrieving a secret from Secrets Manager."""
        secret_result = get_secret(setup_secret["name"], region_name="us-east-1")

        assert secret_result is not None
        assert secret_result["username"] == "testuser"
        assert secret_result["password"] == "testpass"

    def test_get_secret_not_found(self):
        """Test retrieving a non-existent secret."""
        with pytest.raises(ClientError):
            get_secret("nonexistent-secret", region_name="us-east-1")

    def test_create_secret(self):
        """Test creating a new secret."""
        secret_name = "new-test-secret"
        secret_value = {"user": "newuser", "pass": "newpass"}

        result = create_secret(
            secret_name=secret_name,
            secret_value=secret_value,
            description="New test secret",
            region_name="us-east-1",
        )

        assert "ARN" in result
        assert "Name" in result
        assert result["Name"] == secret_name

        # Verify the secret was created with correct value
        client = boto3.client("secretsmanager", region_name="us-east-1")
        response = client.get_secret_value(SecretId=secret_name)
        assert "SecretString" in response

        stored_value = json.loads(response["SecretString"])
        assert stored_value["user"] == "newuser"
        assert stored_value["pass"] == "newpass"

    def test_create_secret_string_value(self):
        """Test creating a secret with a string value."""
        secret_name = "string-value-secret"
        secret_value = "simple-string-secret"

        result = create_secret(
            secret_name=secret_name,
            secret_value=secret_value,
            region_name="us-east-1",
        )

        assert "ARN" in result
        assert "Name" in result
        assert result["Name"] == secret_name

        # Verify the secret was created with correct value
        client = boto3.client("secretsmanager", region_name="us-east-1")
        response = client.get_secret_value(SecretId=secret_name)
        assert "SecretString" in response
        assert response["SecretString"] == secret_value

    def test_update_secret(self, setup_secret):
        """Test updating an existing secret."""
        # Update the secret
        updated_value = {"username": "updateduser", "password": "updatedpass"}
        result = update_secret(
            secret_name=setup_secret["name"],
            secret_value=updated_value,
            region_name="us-east-1",
        )

        assert "ARN" in result
        assert "Name" in result

        # Verify the secret was updated
        secret_result = get_secret(setup_secret["name"], region_name="us-east-1")
        assert secret_result["username"] == "updateduser"
        assert secret_result["password"] == "updatedpass"

    def test_update_nonexistent_secret(self):
        """Test updating a non-existent secret raises an error."""
        with pytest.raises(ClientError):
            update_secret(
                secret_name="nonexistent-secret",
                secret_value={"key": "value"},
                region_name="us-east-1",
            )

    def test_list_secrets(self, setup_secret):
        """Test listing secrets."""
        # Create additional secrets
        create_secret("list-test-1", {"key1": "value1"}, region_name="us-east-1")
        create_secret("list-test-2", {"key2": "value2"}, region_name="us-east-1")

        secrets = list_secrets(region_name="us-east-1")

        assert len(secrets) >= 3  # At least our test secrets
        assert any(s["Name"] == "test-secret" for s in secrets)
        assert any(s["Name"] == "list-test-1" for s in secrets)
        assert any(s["Name"] == "list-test-2" for s in secrets)

    def test_list_secrets_max_results(self):
        """Test listing secrets with max_results."""
        # Create more secrets than our limit
        for i in range(5):
            create_secret(f"limit-test-{i}", {"key": f"value-{i}"}, region_name="us-east-1")

        secrets = list_secrets(max_results=3, region_name="us-east-1")

        assert len(secrets) == 3

    def test_delete_secret(self):
        """Test deleting a secret."""
        # Create a secret to delete
        create_secret("delete-test", {"key": "value"}, region_name="us-east-1")

        # Delete it
        result = delete_secret(
            secret_name="delete-test",
            force_delete=True,
            region_name="us-east-1",
        )

        assert "ARN" in result
        assert "Name" in result
        assert result["Name"] == "delete-test"

        # Verify it was deleted
        client = boto3.client("secretsmanager", region_name="us-east-1")
        with pytest.raises(ClientError):
            client.get_secret_value(SecretId="delete-test")

    def test_setup_secret_rotation(self, setup_secret):
        """Test setting up secret rotation."""
        lambda_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-rotation-lambda"

        # Due to moto limitations, mock the rotate call
        with patch("boto3.client") as mock_client:
            mock_sm = MagicMock()
            mock_client.return_value = mock_sm

            result = setup_secret_rotation(
                secret_name=setup_secret["name"],
                rotation_lambda_arn=lambda_arn,
                rotation_days=15,
                region_name="us-east-1",
            )

            # Verify rotation was set up
            mock_sm.rotate_secret.assert_called_once()

    def test_rotate_secret_immediately(self, setup_secret):
        """Test immediate rotation of a secret."""
        # Due to moto limitations, mock the rotate call
        with patch("boto3.client") as mock_client:
            mock_sm = MagicMock()
            mock_client.return_value = mock_sm

            result = rotate_secret_immediately(
                secret_name=setup_secret["name"],
                region_name="us-east-1",
            )

            # Verify rotation was triggered
            mock_sm.rotate_secret.assert_called_once()


@mock_s3
class TestS3Functions:
    """Tests for the S3 utility functions."""

    @pytest.fixture
    def setup_s3_bucket(self):
        """Create test S3 bucket and objects."""
        # Create test bucket and objects
        s3 = boto3.client("s3", region_name="us-east-1")
        bucket_name = "test-bucket"

        # Create bucket
        s3.create_bucket(Bucket=bucket_name)

        # Create test objects
        s3.put_object(Bucket=bucket_name, Key="file1.txt", Body="content1")
        s3.put_object(Bucket=bucket_name, Key="file2.txt", Body="content2")
        s3.put_object(Bucket=bucket_name, Key="folder/file3.txt", Body="content3")
        s3.put_object(Bucket=bucket_name, Key="folder/file4.txt", Body="content4")
        s3.put_object(Bucket=bucket_name, Key="folder/subfolder/file5.txt", Body="content5")

        return bucket_name

    def test_list_s3_objects_default(self, setup_s3_bucket):
        """Test listing all objects in a bucket."""
        objects = list_s3_objects(
            bucket_name=setup_s3_bucket,
            region_name="us-east-1",
        )

        assert len(objects) == 5
        assert "file1.txt" in objects
        assert "file2.txt" in objects
        assert "folder/file3.txt" in objects
        assert "folder/file4.txt" in objects
        assert "folder/subfolder/file5.txt" in objects

    def test_list_s3_objects_with_prefix(self, setup_s3_bucket):
        """Test listing objects with a prefix."""
        objects = list_s3_objects(
            bucket_name=setup_s3_bucket,
            prefix="folder/",
            region_name="us-east-1",
        )

        assert len(objects) == 3
        assert "folder/file3.txt" in objects
        assert "folder/file4.txt" in objects
        assert "folder/subfolder/file5.txt" in objects
        assert "file1.txt" not in objects
        assert "file2.txt" not in objects

    def test_list_s3_objects_with_subfolder_prefix(self, setup_s3_bucket):
        """Test listing objects with a subfolder prefix."""
        objects = list_s3_objects(
            bucket_name=setup_s3_bucket,
            prefix="folder/subfolder/",
            region_name="us-east-1",
        )

        assert len(objects) == 1
        assert "folder/subfolder/file5.txt" in objects

    def test_list_nonexistent_bucket(self):
        """Test listing objects in a non-existent bucket."""
        with pytest.raises(ClientError):
            list_s3_objects(
                bucket_name="nonexistent-bucket",
                region_name="us-east-1",
            )
