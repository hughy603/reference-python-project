"""Tests for the AWS Secrets Manager rotation functionality."""

import json
from unittest.mock import MagicMock, patch

import boto3
import pytest
from botocore.exceptions import ClientError
from common_utils.aws import (
    create_secret,
    delete_secret,
    list_secrets,
    rotate_secret_immediately,
    setup_secret_rotation,
    update_secret,
)


@pytest.fixture
def mock_boto3_session():
    """Create a mock boto3 session."""
    mock_session = MagicMock(spec=boto3.Session)
    return mock_session


@patch("common_utils.aws.get_aws_session")
def test_create_secret(mock_get_session, mock_boto3_session):
    """Test creating a new secret."""
    # Setup
    mock_get_session.return_value = mock_boto3_session
    mock_client = MagicMock()
    mock_boto3_session.client.return_value = mock_client

    secret_name = "test-db-credentials"
    secret_value = {"username": "admin", "password": "securePassword123"}
    description = "Database credentials for test environment"
    tags = [{"Key": "Environment", "Value": "Test"}, {"Key": "Project", "Value": "DataPipeline"}]

    response = {"ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:test-db-credentials"}
    mock_client.create_secret.return_value = response

    # Execute
    result = create_secret(
        secret_name=secret_name,
        secret_value=secret_value,
        description=description,
        tags=tags,
        region_name="us-east-1",
    )

    # Verify
    mock_get_session.assert_called_once_with(profile_name=None, region_name="us-east-1")
    mock_boto3_session.client.assert_called_once_with(service_name="secretsmanager")
    mock_client.create_secret.assert_called_once_with(
        Name=secret_name,
        Description=description,
        SecretString=json.dumps(secret_value),
        Tags=tags,
    )
    assert result == response


@patch("common_utils.aws.get_aws_session")
def test_update_secret(mock_get_session, mock_boto3_session):
    """Test updating an existing secret."""
    # Setup
    mock_get_session.return_value = mock_boto3_session
    mock_client = MagicMock()
    mock_boto3_session.client.return_value = mock_client

    secret_name = "test-db-credentials"
    new_secret_value = {"username": "admin", "password": "newPassword456"}

    response = {
        "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:test-db-credentials",
        "VersionId": "a1b2c3d4-5678-90ab-cdef-EXAMPLE11111",
    }
    mock_client.update_secret.return_value = response

    # Execute
    result = update_secret(
        secret_name=secret_name,
        secret_value=new_secret_value,
        region_name="us-east-1",
    )

    # Verify
    mock_get_session.assert_called_once_with(profile_name=None, region_name="us-east-1")
    mock_boto3_session.client.assert_called_once_with(service_name="secretsmanager")
    mock_client.update_secret.assert_called_once_with(
        SecretId=secret_name,
        SecretString=json.dumps(new_secret_value),
    )
    assert result == response


@patch("common_utils.aws.get_aws_session")
def test_setup_secret_rotation(mock_get_session, mock_boto3_session):
    """Test setting up automatic secret rotation."""
    # Setup
    mock_get_session.return_value = mock_boto3_session
    mock_client = MagicMock()
    mock_boto3_session.client.return_value = mock_client

    secret_name = "test-db-credentials"
    rotation_lambda_arn = "arn:aws:lambda:us-east-1:123456789012:function:rotate-db-credentials"
    rotation_days = 60

    response = {
        "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:test-db-credentials",
        "VersionId": "a1b2c3d4-5678-90ab-cdef-EXAMPLE22222",
    }
    mock_client.rotate_secret.return_value = response

    # Execute
    result = setup_secret_rotation(
        secret_name=secret_name,
        rotation_lambda_arn=rotation_lambda_arn,
        rotation_days=rotation_days,
        region_name="us-east-1",
    )

    # Verify
    mock_get_session.assert_called_once_with(profile_name=None, region_name="us-east-1")
    mock_boto3_session.client.assert_called_once_with(service_name="secretsmanager")
    mock_client.rotate_secret.assert_called_once_with(
        SecretId=secret_name,
        RotationLambdaARN=rotation_lambda_arn,
        RotationRules={"AutomaticallyAfterDays": rotation_days},
    )
    assert result == response


@patch("common_utils.aws.get_aws_session")
def test_rotate_secret_immediately(mock_get_session, mock_boto3_session):
    """Test triggering an immediate secret rotation."""
    # Setup
    mock_get_session.return_value = mock_boto3_session
    mock_client = MagicMock()
    mock_boto3_session.client.return_value = mock_client

    secret_name = "test-db-credentials"

    response = {
        "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:test-db-credentials",
        "VersionId": "a1b2c3d4-5678-90ab-cdef-EXAMPLE33333",
    }
    mock_client.rotate_secret.return_value = response

    # Execute
    result = rotate_secret_immediately(
        secret_name=secret_name,
        region_name="us-east-1",
    )

    # Verify
    mock_get_session.assert_called_once_with(profile_name=None, region_name="us-east-1")
    mock_boto3_session.client.assert_called_once_with(service_name="secretsmanager")
    mock_client.rotate_secret.assert_called_once_with(
        SecretId=secret_name,
    )
    assert result == response


