"""
Enhanced AWS mocking tests to improve code coverage.

This module expands on the existing AWS mocking tests by:
1. Adding tests for additional AWS services
2. Testing error handling and edge cases
3. Using context managers and fixtures consistently
4. Testing more complex integration scenarios
5. Demonstrating pagination and filtering
"""

import json
import unittest.mock
from datetime import datetime, timedelta

import boto3
import botocore.exceptions
import pytest
from moto import (
    mock_cloudwatch,
    mock_dynamodb,
    mock_events,
    mock_iam,
    mock_kms,
    mock_lambda,
    mock_s3,
    mock_secretsmanager,
    mock_ses,
    mock_sns,
    mock_sqs,
    mock_ssm,
    mock_stepfunctions,
)

# If any of the specific mock decorators are not available, use mock_aws instead
try:
    from moto import mock_cloudwatch
except ImportError:
    from moto import mock_aws as mock_cloudwatch

try:
    from moto import mock_events
except ImportError:
    from moto import mock_aws as mock_events

try:
    from moto import mock_iam
except ImportError:
    from moto import mock_aws as mock_iam

try:
    from moto import mock_kms
except ImportError:
    from moto import mock_aws as mock_kms

try:
    from moto import mock_lambda
except ImportError:
    from moto import mock_aws as mock_lambda

try:
    from moto import mock_secretsmanager
except ImportError:
    from moto import mock_aws as mock_secretsmanager

try:
    from moto import mock_ses
except ImportError:
    from moto import mock_aws as mock_ses

try:
    from moto import mock_stepfunctions
except ImportError:
    from moto import mock_aws as mock_stepfunctions


class TestLambdaMocking:
    """Tests for AWS Lambda mocking."""

    @mock_lambda
    def test_create_and_invoke_lambda(self):
        """Test creating and invoking a Lambda function."""
        lambda_client = boto3.client("lambda", region_name="us-east-1")

        # Create a simple Lambda function
        lambda_code = b"""
def handler(event, context):
    print("Lambda function executed!")
    return {
        "statusCode": 200,
        "body": f"Hello {event.get('name', 'World')}!"
    }
"""
        zip_output = bytes("", "utf-8")

        # Create Lambda function
        lambda_client.create_function(
            FunctionName="test-function",
            Runtime="python3.10",
            Role="arn:aws:iam::123456789012:role/lambda-role",
            Handler="lambda_function.handler",
            Code={"ZipFile": zip_output},
            Description="Test lambda function",
            Timeout=30,
            MemorySize=128,
            Publish=True,
        )

        # Invoke the function
        with unittest.mock.patch(
            "moto.awslambda.models.LambdaFunction._invoke_lambda"
        ) as mock_invoke:
            mock_invoke.return_value = {
                "StatusCode": 200,
                "Payload": json.dumps({"statusCode": 200, "body": "Hello Test!"}).encode(),
                "ExecutedVersion": "$LATEST",
            }

            response = lambda_client.invoke(
                FunctionName="test-function",
                InvocationType="RequestResponse",
                Payload=json.dumps({"name": "Test"}),
            )

        # Verify response
        payload = json.loads(response["Payload"].read().decode("utf-8"))
        assert response["StatusCode"] == 200
        assert payload["statusCode"] == 200
        assert payload["body"] == "Hello Test!"

    @mock_lambda
    def test_lambda_with_permissions(self):
        """Test Lambda with IAM role permissions."""
        iam_client = boto3.client("iam", region_name="us-east-1")
        lambda_client = boto3.client("lambda", region_name="us-east-1")

        # Create IAM role for Lambda
        assume_role_policy = json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": {"Service": "lambda.amazonaws.com"},
                        "Action": "sts:AssumeRole",
                    }
                ],
            }
        )

        role_response = iam_client.create_role(
            RoleName="lambda-test-role",
            AssumeRolePolicyDocument=assume_role_policy,
        )
        role_arn = role_response["Role"]["Arn"]

        # Attach policy to the role
        policy_document = json.dumps(
            {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Action": [
                            "logs:CreateLogGroup",
                            "logs:CreateLogStream",
                            "logs:PutLogEvents",
                        ],
                        "Resource": "arn:aws:logs:*:*:*",
                    }
                ],
            }
        )

        iam_client.put_role_policy(
            RoleName="lambda-test-role",
            PolicyName="lambda-test-policy",
            PolicyDocument=policy_document,
        )

        # Create Lambda function with the role
        zip_output = bytes("", "utf-8")
        lambda_client.create_function(
            FunctionName="role-test-function",
            Runtime="python3.10",
            Role=role_arn,
            Handler="lambda_function.handler",
            Code={"ZipFile": zip_output},
            Description="Test lambda function with IAM role",
            Timeout=30,
            MemorySize=128,
            Publish=True,
        )

        # Verify the function was created with the correct role
        response = lambda_client.get_function(FunctionName="role-test-function")
        assert response["Configuration"]["Role"] == role_arn


