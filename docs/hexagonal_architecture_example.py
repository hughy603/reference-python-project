"""
Hexagonal Architecture Example: Product Catalog System

This example demonstrates the implementation of a product catalog system
using the hexagonal architecture (ports and adapters) pattern.
"""

import abc
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import Protocol

# -------------------------------------------------------------------------
# DOMAIN LAYER
# -------------------------------------------------------------------------
# The core of our application with business logic and rules.
# This layer knows nothing about external concerns like databases or APIs.


@dataclass(frozen=True)
class ProductId:
    """Value object representing a product identifier."""

    value: str

    @classmethod
    def generate(cls) -> "ProductId":
        """Generate a new unique product ID."""
        return cls(str(uuid.uuid4()))

    def __str__(self) -> str:
        return self.value


@dataclass
class Product:
    """Entity representing a product in our catalog."""

    id: ProductId
    name: str
    description: str
    price: Decimal
    tags: set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime | None = None

    def __post_init__(self):
        """Validate the product when it's created."""
        self._validate()

    def _validate(self) -> None:
        """Validate product data according to domain rules."""
        if not self.name:
            raise ValueError("Product name cannot be empty")

        if self.price < Decimal("0.00"):
            raise ValueError("Product price cannot be negative")

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        price: Decimal | None = None,
        tags: set[str] | None = None,
    ) -> None:
        """Update product information."""
        if name is not None:
            self.name = name

        if description is not None:
            self.description = description

        if price is not None:
            self.price = price

        if tags is not None:
            self.tags = tags

        self.updated_at = datetime.now()
        self._validate()


class DomainException(Exception):
    """Base exception for all domain-related errors."""

    pass


class ProductNotFoundError(DomainException):
    """Raised when a product cannot be found."""

    pass


# Domain Service
class ProductDomainService:
    """Domain service with business logic related to products."""

    def calculate_discounted_price(self, product: Product, discount_percentage: Decimal) -> Decimal:
        """Calculate a discounted price for a product."""
        if discount_percentage < Decimal("0") or discount_percentage > Decimal("100"):
            raise ValueError("Discount percentage must be between 0 and 100")

        discount_factor = (Decimal("100") - discount_percentage) / Decimal("100")
        return (product.price * discount_factor).quantize(Decimal("0.01"))


# -------------------------------------------------------------------------
# PORTS LAYER
# -------------------------------------------------------------------------
# Interfaces that define how the domain interacts with the outside world.


# Output Ports (Secondary/Driven Ports)
class ProductRepository(abc.ABC):
    """Output port for product storage operations."""

    @abc.abstractmethod
    def save(self, product: Product) -> Product:
        """Save a product to the repository."""
        pass

    @abc.abstractmethod
    def get_by_id(self, product_id: ProductId) -> Product:
        """Get a product by its ID."""
        pass

    @abc.abstractmethod
    def get_all(self) -> list[Product]:
        """Get all products."""
        pass

    @abc.abstractmethod
    def delete(self, product_id: ProductId) -> None:
        """Delete a product by its ID."""
        pass

    @abc.abstractmethod
    def find_by_tags(self, tags: set[str]) -> list[Product]:
        """Find products with specified tags."""
        pass


class ProductEventPublisher(abc.ABC):
    """Output port for publishing product-related events."""

    @abc.abstractmethod
    def publish_product_created(self, product: Product) -> None:
        """Publish an event when a product is created."""
        pass

    @abc.abstractmethod
    def publish_product_updated(self, product: Product) -> None:
        """Publish an event when a product is updated."""
        pass

    @abc.abstractmethod
    def publish_product_deleted(self, product_id: ProductId) -> None:
        """Publish an event when a product is deleted."""
        pass


# Input Ports (Primary/Driving Ports)
class ProductService(Protocol):
    """Input port for product operations."""

    def create_product(
        self, name: str, description: str, price: Decimal, tags: set[str] | None = None
    ) -> Product:
        """Create a new product."""
        pass

    def get_product(self, product_id: str) -> Product:
        """Get a product by its ID."""
        pass

    def update_product(
        self,
        product_id: str,
        name: str | None = None,
        description: str | None = None,
        price: Decimal | None = None,
        tags: set[str] | None = None,
    ) -> Product:
        """Update an existing product."""
        pass

    def delete_product(self, product_id: str) -> None:
        """Delete a product."""
        pass

    def get_all_products(self) -> list[Product]:
        """Get all products."""
        pass

    def find_products_by_tags(self, tags: set[str]) -> list[Product]:
        """Find products with specified tags."""
        pass

    def calculate_product_discount(self, product_id: str, discount_percentage: Decimal) -> Decimal:
        """Calculate a discounted price for a product."""
        pass


