"""
Product Catalog for Payment Determinism Simulation
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class Product:
    id: str
    name: str
    price: float
    currency: str = "INR"
    tax_rate: float = 0.18
    category: str = "Electronics"
    description: str = ""

    @property
    def price_with_tax(self) -> float:
        return self.price * (1 + self.tax_rate)


# Product catalog
PRODUCTS: Dict[str, Product] = {
    "LAPTOP001": Product(
        id="LAPTOP001",
        name="Dell XPS 15 Laptop",
        price=89999.00,
        description="15.6\" FHD, 16GB RAM, 512GB SSD"
    ),
    "LAPTOP002": Product(
        id="LAPTOP002",
        name="MacBook Pro 14",
        price=199000.00,
        description="M3 Pro, 18GB RAM, 512GB SSD"
    ),
    "PHONE001": Product(
        id="PHONE001",
        name="iPhone 15 Pro",
        price=129900.00,
        description="256GB, Natural Titanium"
    ),
    "MOUSE001": Product(
        id="MOUSE001",
        name="Logitech MX Master 3S",
        price=8995.00,
        description="Wireless mouse with USB-C"
    ),
    "KEYBOARD001": Product(
        id="KEYBOARD001",
        name="Keychron K8 Pro",
        price=9999.00,
        description="Wireless mechanical keyboard"
    ),
    "MONITOR001": Product(
        id="MONITOR001",
        name="LG 27\" 4K Monitor",
        price=29999.00,
        description="27\" IPS, 4K, USB-C"
    ),
    "HEADPHONE001": Product(
        id="HEADPHONE001",
        name="Sony WH-1000XM5",
        price=29990.00,
        description="Wireless noise-cancelling headphones"
    ),
    "TABLET001": Product(
        id="TABLET001",
        name="iPad Pro 11\"",
        price=71900.00,
        description="M2, 128GB, WiFi"
    ),
    "WATCH001": Product(
        id="WATCH001",
        name="Apple Watch Series 9",
        price=45900.00,
        description="GPS, 41mm, Midnight Aluminium"
    ),
    "SPEAKER001": Product(
        id="SPEAKER001",
        name="Sonos One",
        price=19999.00,
        description="Smart speaker with Alexa"
    ),
}


def get_product(product_id: str) -> Product:
    """Get product by ID"""
    return PRODUCTS.get(product_id)


def search_products(query: str, max_results: int = 5) -> List[Product]:
    """Search products by name or category"""
    query = query.lower()
    results = []
    for product in PRODUCTS.values():
        if query in product.name.lower() or query in product.category.lower():
            results.append(product)
            if len(results) >= max_results:
                break
    return results


def get_products_by_price_range(min_price: float, max_price: float) -> List[Product]:
    """Get products within price range"""
    return [p for p in PRODUCTS.values() if min_price <= p.price <= max_price]


# For testing - products with specific prices for edge cases
EDGE_CASE_PRODUCTS = {
    "DECIMAL_TEST": Product(
        id="DECIMAL_TEST",
        name="Decimal Test Product",
        price=29999.99,  # Will cause floating point issues
        description="Product to test floating point arithmetic"
    ),
    "HIGH_VALUE": Product(
        id="HIGH_VALUE",
        name="High Value Product",
        price=500000.00,  # High value for testing large amounts
        description="Expensive product for testing"
    ),
    "LOW_VALUE": Product(
        id="LOW_VALUE",
        name="Low Value Product",
        price=99.00,  # Low value for currency confusion
        description="Cheap product for testing"
    ),
}

# Add edge case products to main catalog
PRODUCTS.update(EDGE_CASE_PRODUCTS)