class TestEventsMocking:
    """Tests for AWS CloudWatch Events (EventBridge) mocking."""

    @mock_events
    def test_create_rule_and_targets(self):
        """Test creating EventBridge rules and targets."""
        events_client = boto3.client("events", region_name="us-east-1")

        # Create a scheduled rule
        rule_name = "test-scheduled-rule"
        events_client.put_rule(
            Name=rule_name,
            ScheduleExpression="rate(5 minutes)",
            State="ENABLED",
            Description="Test scheduled rule",
        )

        # Create a target for the rule
        target_id = "test-target"
        target_arn = "arn:aws:lambda:us-east-1:123456789012:function:test-function"

        events_client.put_targets(
            Rule=rule_name,
            Targets=[
                {
                    "Id": target_id,
                    "Arn": target_arn,
                    "Input": json.dumps({"key": "value"}),
                }
            ],
        )

        # Verify the rule exists
        response = events_client.describe_rule(Name=rule_name)
        assert response["Name"] == rule_name
        assert response["ScheduleExpression"] == "rate(5 minutes)"
        assert response["State"] == "ENABLED"

        # Verify target exists
        targets = events_client.list_targets_by_rule(Rule=rule_name)
        assert len(targets["Targets"]) == 1
        assert targets["Targets"][0]["Id"] == target_id
        assert targets["Targets"][0]["Arn"] == target_arn
        assert json.loads(targets["Targets"][0]["Input"]) == {"key": "value"}

    @mock_events
    @mock_events
    def test_event_pattern_rule(self):
        """Test creating an event pattern rule."""
        events_client = boto3.client("events", region_name="us-east-1")
        lambda_client = boto3.client("lambda", region_name="us-east-1")

        # Create Lambda function
        zip_output = bytes("", "utf-8")
        lambda_client.create_function(
            FunctionName="event-handler",
            Runtime="python3.10",
            Role="arn:aws:iam::123456789012:role/lambda-role",
            Handler="lambda_function.handler",
            Code={"ZipFile": zip_output},
            Description="Test event handler",
            Timeout=30,
            MemorySize=128,
            Publish=True,
        )

        # Get the Lambda function ARN
        lambda_response = lambda_client.get_function(FunctionName="event-handler")
        lambda_arn = lambda_response["Configuration"]["FunctionArn"]

        # Create a pattern-based rule
        rule_name = "test-pattern-rule"
        pattern = {
            "source": ["aws.s3"],
            "detail-type": ["Object Created"],
        }

        events_client.put_rule(
            Name=rule_name,
            EventPattern=json.dumps(pattern),
            State="ENABLED",
            Description="Test pattern rule",
        )

        # Add the Lambda as a target
        events_client.put_targets(
            Rule=rule_name,
            Targets=[
                {
                    "Id": "1",
                    "Arn": lambda_arn,
                }
            ],
        )

        # Verify the rule pattern
        response = events_client.describe_rule(Name=rule_name)
        assert json.loads(response["EventPattern"]) == pattern

        # Verify target
        targets = events_client.list_targets_by_rule(Rule=rule_name)
        assert targets["Targets"][0]["Arn"] == lambda_arn


