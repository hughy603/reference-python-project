"""AWS utility module for common AWS operations."""

import base64
import json
import logging
from typing import Any

import boto3
from boto3.session import Session
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def get_aws_session(profile_name: str | None = None, region_name: str | None = None) -> Session:
    """
    Create an AWS session with the specified profile and region.

    Args:
        profile_name: The AWS profile name to use
        region_name: The AWS region to use

    Returns:
        A boto3 Session object
    """
    return boto3.Session(profile_name=profile_name, region_name=region_name)


def get_secret(
    secret_name: str,
    region_name: str | None = None,
    profile_name: str | None = None,
) -> dict[str, Any]:
    """
    Retrieve a secret from AWS Secrets Manager.

    Args:
        secret_name: Name or ARN of the secret to retrieve
        region_name: AWS region where the secret is stored
        profile_name: AWS profile to use for authentication

    Returns:
        Dictionary containing the secret values or binary data

    Raises:
        ClientError: If the secret cannot be retrieved
    """
    # Create a Secrets Manager client
    session = get_aws_session(profile_name=profile_name, region_name=region_name)
    client = session.client(service_name="secretsmanager")

    try:
        # Get the secret value
        response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        # Handle potential errors
        logger.error(f"Error retrieving secret '{secret_name}': {e!s}")
        raise

    # Parse and return the secret
    if "SecretString" in response:
        try:
            return json.loads(response["SecretString"])
        except json.JSONDecodeError:
            # Handle non-JSON strings
            return {"string": response["SecretString"]}
    else:
        # Handle binary secrets
        return {"binary": base64.b64decode(response["SecretBinary"])}


def list_s3_objects(
    bucket_name: str,
    prefix: str = "",
    profile_name: str | None = None,
    region_name: str | None = None,
) -> list[str]:
    """
    List objects in an S3 bucket with the given prefix.

    Args:
        bucket_name: The name of the S3 bucket
        prefix: Prefix to filter objects (directory path)
        profile_name: AWS profile to use
        region_name: AWS region where the bucket is located

    Returns:
        List of object keys (paths)
    """
    session = get_aws_session(profile_name=profile_name, region_name=region_name)
    s3_client = session.client("s3")

    # Use pagination to handle buckets with many objects
    paginator = s3_client.get_paginator("list_objects_v2")
    pages = paginator.paginate(Bucket=bucket_name, Prefix=prefix)

    objects = []
    for page in pages:
        if "Contents" in page:
            objects.extend([obj["Key"] for obj in page["Contents"]])

    return objects


def create_secret(
    secret_name: str,
    secret_value: dict[str, Any] | str,
    description: str = "",
    tags: list[dict[str, str]] | None = None,
    region_name: str | None = None,
    profile_name: str | None = None,
) -> dict[str, Any]:
    """
    Create a new secret in AWS Secrets Manager.

    Args:
        secret_name: Name for the secret
        secret_value: Value to store (dictionary or string)
        description: Description of the secret
        tags: List of tags to apply to the secret
        region_name: AWS region to store the secret
        profile_name: AWS profile to use

    Returns:
        Response from the create_secret API call

    Raises:
        ClientError: If the secret cannot be created
    """
    session = get_aws_session(profile_name=profile_name, region_name=region_name)
    client = session.client(service_name="secretsmanager")

    # Convert dict to JSON string if necessary
    secret_string = json.dumps(secret_value) if isinstance(secret_value, dict) else secret_value

    try:
        kwargs = {
            "Name": secret_name,
            "Description": description,
            "SecretString": secret_string,
        }

        if tags:
            kwargs["Tags"] = tags

        response = client.create_secret(**kwargs)
        logger.info(f"Created secret '{secret_name}'")
        return response
    except ClientError as e:
        logger.error(f"Error creating secret '{secret_name}': {e!s}")
        raise


def update_secret(
    secret_name: str,
    secret_value: dict[str, Any] | str,
    region_name: str | None = None,
    profile_name: str | None = None,
) -> dict[str, Any]:
    """
    Update an existing secret in AWS Secrets Manager.

    Args:
        secret_name: Name or ARN of the secret to update
        secret_value: New value to store (dictionary or string)
        region_name: AWS region where the secret is stored
        profile_name: AWS profile to use

    Returns:
        Response from the update_secret API call

    Raises:
        ClientError: If the secret cannot be updated
    """
    session = get_aws_session(profile_name=profile_name, region_name=region_name)
    client = session.client(service_name="secretsmanager")

    # Convert dict to JSON string if necessary
    secret_string = json.dumps(secret_value) if isinstance(secret_value, dict) else secret_value

    try:
        response = client.update_secret(
            SecretId=secret_name,
            SecretString=secret_string,
        )
        logger.info(f"Updated secret '{secret_name}'")
        return response
    except ClientError as e:
        logger.error(f"Error updating secret '{secret_name}': {e!s}")
        raise