# -------------------------------------------------------------------------
# APPLICATION LAYER
# -------------------------------------------------------------------------
# Coordinates the application workflow, connecting the domain to the ports.


@dataclass
class ProductDTO:
    """Data Transfer Object for products."""

    id: str
    name: str
    description: str
    price: Decimal
    tags: set[str]
    created_at: datetime
    updated_at: datetime | None = None

    @classmethod
    def from_entity(cls, product: Product) -> "ProductDTO":
        """Convert a domain entity to a DTO."""
        return cls(
            id=str(product.id),
            name=product.name,
            description=product.description,
            price=product.price,
            tags=product.tags.copy(),
            created_at=product.created_at,
            updated_at=product.updated_at,
        )


class ProductApplicationService:
    """Application service implementing the ProductService input port."""

    def __init__(
        self,
        product_repository: ProductRepository,
        product_event_publisher: ProductEventPublisher,
        product_domain_service: ProductDomainService,
    ):
        self.product_repository = product_repository
        self.product_event_publisher = product_event_publisher
        self.product_domain_service = product_domain_service

    def create_product(
        self, name: str, description: str, price: Decimal, tags: set[str] | None = None
    ) -> Product:
        """Create a new product."""
        product_id = ProductId.generate()
        product = Product(
            id=product_id, name=name, description=description, price=price, tags=tags or set()
        )

        saved_product = self.product_repository.save(product)
        self.product_event_publisher.publish_product_created(saved_product)

        return saved_product

    def get_product(self, product_id: str) -> Product:
        """Get a product by its ID."""
        try:
            return self.product_repository.get_by_id(ProductId(product_id))
        except Exception as e:
            raise ProductNotFoundError(f"Product with ID {product_id} not found") from e

    def update_product(
        self,
        product_id: str,
        name: str | None = None,
        description: str | None = None,
        price: Decimal | None = None,
        tags: set[str] | None = None,
    ) -> Product:
        """Update an existing product."""
        product = self.get_product(product_id)
        product.update(name, description, price, tags)

        updated_product = self.product_repository.save(product)
        self.product_event_publisher.publish_product_updated(updated_product)

        return updated_product

    def delete_product(self, product_id: str) -> None:
        """Delete a product."""
        product_id_obj = ProductId(product_id)
        # Verify product exists
        self.product_repository.get_by_id(product_id_obj)

        self.product_repository.delete(product_id_obj)
        self.product_event_publisher.publish_product_deleted(product_id_obj)

    def get_all_products(self) -> list[Product]:
        """Get all products."""
        return self.product_repository.get_all()

    def find_products_by_tags(self, tags: set[str]) -> list[Product]:
        """Find products with specified tags."""
        return self.product_repository.find_by_tags(tags)

    def calculate_product_discount(self, product_id: str, discount_percentage: Decimal) -> Decimal:
        """Calculate a discounted price for a product."""
        product = self.get_product(product_id)
        return self.product_domain_service.calculate_discounted_price(product, discount_percentage)


# -------------------------------------------------------------------------
# ADAPTERS LAYER
# -------------------------------------------------------------------------
# Implementations of the ports for specific technologies.


# Secondary Adapters (Output/Driven Adapters)
class InMemoryProductRepository(ProductRepository):
    """In-memory implementation of the ProductRepository."""

    def __init__(self):
        self.products: dict[str, Product] = {}

    def save(self, product: Product) -> Product:
        """Save a product to the repository."""
        self.products[str(product.id)] = product
        return product

    def get_by_id(self, product_id: ProductId) -> Product:
        """Get a product by its ID."""
        product = self.products.get(str(product_id))
        if not product:
            raise ProductNotFoundError(f"Product with ID {product_id} not found")
        return product

    def get_all(self) -> list[Product]:
        """Get all products."""
        return list(self.products.values())

    def delete(self, product_id: ProductId) -> None:
        """Delete a product by its ID."""
        if str(product_id) not in self.products:
            raise ProductNotFoundError(f"Product with ID {product_id} not found")
        del self.products[str(product_id)]

    def find_by_tags(self, tags: set[str]) -> list[Product]:
        """Find products with specified tags."""
        return [product for product in self.products.values() if tags.intersection(product.tags)]


class ConsoleProductEventPublisher(ProductEventPublisher):
    """Console implementation of the ProductEventPublisher."""

    def publish_product_created(self, product: Product) -> None:
        """Publish an event when a product is created."""
        print(f"EVENT: Product created - {product.id}: {product.name}")

    def publish_product_updated(self, product: Product) -> None:
        """Publish an event when a product is updated."""
        print(f"EVENT: Product updated - {product.id}: {product.name}")

    def publish_product_deleted(self, product_id: ProductId) -> None:
        """Publish an event when a product is deleted."""
        print(f"EVENT: Product deleted - {product_id}")