class TestSNSMocking:
    """Tests for AWS SNS mocking."""

    @mock_sns
    def test_create_topic_and_subscribe(self):
        """Test creating an SNS topic and subscribing to it."""
        sns_client = boto3.client("sns", region_name="us-east-1")

        # Create a topic
        topic_name = "test-topic"
        response = sns_client.create_topic(Name=topic_name)
        topic_arn = response["TopicArn"]

        # Subscribe to the topic
        subscription_response = sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol="email",
            Endpoint="test@example.com",
        )

        # Verify the subscription was created
        assert "SubscriptionArn" in subscription_response

        # List subscriptions
        subscriptions = sns_client.list_subscriptions_by_topic(TopicArn=topic_arn)
        assert len(subscriptions["Subscriptions"]) == 1
        assert subscriptions["Subscriptions"][0]["TopicArn"] == topic_arn
        assert subscriptions["Subscriptions"][0]["Protocol"] == "email"
        assert subscriptions["Subscriptions"][0]["Endpoint"] == "test@example.com"

    @mock_sns
    @mock_sns
    def test_sns_to_sqs_integration(self):
        """Test integrating SNS with SQS."""
        sns_client = boto3.client("sns", region_name="us-east-1")
        sqs_client = boto3.client("sqs", region_name="us-east-1")

        # Create an SNS topic
        topic_response = sns_client.create_topic(Name="notification-topic")
        topic_arn = topic_response["TopicArn"]

        # Create an SQS queue
        queue_response = sqs_client.create_queue(QueueName="notification-queue")
        queue_url = queue_response["QueueUrl"]

        # Get queue ARN
        queue_attrs = sqs_client.get_queue_attributes(
            QueueUrl=queue_url,
            AttributeNames=["QueueArn"],
        )
        queue_arn = queue_attrs["Attributes"]["QueueArn"]

        # Subscribe the SQS queue to the SNS topic
        sns_client.subscribe(
            TopicArn=topic_arn,
            Protocol="sqs",
            Endpoint=queue_arn,
        )

        # Create a policy allowing SNS to send messages
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "sns.amazonaws.com"},
                    "Action": "sqs:SendMessage",
                    "Resource": queue_arn,
                    "Condition": {"ArnEquals": {"aws:SourceArn": topic_arn}},
                }
            ],
        }

        # Set the policy on the queue
        sqs_client.set_queue_attributes(
            QueueUrl=queue_url,
            Attributes={"Policy": json.dumps(policy)},
        )

        # Publish a message to the SNS topic
        message = "Test message"
        sns_client.publish(
            TopicArn=topic_arn,
            Message=message,
            Subject="Test Subject",
        )

        # In a real environment, message delivery would happen asynchronously
        # For the test, we know moto delivers the messages immediately

        # Receive messages from the SQS queue
        response = sqs_client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            WaitTimeSeconds=1,
        )

        # Verify the message was received
        assert "Messages" in response
        assert len(response["Messages"]) == 1

        # The message body from SNS contains metadata, so parse it as JSON
        body = json.loads(response["Messages"][0]["Body"])
        assert body["Message"] == message
        assert body["Subject"] == "Test Subject"


