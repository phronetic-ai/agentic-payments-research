"""
Product Catalog for PayCentral Mandate Simulation
Same products as naive simulation for fair comparison
"""

from dataclasses import dataclass
from typing import List


@dataclass
class Product:
    """Product with deterministic pricing"""
    id: str
    name: str
    price: float
    currency: str = "INR"
    tax_rate: float = 0.18
    category: str = "Electronics"
    description: str = ""

    @property
    def price_with_tax(self) -> float:
        """Calculate price including tax"""
        return round(self.price * (1 + self.tax_rate), 2)


# Product Catalog - Same as naive simulation
PRODUCT_CATALOG = [
    Product(
        id="prod_laptop_hp_001",
        name="HP Pavilion Gaming Laptop",
        price=89999.00,
        description="AMD Ryzen 5, 16GB RAM, 512GB SSD, GTX 1650"
    ),
    Product(
        id="prod_laptop_dell_002",
        name="Dell Inspiron 15",
        price=65999.00,
        description="Intel Core i5, 8GB RAM, 1TB HDD"
    ),
    Product(
        id="prod_laptop_mac_003",
        name="MacBook Air M2",
        price=119900.00,
        description="Apple M2 chip, 8GB RAM, 256GB SSD"
    ),
    Product(
        id="prod_phone_iphone_004",
        name="iPhone 15 Pro",
        price=129900.00,
        description="128GB, Titanium Blue"
    ),
    Product(
        id="prod_phone_samsung_005",
        name="Samsung Galaxy S24",
        price=79999.00,
        description="256GB, Phantom Black"
    ),
    Product(
        id="prod_mouse_001",
        name="Logitech MX Master 3",
        price=8995.00,
        category="Accessories",
        description="Wireless ergonomic mouse"
    ),
    Product(
        id="prod_keyboard_001",
        name="Keychron K2 Mechanical Keyboard",
        price=7999.00,
        category="Accessories",
        description="Wireless mechanical, hot-swappable"
    ),
    Product(
        id="prod_monitor_001",
        name="LG UltraWide 34-inch Monitor",
        price=45999.00,
        category="Displays",
        description="3440x1440, 144Hz, IPS"
    ),
    Product(
        id="prod_headphones_001",
        name="Sony WH-1000XM5",
        price=29990.00,
        category="Audio",
        description="Noise-cancelling wireless headphones"
    ),
    Product(
        id="prod_tablet_001",
        name="iPad Pro 12.9-inch",
        price=112900.00,
        category="Tablets",
        description="M2 chip, 256GB, WiFi"
    ),
    # Special products for edge case testing
    Product(
        id="prod_test_decimal",
        name="DECIMAL_TEST Product",
        price=29999.99,
        description="For testing decimal precision"
    ),
    Product(
        id="prod_test_high",
        name="HIGH_VALUE Product",
        price=199999.00,
        description="For testing high value transactions"
    ),
    Product(
        id="prod_test_low",
        name="LOW_VALUE Product",
        price=99.00,
        description="For testing low value transactions"
    ),
]


def get_product_by_id(product_id: str) -> Product:
    """Get product by ID"""
    for product in PRODUCT_CATALOG:
        if product.id == product_id:
            return product
    raise ValueError(f"Product not found: {product_id}")


def get_products_by_category(category: str) -> List[Product]:
    """Get all products in a category"""
    return [p for p in PRODUCT_CATALOG if p.category == category]


def get_all_products() -> List[Product]:
    """Get all products"""
    return PRODUCT_CATALOG.copy()