@patch("common_utils.aws.get_aws_session")
def test_list_secrets(mock_get_session, mock_boto3_session):
    """Test listing secrets."""
    # Setup
    mock_get_session.return_value = mock_boto3_session
    mock_client = MagicMock()
    mock_boto3_session.client.return_value = mock_client

    mock_paginator = MagicMock()
    mock_client.get_paginator.return_value = mock_paginator

    # Create mock pages with secrets
    secrets = [
        {
            "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:secret1",
            "Name": "secret1",
            "LastChangedDate": "2023-01-01T12:00:00Z",
        },
        {
            "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:secret2",
            "Name": "secret2",
            "LastChangedDate": "2023-01-02T14:30:00Z",
        },
    ]
    mock_paginator.paginate.return_value = [{"SecretList": secrets}]

    # Execute
    result = list_secrets(max_results=10, region_name="us-east-1")

    # Verify
    mock_get_session.assert_called_once_with(profile_name=None, region_name="us-east-1")
    mock_boto3_session.client.assert_called_once_with(service_name="secretsmanager")
    mock_client.get_paginator.assert_called_once_with("list_secrets")
    mock_paginator.paginate.assert_called_once_with(
        MaxResults=10, PaginationConfig={"MaxItems": 10}
    )
    assert result == secrets


@patch("common_utils.aws.get_aws_session")
def test_delete_secret(mock_get_session, mock_boto3_session):
    """Test deleting a secret."""
    # Setup
    mock_get_session.return_value = mock_boto3_session
    mock_client = MagicMock()
    mock_boto3_session.client.return_value = mock_client

    secret_name = "test-db-credentials"
    recovery_window_days = 15

    response = {
        "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:test-db-credentials",
        "DeletionDate": "2023-02-15T00:00:00Z",
    }
    mock_client.delete_secret.return_value = response

    # Execute
    result = delete_secret(
        secret_name=secret_name,
        recovery_window_days=recovery_window_days,
        region_name="us-east-1",
    )

    # Verify
    mock_get_session.assert_called_once_with(profile_name=None, region_name="us-east-1")
    mock_boto3_session.client.assert_called_once_with(service_name="secretsmanager")
    mock_client.delete_secret.assert_called_once_with(
        SecretId=secret_name, RecoveryWindowInDays=recovery_window_days
    )
    assert result == response


@patch("common_utils.aws.get_aws_session")
def test_delete_secret_force(mock_get_session, mock_boto3_session):
    """Test force deleting a secret without recovery window."""
    # Setup
    mock_get_session.return_value = mock_boto3_session
    mock_client = MagicMock()
    mock_boto3_session.client.return_value = mock_client

    secret_name = "test-db-credentials"

    response = {
        "ARN": "arn:aws:secretsmanager:us-east-1:123456789012:secret:test-db-credentials",
        "DeletionDate": "2023-02-01T00:00:00Z",
    }
    mock_client.delete_secret.return_value = response

    # Execute
    result = delete_secret(
        secret_name=secret_name,
        force_delete=True,
        region_name="us-east-1",
    )

    # Verify
    mock_get_session.assert_called_once_with(profile_name=None, region_name="us-east-1")
    mock_boto3_session.client.assert_called_once_with(service_name="secretsmanager")
    mock_client.delete_secret.assert_called_once_with(
        SecretId=secret_name, ForceDeleteWithoutRecovery=True
    )
    assert result == response


@patch("common_utils.aws.get_aws_session")
def test_create_secret_error(mock_get_session, mock_boto3_session):
    """Test error handling when creating a secret."""
    # Setup
    mock_get_session.return_value = mock_boto3_session
    mock_client = MagicMock()
    mock_boto3_session.client.return_value = mock_client

    secret_name = "test-db-credentials"
    secret_value = {"username": "admin", "password": "securePassword123"}

    # Simulate an error response
    error = ClientError(
        {"Error": {"Code": "ResourceExistsException", "Message": "Secret already exists"}},
        "CreateSecret",
    )
    mock_client.create_secret.side_effect = error

    # Execute and verify exception is raised
    with pytest.raises(ClientError) as excinfo:
        create_secret(
            secret_name=secret_name,
            secret_value=secret_value,
            region_name="us-east-1",
        )

    assert "ResourceExistsException" in str(excinfo.value)
    assert "Secret already exists" in str(excinfo.value)