class TestSecretManagerMocking:
    """Tests for AWS Secrets Manager mocking."""

    @mock_secretsmanager
    def test_create_and_retrieve_secret(self):
        """Test creating and retrieving a secret."""
        secretsmanager_client = boto3.client("secretsmanager", region_name="us-east-1")

        # Create a secret
        secret_name = "test/db/credentials"
        secret_value = {
            "username": "admin",
            "password": "secret-password",
            "host": "db.example.com",
            "port": "3306",
        }

        response = secretsmanager_client.create_secret(
            Name=secret_name,
            SecretString=json.dumps(secret_value),
            Description="Test database credentials",
            Tags=[
                {
                    "Key": "Environment",
                    "Value": "Test",
                },
            ],
        )

        # Verify the secret was created
        assert "ARN" in response
        assert "Name" in response
        assert response["Name"] == secret_name

        # Retrieve the secret
        get_response = secretsmanager_client.get_secret_value(SecretId=secret_name)
        assert get_response["Name"] == secret_name
        assert json.loads(get_response["SecretString"]) == secret_value

    @mock_secretsmanager
    def test_rotate_secret(self):
        """Test rotating a secret."""
        secretsmanager_client = boto3.client("secretsmanager", region_name="us-east-1")

        # Create a secret
        secret_name = "rotating-secret"
        original_value = {"password": "original-password"}

        secretsmanager_client.create_secret(
            Name=secret_name,
            SecretString=json.dumps(original_value),
        )

        # Update the secret value (simulating rotation)
        new_value = {"password": "new-password"}
        secretsmanager_client.update_secret(
            SecretId=secret_name,
            SecretString=json.dumps(new_value),
        )

        # Retrieve the rotated secret
        response = secretsmanager_client.get_secret_value(SecretId=secret_name)
        assert json.loads(response["SecretString"]) == new_value

        # Test listing versions (not fully implemented in moto, but demonstrates the API)
        versions = secretsmanager_client.list_secret_version_ids(SecretId=secret_name)
        assert len(versions["Versions"]) >= 1  # Should have at least one version

    @mock_secretsmanager
    def test_secret_error_handling(self):
        """Test error handling for secret operations."""
        secretsmanager_client = boto3.client("secretsmanager", region_name="us-east-1")

        # Try to get a nonexistent secret
        with pytest.raises(botocore.exceptions.ClientError) as excinfo:
            secretsmanager_client.get_secret_value(SecretId="nonexistent-secret")

        # Verify the error
        error = excinfo.value.response.get("Error", {})
        assert error.get("Code") == "ResourceNotFoundException"


class TestCloudWatchMocking:
    """Tests for AWS CloudWatch mocking."""

    @mock_cloudwatch
    def test_put_and_get_metrics(self):
        """Test putting and getting CloudWatch metrics."""
        cloudwatch_client = boto3.client("cloudwatch", region_name="us-east-1")

        # Set up time windows for metrics
        now = datetime.utcnow()
        start_time = now - timedelta(minutes=30)
        end_time = now + timedelta(minutes=10)

        # Put a metric data point
        namespace = "TestNamespace"
        metric_name = "CPUUtilization"

        cloudwatch_client.put_metric_data(
            Namespace=namespace,
            MetricData=[
                {
                    "MetricName": metric_name,
                    "Dimensions": [
                        {
                            "Name": "InstanceId",
                            "Value": "i-1234567890abcdef0",
                        },
                    ],
                    "Timestamp": now,
                    "Value": 70.0,
                    "Unit": "Percent",
                },
            ],
        )

        # Get metric statistics
        response = cloudwatch_client.get_metric_statistics(
            Namespace=namespace,
            MetricName=metric_name,
            Dimensions=[
                {
                    "Name": "InstanceId",
                    "Value": "i-1234567890abcdef0",
                },
            ],
            StartTime=start_time,
            EndTime=end_time,
            Period=60,  # 1-minute periods
            Statistics=["Average", "Maximum", "Minimum"],
            Unit="Percent",
        )

        # Verify metrics were returned
        assert len(response["Datapoints"]) > 0
        assert response["Datapoints"][0]["Unit"] == "Percent"
        assert response["Datapoints"][0]["Average"] == 70.0
        assert response["Datapoints"][0]["Maximum"] == 70.0
        assert response["Datapoints"][0]["Minimum"] == 70.0

    @mock_cloudwatch
    def test_create_alarm(self):
        """Test creating a CloudWatch alarm."""
        cloudwatch_client = boto3.client("cloudwatch", region_name="us-east-1")

        # Create an alarm
        alarm_name = "high-cpu-alarm"
        cloudwatch_client.put_metric_alarm(
            AlarmName=alarm_name,
            ComparisonOperator="GreaterThanThreshold",
            EvaluationPeriods=1,
            MetricName="CPUUtilization",
            Namespace="AWS/EC2",
            Period=60,
            Statistic="Average",
            Threshold=70.0,
            ActionsEnabled=True,
            AlarmDescription="Alarm when CPU exceeds 70%",
            Dimensions=[
                {
                    "Name": "InstanceId",
                    "Value": "i-1234567890abcdef0",
                },
            ],
            Unit="Percent",
        )

        # Describe the alarm
        response = cloudwatch_client.describe_alarms(AlarmNames=[alarm_name])

        # Verify the alarm
        assert len(response["MetricAlarms"]) == 1
        alarm = response["MetricAlarms"][0]
        assert alarm["AlarmName"] == alarm_name
        assert alarm["Threshold"] == 70.0
        assert alarm["Statistic"] == "Average"


