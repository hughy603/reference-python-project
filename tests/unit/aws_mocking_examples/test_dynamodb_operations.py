"""
Example unit tests demonstrating DynamoDB mocking with Moto's latest mock_aws decorator.

This module shows how to effectively use Moto's mock_aws decorator
to test code that interacts with AWS DynamoDB.
"""

import decimal
import json
from typing import Any

import boto3
import pytest
from botocore.exceptions import ClientError
from moto import mock_aws


# Helper class for DynamoDB decimal encoding/decoding
class DecimalEncoder(json.JSONEncoder):
    """Helper class to convert Decimal types to integers for JSON serialization."""

    def default(self, obj: Any) -> Any:
        """Convert Decimal to int for JSON serialization."""
        if isinstance(obj, decimal.Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super().default(obj)


class TestDynamoDBOperations:
    """Test suite demonstrating DynamoDB operations with moto's mock_aws decorator."""

    @mock_aws
    def test_create_table(self) -> None:
        """Test creating a DynamoDB table."""
        # Arrange
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table_name = "test-table"

        # Act
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "id", "KeyType": "HASH"},  # Partition key
                {"AttributeName": "timestamp", "KeyType": "RANGE"},  # Sort key
            ],
            AttributeDefinitions=[
                {"AttributeName": "id", "AttributeType": "S"},
                {"AttributeName": "timestamp", "AttributeType": "N"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        # Wait until table is created
        table.meta.client.get_waiter("table_exists").wait(TableName=table_name)

        # Assert
        assert table.table_status == "ACTIVE"

        # Check table definition
        table_description = table.meta.client.describe_table(TableName=table_name)
        assert table_description["Table"]["TableName"] == table_name
        assert len(table_description["Table"]["KeySchema"]) == 2

    @mock_aws
    def test_put_and_get_item(self) -> None:
        """Test putting and retrieving an item from DynamoDB."""
        # Arrange
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table_name = "test-table"

        # Create table
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        # Act - Put item
        item = {
            "id": "item-1",
            "name": "Test Item",
            "count": 100,
            "metadata": {"category": "test", "active": True},
        }
        table.put_item(Item=item)

        # Act - Get item
        response = table.get_item(Key={"id": "item-1"})

        # Assert
        assert "Item" in response
        assert response["Item"] == item

    @mock_aws
    def test_update_item(self) -> None:
        """Test updating an item in DynamoDB."""
        # Arrange
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table_name = "test-table"

        # Create table
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        # Create initial item
        table.put_item(Item={"id": "item-1", "name": "Original Name", "count": 100})

        # Act - Update item
        table.update_item(
            Key={"id": "item-1"},
            UpdateExpression="SET #name = :new_name, #count = #count + :increment",
            ExpressionAttributeNames={"#name": "name", "#count": "count"},
            ExpressionAttributeValues={":new_name": "Updated Name", ":increment": 50},
            ReturnValues="UPDATED_NEW",
        )

        # Get updated item
        response = table.get_item(Key={"id": "item-1"})

        # Assert
        assert "Item" in response
        assert response["Item"]["name"] == "Updated Name"
        assert response["Item"]["count"] == 150

    @mock_aws
    def test_delete_item(self) -> None:
        """Test deleting an item from DynamoDB."""
        # Arrange
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table_name = "test-table"

        # Create table
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        # Create item
        table.put_item(Item={"id": "item-to-delete", "data": "some data"})

        # Verify item exists
        response = table.get_item(Key={"id": "item-to-delete"})
        assert "Item" in response

        # Act - Delete item
        table.delete_item(Key={"id": "item-to-delete"})

        # Assert
        response = table.get_item(Key={"id": "item-to-delete"})
        assert "Item" not in response

    @mock_aws
    def test_batch_write(self) -> None:
        """Test batch writing items to DynamoDB."""
        # Arrange
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table_name = "batch-table"

        # Create table
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        # Act - Batch write items
        with table.batch_writer() as batch:
            for i in range(10):
                batch.put_item(
                    Item={"id": f"batch-item-{i}", "data": f"Batch data {i}", "number": i}
                )

        # Assert
        for i in range(10):
            response = table.get_item(Key={"id": f"batch-item-{i}"})
            assert "Item" in response
            assert response["Item"]["number"] == i

    @mock_aws
    def test_query(self) -> None:
        """Test querying items from DynamoDB."""
        # Arrange
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table_name = "query-table"

        # Create table with composite key
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {"AttributeName": "user_id", "KeyType": "HASH"},  # Partition key
                {"AttributeName": "timestamp", "KeyType": "RANGE"},  # Sort key
            ],
            AttributeDefinitions=[
                {"AttributeName": "user_id", "AttributeType": "S"},
                {"AttributeName": "timestamp", "AttributeType": "N"},
            ],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        # Insert test data
        current_user = "user-123"
        for i in range(5):
            table.put_item(
                Item={
                    "user_id": current_user,
                    "timestamp": i,
                    "message": f"Message {i}",
                    "is_read": i % 2 == 0,  # Even items are read
                }
            )

        # Also add items for a different user
        for i in range(3):
            table.put_item(
                Item={"user_id": "other-user", "timestamp": i, "message": f"Other message {i}"}
            )

        # Act - Query for specific user items
        response = table.query(
            KeyConditionExpression="user_id = :user AND timestamp > :start_time",
            ExpressionAttributeValues={":user": current_user, ":start_time": 1},
        )

        # Assert
        assert "Items" in response
        assert len(response["Items"]) == 3  # Timestamps 2, 3, 4
        assert all(item["user_id"] == current_user for item in response["Items"])
        assert all(item["timestamp"] > 1 for item in response["Items"])

    @mock_aws
    def test_scan_with_filter(self) -> None:
        """Test scanning with filters in DynamoDB."""
        # Arrange
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table_name = "scan-table"

        # Create table
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        # Insert test data
        for i in range(20):
            table.put_item(
                Item={
                    "id": f"item-{i}",
                    "category": "A" if i < 10 else "B",
                    "value": i * 5,
                    "active": i % 2 == 0,  # Even items are active
                }
            )

        # Act - Scan with filter
        response = table.scan(
            FilterExpression="category = :cat AND active = :status AND #val > :min_val",
            ExpressionAttributeNames={
                "#val": "value"  # 'value' is a reserved word
            },
            ExpressionAttributeValues={":cat": "A", ":status": True, ":min_val": 20},
        )

        # Assert
        assert "Items" in response
        items = response["Items"]
        # Should only return category A, active items with value > 20
        assert all(item["category"] == "A" for item in items)
        assert all(item["active"] is True for item in items)
        assert all(item["value"] > 20 for item in items)

    @mock_aws
    def test_conditional_put(self) -> None:
        """Test conditional puts in DynamoDB."""
        # Arrange
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table_name = "conditional-table"

        # Create table
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        # Insert initial item
        table.put_item(Item={"id": "test-item", "version": 1, "data": "original data"})

        # Act - Conditional update with wrong condition (should fail)
        with pytest.raises(ClientError) as excinfo:
            table.put_item(
                Item={"id": "test-item", "version": 2, "data": "new data"},
                ConditionExpression="version = :expected_version",
                ExpressionAttributeValues={
                    ":expected_version": 5  # Wrong version
                },
            )

        # Assert
        assert "ConditionalCheckFailedException" in str(excinfo.value)

        # Act - Conditional update with correct condition (should succeed)
        table.put_item(
            Item={"id": "test-item", "version": 2, "data": "new data"},
            ConditionExpression="version = :expected_version",
            ExpressionAttributeValues={
                ":expected_version": 1  # Correct version
            },
        )

        # Verify update
        response = table.get_item(Key={"id": "test-item"})
        assert response["Item"]["version"] == 2
        assert response["Item"]["data"] == "new data"


# Example of a fixture-based approach for DynamoDB testing
class TestDynamoDBWithFixtures:
    """Test DynamoDB operations with pytest fixtures."""

    @pytest.fixture()
    def dynamodb_resource(self) -> Any:
        """Create a mocked DynamoDB resource."""
        with mock_aws():
            yield boto3.resource("dynamodb", region_name="us-east-1")

    @pytest.fixture()
    def products_table(self, dynamodb_resource: Any) -> Any:
        """Create a test products table."""
        table = dynamodb_resource.create_table(
            TableName="products",
            KeySchema=[{"AttributeName": "product_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "product_id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        # Wait until the table exists
        table.meta.client.get_waiter("table_exists").wait(TableName="products")
        return table

    def test_add_product(self, products_table: Any) -> None:
        """Test adding a product using fixtures."""
        # Arrange
        product = {
            "product_id": "prod-123",
            "name": "Test Product",
            "price": decimal.Decimal("19.99"),
            "stock": 100,
        }

        # Act
        products_table.put_item(Item=product)

        # Assert
        response = products_table.get_item(Key={"product_id": "prod-123"})
        assert "Item" in response

        # Convert decimal to float for comparison
        item = response["Item"]
        if isinstance(item["price"], decimal.Decimal):
            item["price"] = float(item["price"])

        expected = product.copy()
        expected["price"] = float(expected["price"])

        assert item["product_id"] == expected["product_id"]
        assert item["name"] == expected["name"]
        assert item["price"] == expected["price"]
        assert item["stock"] == expected["stock"]


# Example of a real-world business function using DynamoDB
class ProductRepository:
    """Repository for product data in DynamoDB."""

    def __init__(self, table_name: str, region: str = "us-east-1") -> None:
        """Initialize the repository."""
        self.dynamodb = boto3.resource("dynamodb", region_name=region)
        self.table = self.dynamodb.Table(table_name)

    def get_product(self, product_id: str) -> dict[str, Any] | None:
        """
        Get product by ID.

        Args:
            product_id: The product ID to retrieve

        Returns:
            The product data or None if not found
        """
        try:
            response = self.table.get_item(Key={"product_id": product_id})
            return response.get("Item")
        except ClientError:
            return None

    def save_product(self, product: dict[str, Any]) -> bool:
        """
        Save a product to DynamoDB.

        Args:
            product: The product data to save

        Returns:
            True if successful, False otherwise
        """
        try:
            if "product_id" not in product:
                return False

            self.table.put_item(Item=product)
            return True
        except ClientError:
            return False

    def update_stock(self, product_id: str, change: int) -> bool:
        """
        Update product stock level.

        Args:
            product_id: The product ID to update
            change: The amount to change stock (positive or negative)

        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.table.update_item(
                Key={"product_id": product_id},
                UpdateExpression="SET stock = stock + :change",
                ConditionExpression="stock + :change >= :min AND attribute_exists(product_id)",
                ExpressionAttributeValues={
                    ":change": change,
                    ":min": 0,  # Prevent negative stock
                },
                ReturnValues="UPDATED_NEW",
            )
            return "Attributes" in response
        except ClientError as e:
            if "ConditionalCheckFailedException" in str(e):
                # Out of stock or product doesn't exist
                return False
            raise


# Test for the business repository
class TestProductRepository:
    """Tests for ProductRepository class."""

    @mock_aws
    def test_product_repository(self) -> None:
        """Integration test for ProductRepository."""
        # Arrange - Create table
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
        table_name = "products-test"
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{"AttributeName": "product_id", "KeyType": "HASH"}],
            AttributeDefinitions=[{"AttributeName": "product_id", "AttributeType": "S"}],
            ProvisionedThroughput={"ReadCapacityUnits": 5, "WriteCapacityUnits": 5},
        )

        # Initialize repository
        repo = ProductRepository(table_name)

        # Test saving a product
        product = {
            "product_id": "laptop-15",
            "name": 'Laptop 15"',
            "description": "Powerful laptop for developers",
            "price": decimal.Decimal("999.99"),
            "stock": 10,
            "categories": ["electronics", "computers"],
        }

        # Act - Save product
        result = repo.save_product(product)

        # Assert
        assert result is True

        # Test retrieving a product
        retrieved = repo.get_product("laptop-15")
        assert retrieved is not None
        assert retrieved["name"] == 'Laptop 15"'
        assert retrieved["stock"] == 10

        # Test updating stock
        updated = repo.update_stock("laptop-15", -3)
        assert updated is True

        # Verify update
        retrieved = repo.get_product("laptop-15")
        assert retrieved["stock"] == 7

        # Test conditional failure (prevent negative stock)
        updated = repo.update_stock("laptop-15", -10)
        assert updated is False  # Should fail because stock would be negative

        # Verify stock unchanged
        retrieved = repo.get_product("laptop-15")
        assert retrieved["stock"] == 7  # Still 7, not -3