# Primary Adapters (Input/Driving Adapters)
class ProductCLIAdapter:
    """Command-line interface adapter for the product service."""

    def __init__(self, product_service: ProductService):
        self.product_service = product_service

    def create_product(
        self, name: str, description: str, price: str, tags: str = ""
    ) -> dict[str, str | list[str]]:
        """Create a new product via CLI."""
        tag_set = {tag.strip() for tag in tags.split(",")} if tags else set()

        try:
            product = self.product_service.create_product(
                name=name, description=description, price=Decimal(price), tags=tag_set
            )

            return {
                "status": "success",
                "message": f"Product created with ID: {product.id}",
                "product_id": str(product.id),
            }
        except ValueError as e:
            return {"status": "error", "message": str(e)}

    def get_product(self, product_id: str) -> dict[str, str | dict]:
        """Get a product by its ID via CLI."""
        try:
            product = self.product_service.get_product(product_id)
            dto = ProductDTO.from_entity(product)

            return {
                "status": "success",
                "product": {
                    "id": dto.id,
                    "name": dto.name,
                    "description": dto.description,
                    "price": str(dto.price),
                    "tags": list(dto.tags),
                    "created_at": dto.created_at.isoformat(),
                    "updated_at": dto.updated_at.isoformat() if dto.updated_at else None,
                },
            }
        except ProductNotFoundError as e:
            return {"status": "error", "message": str(e)}


# REST API Adapter Example (using FastAPI)
"""
from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide

router = APIRouter(prefix="/products", tags=["products"])

@router.post("/")
@inject
def create_product(
    request: CreateProductRequest,
    product_service: ProductService = Depends(Provide[Container.product_service])
):
    try:
        product = product_service.create_product(
            name=request.name,
            description=request.description,
            price=Decimal(request.price),
            tags=set(request.tags) if request.tags else set()
        )
        return ProductDTO.from_entity(product)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
"""


# -------------------------------------------------------------------------
# DEPENDENCY INJECTION
# -------------------------------------------------------------------------
# Wiring everything together while maintaining the direction of dependencies.


class Container:
    """Simple dependency injection container."""

    def __init__(self):
        # Create instances of domain services
        self.product_domain_service = ProductDomainService()

        # Create instances of secondary adapters
        self.product_repository = InMemoryProductRepository()
        self.product_event_publisher = ConsoleProductEventPublisher()

        # Create instances of application services
        self.product_service = ProductApplicationService(
            product_repository=self.product_repository,
            product_event_publisher=self.product_event_publisher,
            product_domain_service=self.product_domain_service,
        )

        # Create instances of primary adapters
        self.product_cli = ProductCLIAdapter(self.product_service)


# -------------------------------------------------------------------------
# USAGE EXAMPLE
# -------------------------------------------------------------------------


def main():
    """Main function demonstrating the usage of the hexagonal architecture."""
    # Initialize the container
    container = Container()

    # Use the CLI adapter to interact with the application
    print("\n=== Creating Products ===")
    result1 = container.product_cli.create_product(
        name="Laptop XPS 15",
        description="High-performance laptop for developers",
        price="1599.99",
        tags="electronics,computers,premium",
    )
    print(f"Result: {result1}")

    result2 = container.product_cli.create_product(
        name="Wireless Mouse",
        description="Ergonomic wireless mouse",
        price="49.99",
        tags="electronics,accessories",
    )
    print(f"Result: {result2}")

    # Invalid product (negative price)
    result3 = container.product_cli.create_product(
        name="Invalid Product", description="This product has a negative price", price="-10.00"
    )
    print(f"Result: {result3}")

    print("\n=== Retrieving Products ===")
    if result1["status"] == "success":
        product_id = result1["product_id"]
        get_result = container.product_cli.get_product(product_id)
        print(f"Retrieved product: {get_result}")

    # Directly access application service for more complex operations
    print("\n=== Using Application Service Directly ===")
    # Calculate discount
    if result1["status"] == "success":
        product_id = result1["product_id"]
        discounted_price = container.product_service.calculate_product_discount(
            product_id, Decimal("15.0")
        )
        print(f"Discounted price (15% off): ${discounted_price}")

    # Find products by tags
    products_with_electronics_tag = container.product_service.find_products_by_tags({"electronics"})
    print(f"Found {len(products_with_electronics_tag)} products with 'electronics' tag:")
    for product in products_with_electronics_tag:
        print(f" - {product.name} (ID: {product.id})")


if __name__ == "__main__":
    main()