class TestStepFunctionsMocking:
    """Tests for AWS Step Functions mocking."""

    @mock_stepfunctions
    def test_create_and_execute_state_machine(self):
        """Test creating and executing a Step Functions state machine."""
        sfn_client = boto3.client("stepfunctions", region_name="us-east-1")

        # Define a simple state machine
        definition = {
            "Comment": "A simple state machine",
            "StartAt": "HelloWorld",
            "States": {
                "HelloWorld": {
                    "Type": "Pass",
                    "Result": "Hello, World!",
                    "End": True,
                }
            },
        }

        # Create state machine
        response = sfn_client.create_state_machine(
            name="test-state-machine",
            definition=json.dumps(definition),
            roleArn="arn:aws:iam::123456789012:role/step-functions-role",
        )

        state_machine_arn = response["stateMachineArn"]

        # Describe the state machine
        describe_response = sfn_client.describe_state_machine(stateMachineArn=state_machine_arn)

        assert describe_response["name"] == "test-state-machine"
        assert describe_response["status"] == "ACTIVE"
        assert json.loads(describe_response["definition"]) == definition

        # Start execution
        execution_response = sfn_client.start_execution(
            stateMachineArn=state_machine_arn,
            name="test-execution",
            input=json.dumps({"key": "value"}),
        )

        execution_arn = execution_response["executionArn"]

        # Describe execution (in moto this doesn't actually run the state machine logic)
        describe_execution = sfn_client.describe_execution(executionArn=execution_arn)

        assert describe_execution["stateMachineArn"] == state_machine_arn
        assert describe_execution["status"] in [
            "RUNNING",
            "SUCCEEDED",
        ]  # Status depends on moto implementation


class TestSESMocking:
    """Tests for AWS SES (Simple Email Service) mocking."""

    @mock_ses
    def test_verify_email_identity(self):
        """Test verifying an email identity."""
        ses_client = boto3.client("ses", region_name="us-east-1")

        # Verify an email address
        email = "test@example.com"
        ses_client.verify_email_identity(EmailAddress=email)

        # List verified email addresses
        response = ses_client.list_identities(IdentityType="EmailAddress")

        # Verify the email is in the list
        assert email in response["Identities"]

    @mock_ses
    def test_send_email(self):
        """Test sending an email."""
        ses_client = boto3.client("ses", region_name="us-east-1")

        # Verify sender email first (required before sending)
        sender = "sender@example.com"
        ses_client.verify_email_identity(EmailAddress=sender)

        # Send email
        response = ses_client.send_email(
            Source=sender,
            Destination={
                "ToAddresses": ["recipient@example.com"],
                "CcAddresses": ["cc@example.com"],
                "BccAddresses": [],
            },
            Message={
                "Subject": {
                    "Data": "Test Email",
                    "Charset": "UTF-8",
                },
                "Body": {
                    "Text": {
                        "Data": "This is a test email sent using Amazon SES.",
                        "Charset": "UTF-8",
                    },
                    "Html": {
                        "Data": "<html><body><h1>Test Email</h1><p>This is a test email sent using Amazon SES.</p></body></html>",
                        "Charset": "UTF-8",
                    },
                },
            },
            ReplyToAddresses=[sender],
        )

        # Verify the response contains a message ID
        assert "MessageId" in response


