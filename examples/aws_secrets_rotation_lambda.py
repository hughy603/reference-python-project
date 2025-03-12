"""
AWS Secrets Manager rotation Lambda example.

This module provides an example AWS Lambda function that rotates database credentials stored in
AWS Secrets Manager. This is designed to be deployed as a Lambda function and used with the
automated rotation feature of AWS Secrets Manager.

For more information on AWS Secrets Manager rotation, see:
https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html
"""

import json
import logging
from typing import Any

import boto3
import pymysql
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """
    AWS Lambda function handler for rotating database credentials.

    Args:
        event: Lambda event containing information about the rotation
        context: Lambda context object

    Returns:
        Dictionary with status information for the rotation
    """
    logger.info("Starting secrets rotation")

    # Parse event information
    arn = event["SecretId"]
    token = event["ClientRequestToken"]
    step = event["Step"]

    # Initialize SecretsManager client
    service_client = boto3.client("secretsmanager")

    # Validate event information
    try:
        metadata = service_client.describe_secret(SecretId=arn)
        if not metadata["RotationEnabled"]:
            logger.error(f"Secret {arn} is not enabled for rotation")
            raise ValueError(f"Secret {arn} is not enabled for rotation")

        versions = metadata["VersionIdsToStages"]
        if token not in versions:
            logger.error(f"Secret version {token} has no stage for rotation")
            raise ValueError(f"Secret version {token} has no stage for rotation")

        if "AWSCURRENT" in versions[token]:
            logger.info(f"Secret version {token} is already AWSCURRENT")
            return {"statusCode": 200, "message": "Secret is already current"}

        elif "AWSPENDING" not in versions[token]:
            logger.error(f"Secret version {token} not set as AWSPENDING")
            raise ValueError(f"Secret version {token} not set as AWSPENDING")

    except ClientError as e:
        logger.error(f"Error validating secret: {e!s}")
        raise

    # Execute the appropriate step based on the rotation request
    if step == "createSecret":
        create_secret(service_client, arn, token)
    elif step == "setSecret":
        set_secret(service_client, arn, token)
    elif step == "testSecret":
        test_secret(service_client, arn, token)
    elif step == "finishSecret":
        finish_secret(service_client, arn, token)
    else:
        logger.error(f"Invalid step parameter: {step}")
        raise ValueError(f"Invalid step parameter: {step}")

    logger.info(f"Completed {step} step for secret {arn}")
    return {"statusCode": 200, "message": f"Successfully completed {step}"}


def create_secret(service_client: Any, arn: str, token: str) -> None:
    """
    Create a new secret with a new password.

    This step generates a new password and creates a new version of the secret.

    Args:
        service_client: The SecretsManager service client
        arn: The ARN of the secret being rotated
        token: The ClientRequestToken for this rotation
    """
    try:
        # Get the current secret
        current_secret = get_secret_dict(service_client, arn, "AWSCURRENT")

        # Generate new password
        new_password = generate_password()

        # Create new secret value with updated password
        new_secret = current_secret.copy()
        new_secret["password"] = new_password

        # Put the new secret value in the AWSPENDING stage
        service_client.put_secret_value(
            SecretId=arn,
            ClientRequestToken=token,
            SecretString=json.dumps(new_secret),
            VersionStages=["AWSPENDING"],
        )

        logger.info(f"Created new secret version for {arn}")

    except ClientError as e:
        logger.error(f"Error creating secret: {e!s}")
        raise


def set_secret(service_client: Any, arn: str, token: str) -> None:
    """
    Set the new password in the database.

    Args:
        service_client: The SecretsManager service client
        arn: The ARN of the secret being rotated
        token: The ClientRequestToken for this rotation
    """
    try:
        # Get the current and pending secret values
        current_secret = get_secret_dict(service_client, arn, "AWSCURRENT")
        pending_secret = get_secret_dict(service_client, arn, "AWSPENDING")

        # Connect to the database using current credentials
        with get_db_connection(
            host=current_secret["host"],
            port=current_secret.get("port", 3306),
            user=current_secret["username"],
            password=current_secret["password"],
            database=current_secret.get("dbname", "mysql"),
        ) as conn:
            with conn.cursor() as cursor:
                # Update the user's password in the database
                set_password_query = "ALTER USER %s@'%%' IDENTIFIED BY %s"
                cursor.execute(
                    set_password_query, (current_secret["username"], pending_secret["password"])
                )
                conn.commit()

        logger.info(f'Updated password in database for user {current_secret["username"]}')

    except (ClientError, pymysql.Error) as e:
        logger.error(f"Error setting secret in database: {e!s}")
        raise


