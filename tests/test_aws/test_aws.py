"""Tests for the AWS utilities module."""

import json
from unittest.mock import MagicMock, patch

import boto3
import pytest
from botocore.exceptions import ClientError
from common_utils.aws import get_aws_session, get_secret, list_s3_objects


@pytest.fixture
def mock_boto3_session():
    """Create a mock boto3 session."""
    mock_session = MagicMock(spec=boto3.Session)
    return mock_session


def test_get_aws_session():
    """Test creating an AWS session."""
    session = get_aws_session(profile_name="test-profile", region_name="us-west-2")
    assert isinstance(session, boto3.Session)
    assert session.profile_name == "test-profile"
    assert session.region_name == "us-west-2"


@patch("common_utils.aws.get_aws_session")
def test_get_secret_string(mock_get_session, mock_boto3_session):
    """Test retrieving a string secret."""
    # Setup
    mock_get_session.return_value = mock_boto3_session
    mock_client = MagicMock()
    mock_boto3_session.client.return_value = mock_client

    secret_value = {"username": "test-user", "password": "test-password"}
    mock_client.get_secret_value.return_value = {"SecretString": json.dumps(secret_value)}

    # Execute
    result = get_secret("test-secret", "us-west-2", "test-profile")

    # Verify
    mock_get_session.assert_called_once_with(profile_name="test-profile", region_name="us-west-2")
    mock_boto3_session.client.assert_called_once_with(service_name="secretsmanager")
    mock_client.get_secret_value.assert_called_once_with(SecretId="test-secret")
    assert result == secret_value


@patch("common_utils.aws.get_aws_session")
def test_get_secret_binary(mock_get_session, mock_boto3_session):
    """Test retrieving a binary secret."""
    # Setup
    mock_get_session.return_value = mock_boto3_session
    mock_client = MagicMock()
    mock_boto3_session.client.return_value = mock_client

    binary_data = b"binary-secret-data"
    import base64

    mock_client.get_secret_value.return_value = {"SecretBinary": base64.b64encode(binary_data)}

    # Execute
    result = get_secret("test-secret", "us-west-2", "test-profile")

    # Verify
    assert result["binary"] == binary_data


@patch("common_utils.aws.get_aws_session")
def test_get_secret_error(mock_get_session, mock_boto3_session):
    """Test error handling when retrieving a secret."""
    # Setup
    mock_get_session.return_value = mock_boto3_session
    mock_client = MagicMock()
    mock_boto3_session.client.return_value = mock_client

    error = ClientError(
        {"Error": {"Code": "ResourceNotFoundException", "Message": "Secret not found"}},
        "GetSecretValue",
    )
    mock_client.get_secret_value.side_effect = error

    # Execute and verify
    with pytest.raises(ClientError):
        get_secret("test-secret", "us-west-2", "test-profile")


@patch("common_utils.aws.get_aws_session")
def test_list_s3_objects(mock_get_session, mock_boto3_session):
    """Test listing objects in an S3 bucket."""
    # Setup
    mock_get_session.return_value = mock_boto3_session
    mock_client = MagicMock()
    mock_boto3_session.client.return_value = mock_client

    mock_paginator = MagicMock()
    mock_client.get_paginator.return_value = mock_paginator

    page1 = {"Contents": [{"Key": "prefix/file1.csv"}, {"Key": "prefix/file2.csv"}]}
    page2 = {"Contents": [{"Key": "prefix/file3.csv"}]}
    mock_paginator.paginate.return_value = [page1, page2]

    # Execute
    result = list_s3_objects("test-bucket", "prefix", "test-profile", "us-west-2")

    # Verify
    mock_get_session.assert_called_once_with(profile_name="test-profile", region_name="us-west-2")
    mock_boto3_session.client.assert_called_once_with("s3")
    mock_client.get_paginator.assert_called_once_with("list_objects_v2")
    mock_paginator.paginate.assert_called_once_with(Bucket="test-bucket", Prefix="prefix")
    assert result == ["prefix/file1.csv", "prefix/file2.csv", "prefix/file3.csv"]


@patch("common_utils.aws.get_aws_session")
def test_list_s3_objects_empty(mock_get_session, mock_boto3_session):
    """Test listing objects in an empty S3 bucket."""
    # Setup
    mock_get_session.return_value = mock_boto3_session
    mock_client = MagicMock()
    mock_boto3_session.client.return_value = mock_client

    mock_paginator = MagicMock()
    mock_client.get_paginator.return_value = mock_paginator

    # Empty page without 'Contents'
    mock_paginator.paginate.return_value = [{}]

    # Execute
    result = list_s3_objects("test-bucket", "prefix")

    # Verify
    assert result == []