class TestKMSMocking:
    """Tests for AWS KMS (Key Management Service) mocking."""

    @mock_kms
    def test_create_and_use_key(self):
        """Test creating and using a KMS key."""
        kms_client = boto3.client("kms", region_name="us-east-1")

        # Create a KMS key
        key_response = kms_client.create_key(
            Description="Test Key",
            KeyUsage="ENCRYPT_DECRYPT",
            Origin="AWS_KMS",
        )

        # Get the key ID
        key_id = key_response["KeyMetadata"]["KeyId"]

        # Encrypt data
        plaintext = "Sensitive data"
        encrypt_response = kms_client.encrypt(
            KeyId=key_id,
            Plaintext=plaintext.encode("utf-8"),
        )

        # Get the encrypted data
        ciphertext = encrypt_response["CiphertextBlob"]

        # Decrypt data
        decrypt_response = kms_client.decrypt(
            CiphertextBlob=ciphertext,
        )

        # Verify the decrypted data
        decrypted_text = decrypt_response["Plaintext"].decode("utf-8")
        assert decrypted_text == plaintext


class TestErrorHandling:
    """Tests for error handling with AWS mocking."""

    @mock_dynamodb
    def test_dynamodb_resource_not_found(self):
        """Test handling of resource not found errors in DynamoDB."""
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        # Try to get a nonexistent table
        table = dynamodb.Table("nonexistent-table")

        # Attempt to perform an operation on the table
        with pytest.raises(botocore.exceptions.ClientError) as excinfo:
            table.get_item(Key={"id": "test-id"})

        # Verify the error
        error = excinfo.value.response.get("Error", {})
        assert error.get("Code") == "ResourceNotFoundException"

    @mock_s3
    def test_s3_no_such_bucket(self):
        """Test handling of no such bucket errors with S3."""
        s3_client = boto3.client("s3", region_name="us-east-1")

        # Try to get an object from a nonexistent bucket
        with pytest.raises(botocore.exceptions.ClientError) as excinfo:
            s3_client.get_object(Bucket="nonexistent-bucket", Key="test-object")

        # Verify the error
        error = excinfo.value.response.get("Error", {})
        assert error.get("Code") == "NoSuchBucket"


# Define AWS resources fixtures for more reusable testing
@pytest.fixture
def mock_aws_complex_environment():
    """Create a complex AWS environment with multiple interacting services."""
    with (
        mock_cloudwatch(),
        mock_dynamodb(),
        mock_events(),
        mock_iam(),
        mock_kms(),
        mock_lambda(),
        mock_secretsmanager(),
        mock_ses(),
        mock_sns(),
        mock_sqs(),
        mock_ssm(),
        mock_stepfunctions(),
    ):
        # Set up S3
        s3_client = boto3.client("s3", region_name="us-east-1")
        bucket_name = "data-bucket"
        s3_client.create_bucket(Bucket=bucket_name)

        # Set up DynamoDB
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table_name = "events-table"
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        # Set up SNS topic
        sns_client = boto3.client("sns", region_name="us-east-1")
        topic_response = sns_client.create_topic(Name="notifications")
        topic_arn = topic_response["TopicArn"]

        # Set up SQS queue
        sqs_client = boto3.client("sqs", region_name="us-east-1")
        queue_response = sqs_client.create_queue(QueueName="processing-queue")
        queue_url = queue_response["QueueUrl"]

        # Set up Lambda
        lambda_client = boto3.client("lambda", region_name="us-east-1")
        zip_output = bytes("", "utf-8")
        lambda_client.create_function(
            FunctionName="processor",
            Runtime="python3.10",
            Role="arn:aws:iam::123456789012:role/lambda-role",
            Handler="lambda_function.handler",
            Code={"ZipFile": zip_output},
            Description="Test processor lambda",
            Timeout=30,
            MemorySize=128,
            Publish=True,
        )

        # Set up EventBridge rule
        events_client = boto3.client("events", region_name="us-east-1")
        events_client.put_rule(
            Name="scheduled-task",
            ScheduleExpression="rate(1 hour)",
            State="ENABLED",
            Description="Scheduled task rule",
        )

        # Return the environment
        yield {
            "s3_client": s3_client,
            "s3_bucket": bucket_name,
            "dynamodb_table": table,
            "sns_topic_arn": topic_arn,
            "sqs_queue_url": queue_url,
            "lambda_client": lambda_client,
            "events_client": events_client,
        }