def test_secret(service_client: Any, arn: str, token: str) -> None:
    """
    Test the new secret by connecting to the database.

    Args:
        service_client: The SecretsManager service client
        arn: The ARN of the secret being rotated
        token: The ClientRequestToken for this rotation
    """
    try:
        # Get the pending secret value
        pending_secret = get_secret_dict(service_client, arn, "AWSPENDING")

        # Try to connect with the new credentials
        with get_db_connection(
            host=pending_secret["host"],
            port=pending_secret.get("port", 3306),
            user=pending_secret["username"],
            password=pending_secret["password"],
            database=pending_secret.get("dbname", "mysql"),
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result[0] != 1:
                    raise ValueError("Test query failed")

        logger.info(f'Successfully tested new credentials for {pending_secret["username"]}')

    except (ClientError, pymysql.Error) as e:
        logger.error(f"Error testing secret: {e!s}")
        raise


def finish_secret(service_client: Any, arn: str, token: str) -> None:
    """
    Finish the rotation by marking the pending secret as current.

    Args:
        service_client: The SecretsManager service client
        arn: The ARN of the secret being rotated
        token: The ClientRequestToken for this rotation
    """
    try:
        # Get the current version
        metadata = service_client.describe_secret(SecretId=arn)
        current_version = None
        for version in metadata["VersionIdsToStages"]:
            if "AWSCURRENT" in metadata["VersionIdsToStages"][version]:
                if version != token:
                    current_version = version
                break

        # Mark the pending secret as current
        service_client.update_secret_version_stage(
            SecretId=arn,
            VersionStage="AWSCURRENT",
            MoveToVersionId=token,
            RemoveFromVersionId=current_version if current_version else None,
        )

        logger.info(f"Successfully marked version {token} as AWSCURRENT")

    except ClientError as e:
        logger.error(f"Error finishing secret rotation: {e!s}")
        raise


def get_secret_dict(service_client: Any, arn: str, stage: str) -> dict[str, Any]:
    """
    Get the secret value from Secrets Manager.

    Args:
        service_client: The SecretsManager service client
        arn: The ARN of the secret
        stage: The stage of the secret (AWSCURRENT or AWSPENDING)

    Returns:
        Dictionary containing the secret values
    """
    try:
        response = service_client.get_secret_value(SecretId=arn, VersionStage=stage)
        secret_string = response["SecretString"]
        return json.loads(secret_string)
    except ClientError as e:
        logger.error(f"Error getting secret value: {e!s}")
        raise


def get_db_connection(
    host: str, user: str, password: str, port: int = 3306, database: str = "mysql"
) -> pymysql.Connection:
    """
    Connect to a MySQL database.

    Args:
        host: Database hostname
        user: Database username
        password: Database password
        port: Database port
        database: Database name

    Returns:
        Database connection object
    """
    try:
        conn = pymysql.connect(
            host=host, user=user, password=password, port=port, database=database, connect_timeout=5
        )
        return conn
    except pymysql.Error as e:
        logger.error(f"Error connecting to database: {e!s}")
        raise


def generate_password(length: int = 16) -> str:
    """
    Generate a secure random password.

    Args:
        length: Length of the password to generate

    Returns:
        A secure random password
    """
    import random
    import string

    # Define character sets for password complexity
    char_sets = [
        string.ascii_lowercase,
        string.ascii_uppercase,
        string.digits,
        "!@#$%^&*()-_=+[]{}|;:,.<>?",
    ]

    # Ensure at least one character from each set
    password = [random.choice(char_set) for char_set in char_sets]

    # Fill the rest with random characters from all sets
    all_chars = "".join(char_sets)
    password.extend(random.choice(all_chars) for _ in range(length - len(char_sets)))

    # Shuffle the password characters
    random.shuffle(password)

    return "".join(password)


# Example AWS SAM/CloudFormation template for deploying this Lambda function
"""
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Resources:
  SecretsRotationFunction:
    Type: AWS::Serverless::Function
    Properties:
      CodeUri: ./
      Handler: aws_secrets_rotation_lambda.lambda_handler
      Runtime: python3.9
      Timeout: 30
      Policies:
        - AWSSecretsManagerRotationPolicy:
            FunctionName: !Ref SecretsRotationFunction
        - Version: '2012-10-17'
          Statement:
            - Effect: Allow
              Action:
                - secretsmanager:GetSecretValue
                - secretsmanager:DescribeSecret
                - secretsmanager:PutSecretValue
                - secretsmanager:UpdateSecretVersionStage
              Resource: !Sub 'arn:aws:secretsmanager:${AWS::Region}:${AWS::AccountId}:secret:*'
      Environment:
        Variables:
          LOG_LEVEL: INFO
"""