def setup_secret_rotation(
    secret_name: str,
    rotation_lambda_arn: str,
    rotation_days: int = 30,
    region_name: str | None = None,
    profile_name: str | None = None,
) -> dict[str, Any]:
    """
    Configure automatic rotation for a secret in AWS Secrets Manager.

    Args:
        secret_name: Name or ARN of the secret to configure
        rotation_lambda_arn: ARN of the Lambda function to perform rotation
        rotation_days: Number of days between automatic rotations
        region_name: AWS region where the secret is stored
        profile_name: AWS profile to use

    Returns:
        Response from the rotate_secret API call

    Raises:
        ClientError: If rotation cannot be configured
    """
    session = get_aws_session(profile_name=profile_name, region_name=region_name)
    client = session.client(service_name="secretsmanager")

    try:
        response = client.rotate_secret(
            SecretId=secret_name,
            RotationLambdaARN=rotation_lambda_arn,
            RotationRules={"AutomaticallyAfterDays": rotation_days},
        )
        logger.info(f"Configured automatic rotation for secret '{secret_name}'")
        return response
    except ClientError as e:
        logger.error(f"Error configuring rotation for secret '{secret_name}': {e!s}")
        raise


def rotate_secret_immediately(
    secret_name: str,
    region_name: str | None = None,
    profile_name: str | None = None,
) -> dict[str, Any]:
    """
    Trigger an immediate rotation of a secret in AWS Secrets Manager.

    Args:
        secret_name: Name or ARN of the secret to rotate
        region_name: AWS region where the secret is stored
        profile_name: AWS profile to use

    Returns:
        Response from the rotate_secret API call

    Raises:
        ClientError: If the secret cannot be rotated
    """
    session = get_aws_session(profile_name=profile_name, region_name=region_name)
    client = session.client(service_name="secretsmanager")

    try:
        response = client.rotate_secret(
            SecretId=secret_name,
        )
        logger.info(f"Triggered immediate rotation for secret '{secret_name}'")
        return response
    except ClientError as e:
        logger.error(f"Error rotating secret '{secret_name}': {e!s}")
        raise


def list_secrets(
    max_results: int = 100,
    region_name: str | None = None,
    profile_name: str | None = None,
) -> list[dict[str, Any]]:
    """
    List secrets in AWS Secrets Manager.

    Args:
        max_results: Maximum number of secrets to return
        region_name: AWS region to query
        profile_name: AWS profile to use

    Returns:
        List of dictionaries containing secret metadata

    Raises:
        ClientError: If the secrets cannot be listed
    """
    session = get_aws_session(profile_name=profile_name, region_name=region_name)
    client = session.client(service_name="secretsmanager")

    try:
        paginator = client.get_paginator("list_secrets")
        iterator = paginator.paginate(
            MaxResults=max_results,
            PaginationConfig={"MaxItems": max_results},
        )

        secrets = []
        for page in iterator:
            if "SecretList" in page:
                secrets.extend(page["SecretList"])

        return secrets
    except ClientError as e:
        logger.error(f"Error listing secrets: {e!s}")
        raise


def delete_secret(
    secret_name: str,
    recovery_window_days: int = 30,
    force_delete: bool = False,
    region_name: str | None = None,
    profile_name: str | None = None,
) -> dict[str, Any]:
    """
    Delete a secret from AWS Secrets Manager.

    Args:
        secret_name: Name or ARN of the secret to delete
        recovery_window_days: Number of days before permanent deletion (0-30)
        force_delete: If True, permanently delete without recovery window
        region_name: AWS region where the secret is stored
        profile_name: AWS profile to use

    Returns:
        Response from the delete_secret API call

    Raises:
        ClientError: If the secret cannot be deleted
    """
    session = get_aws_session(profile_name=profile_name, region_name=region_name)
    client = session.client(service_name="secretsmanager")

    try:
        kwargs = {"SecretId": secret_name}

        if force_delete:
            kwargs["ForceDeleteWithoutRecovery"] = True
        else:
            kwargs["RecoveryWindowInDays"] = recovery_window_days

        response = client.delete_secret(**kwargs)
        logger.info(f"Deleted secret '{secret_name}'")
        return response
    except ClientError as e:
        logger.error(f"Error deleting secret '{secret_name}': {e!s}")
        raise