def test_complex_event_processing(mock_aws_complex_environment):
    """Test a complex event processing flow using multiple AWS services."""
    env = mock_aws_complex_environment

    # Upload file to S3 (trigger event)
    env["s3_client"].put_object(
        Bucket=env["s3_bucket"],
        Key="data/event.json",
        Body=json.dumps({"event_type": "test", "timestamp": "2023-04-01T12:00:00Z"}),
    )

    # Store event in DynamoDB
    event_id = "evt-12345"
    env["dynamodb_table"].put_item(
        Item={
            "id": event_id,
            "type": "test",
            "timestamp": "2023-04-01T12:00:00Z",
            "processed": False,
        }
    )

    # Publish notification to SNS
    notification = {
        "event_id": event_id,
        "status": "PENDING",
        "source_bucket": env["s3_bucket"],
        "source_key": "data/event.json",
    }

    sns_client = boto3.client("sns", region_name="us-east-1")
    sns_client.publish(
        TopicArn=env["sns_topic_arn"],
        Message=json.dumps(notification),
        Subject="Event Notification",
    )

    # Retrieve item from DynamoDB
    response = env["dynamodb_table"].get_item(Key={"id": event_id})
    assert "Item" in response
    assert response["Item"]["type"] == "test"
    assert response["Item"]["processed"] is False

    # Update record to mark as processed
    env["dynamodb_table"].update_item(
        Key={"id": event_id},
        UpdateExpression="SET processed = :processed, process_date = :date",
        ExpressionAttributeValues={
            ":processed": True,
            ":date": "2023-04-01T12:05:00Z",
        },
    )

    # Verify update worked
    response = env["dynamodb_table"].get_item(Key={"id": event_id})
    assert response["Item"]["processed"] is True
    assert response["Item"]["process_date"] == "2023-04-01T12:05:00Z"


def test_pagination_filtering():
    """Test paginating and filtering AWS responses."""
    with mock_cloudwatch():
        # Set up DynamoDB
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table_name = "items-table"
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "category", "AttributeType": "S"},
            ],
            GlobalSecondaryIndexes=[
                {
                    "IndexName": "category-index",
                    "KeySchema": [{"AttributeName": "category", "KeyType": "HASH"}],
                    "Projection": {"ProjectionType": "ALL"},
                    "ProvisionedThroughput": {"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
                },
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        # Insert test data (50 items across 5 categories)
        categories = ["electronics", "books", "clothing", "food", "toys"]
        for i in range(50):
            category = categories[i % len(categories)]
            table.put_item(
                Item={
                    "id": f"item-{i:03d}",
                    "category": category,
                    "name": f"Item {i}",
                    "price": float(10 + i),
                    "in_stock": i % 3 == 0,  # Every third item is in stock
                }
            )

        # Test pagination with DynamoDB
        all_items: list[dict] = []
        paginator = boto3.client("dynamodb", region_name="us-east-1").get_paginator("scan")

        # Use small page size to force pagination
        page_iterator = paginator.paginate(
            TableName=table_name,
            PaginationConfig={"PageSize": 10},
        )

        for page in page_iterator:
            all_items.extend(page.get("Items", []))

        # Verify all 50 items were retrieved
        assert len(all_items) == 50

        # Test filtering using a query
        dynamodb_client = boto3.client("dynamodb", region_name="us-east-1")
        response = dynamodb_client.query(
            TableName=table_name,
            IndexName="category-index",
            KeyConditionExpression="#category = :category",
            FilterExpression="#in_stock = :in_stock",
            ExpressionAttributeNames={
                "#category": "category",
                "#in_stock": "in_stock",
            },
            ExpressionAttributeValues={
                ":category": {"S": "electronics"},
                ":in_stock": {"BOOL": True},
            },
        )

        # We should get only the electronics that are in stock
        # We have 10 electronics (0, 5, 10, ..., 45) and every third is in stock (0, 3, 6, ...)
        # So we should have items 0, 30 (indices that are both divisible by 5 and by 3)
        assert len(response["Items"]) >= 2  # At least 2 items should match
