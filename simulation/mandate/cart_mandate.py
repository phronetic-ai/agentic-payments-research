"""
Cart Mandate Service - Deterministic Layer
This is the CORRECT architecture that eliminates LLM non-determinism
"""

import hashlib
import hmac
import json
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import uuid


@dataclass
class CartItem:
    """Cart item with deterministic pricing"""
    id: str
    name: str
    description: str
    quantity: int
    unit_price: float
    total_price: float
    tax_rate: float
    tax_amount: float
    currency: str = "INR"

    def validate(self) -> bool:
        """Validate item calculations"""
        # Check total = quantity × unit_price
        expected_total = self.quantity * self.unit_price
        if abs(self.total_price - expected_total) > 0.01:
            return False

        # Check tax = total × tax_rate
        expected_tax = self.total_price * self.tax_rate
        if abs(self.tax_amount - expected_tax) > 0.01:
            return False

        return True


@dataclass
class CartMandate:
    """
    Cryptographically signed cart mandate
    This is immutable and tamper-proof
    """
    cart_id: str
    merchant_id: str
    customer_email: str
    items: List[CartItem]
    subtotal: float
    tax_total: float
    total_amount: float
    currency: str
    created_at: datetime
    expires_at: datetime
    signature: str = ""

    # Tracking
    status: str = "awaiting_authorization"  # awaiting_authorization, authorized, processed, expired
    processed_at: Optional[datetime] = None
    payment_id: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for signing"""
        return {
            "cart_id": self.cart_id,
            "merchant_id": self.merchant_id,
            "customer_email": self.customer_email,
            "items": [
                {
                    "id": item.id,
                    "name": item.name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "total_price": item.total_price,
                    "tax_rate": item.tax_rate,
                    "tax_amount": item.tax_amount,
                }
                for item in self.items
            ],
            "subtotal": self.subtotal,
            "tax_total": self.tax_total,
            "total_amount": self.total_amount,
            "currency": self.currency,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat(),
        }

    def validate(self) -> bool:
        """Validate cart mandate integrity"""
        # Validate each item
        for item in self.items:
            if not item.validate():
                return False

        # Validate subtotal = sum of item totals
        expected_subtotal = sum(item.total_price for item in self.items)
        if abs(self.subtotal - expected_subtotal) > 0.01:
            return False

        # Validate tax_total = sum of item taxes
        expected_tax = sum(item.tax_amount for item in self.items)
        if abs(self.tax_total - expected_tax) > 0.01:
            return False

        # Validate total = subtotal + tax
        expected_total = self.subtotal + self.tax_total
        if abs(self.total_amount - expected_total) > 0.01:
            return False

        return True


class CartMandateService:
    """
    Cart Mandate Service - The Deterministic Layer

    This service provides cryptographic guarantees that:
    1. Cart amounts cannot be tampered with
    2. Prices are locked at mandate creation
    3. Mandates expire after 30 minutes
    4. Each mandate can only be used once
    5. Signature verification prevents manipulation
    """

    def __init__(self, secret_key: str = "phronetic_secret_key_2025"):
        self.secret_key = secret_key
        self.mandates: Dict[str, CartMandate] = {}
        self.idempotency_keys: Dict[str, str] = {}  # Track payment idempotency

    def _generate_signature(self, mandate: CartMandate) -> str:
        """
        Generate HMAC-SHA256 signature for cart mandate
        This cryptographically seals the cart contents
        """
        # Serialize cart data
        data = json.dumps(mandate.to_dict(), sort_keys=True)

        # Create HMAC signature
        signature = hmac.new(
            self.secret_key.encode(),
            data.encode(),
            hashlib.sha256
        ).hexdigest()

        return signature

    def _verify_signature(self, mandate: CartMandate) -> bool:
        """Verify cart mandate signature"""
        stored_signature = mandate.signature
        mandate.signature = ""  # Temporarily remove for verification

        expected_signature = self._generate_signature(mandate)

        mandate.signature = stored_signature  # Restore signature

        return hmac.compare_digest(stored_signature, expected_signature)

    def create_cart_mandate(
        self,
        merchant_id: str,
        customer_email: str,
        items: List[Dict],
        currency: str = "INR",
        idempotency_key: Optional[str] = None
    ) -> Dict:
        """
        Create a cryptographically signed cart mandate

        This is the DETERMINISTIC operation that locks cart contents
        LLM cannot tamper with this after creation
        """

        # Check idempotency
        if idempotency_key and idempotency_key in self.idempotency_keys:
            existing_cart_id = self.idempotency_keys[idempotency_key]
            existing_mandate = self.mandates[existing_cart_id]
            return {
                "status": "existing",
                "cart_id": existing_mandate.cart_id,
                "validation_token": existing_mandate.signature[:32],
                "cart_details": {
                    "items": len(existing_mandate.items),
                    "total_amount": existing_mandate.total_amount,
                    "currency": existing_mandate.currency,
                    "expires_at": existing_mandate.expires_at.isoformat()
                }
            }

        # Generate cart ID
        cart_id = f"cart_{uuid.uuid4().hex[:12]}"

        # Create cart items with DETERMINISTIC calculations
        cart_items = []
        subtotal = 0.0
        tax_total = 0.0

        for item_data in items:
            # Calculate with precision (no hallucination possible)
            quantity = item_data["quantity"]
            unit_price = float(item_data["unit_price"])
            tax_rate = float(item_data.get("tax_rate", 0.18))

            # DETERMINISTIC calculations
            total_price = round(quantity * unit_price, 2)
            tax_amount = round(total_price * tax_rate, 2)

            item = CartItem(
                id=item_data["id"],
                name=item_data["name"],
                description=item_data.get("description", ""),
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price,
                tax_rate=tax_rate,
                tax_amount=tax_amount,
                currency=currency
            )

            cart_items.append(item)
            subtotal += total_price
            tax_total += tax_amount

        # Round totals
        subtotal = round(subtotal, 2)
        tax_total = round(tax_total, 2)
        total_amount = round(subtotal + tax_total, 2)

        # Create mandate
        now = datetime.now()
        mandate = CartMandate(
            cart_id=cart_id,
            merchant_id=merchant_id,
            customer_email=customer_email,
            items=cart_items,
            subtotal=subtotal,
            tax_total=tax_total,
            total_amount=total_amount,
            currency=currency,
            created_at=now,
            expires_at=now + timedelta(minutes=30)  # 30 minute expiry
        )

        # Validate mandate calculations
        if not mandate.validate():
            raise ValueError("Cart mandate validation failed - calculation error")

        # Generate signature
        mandate.signature = self._generate_signature(mandate)

        # Store mandate
        self.mandates[cart_id] = mandate

        # Store idempotency key
        if idempotency_key:
            self.idempotency_keys[idempotency_key] = cart_id

        return {
            "status": "awaiting_authorization",
            "cart_id": cart_id,
            "validation_token": mandate.signature[:32],  # First 32 chars as token
            "cart_details": {
                "items": len(cart_items),
                "subtotal": subtotal,
                "tax_total": tax_total,
                "total_amount": total_amount,
                "currency": currency,
                "expires_at": mandate.expires_at.isoformat()
            },
            "mandate": mandate  # For internal use
        }

    def validate_cart_mandate(
        self,
        cart_id: str,
        validation_token: str
    ) -> Dict:
        """
        Validate cart mandate before authorization
        """
        # Get mandate
        mandate = self.mandates.get(cart_id)
        if not mandate:
            return {
                "valid": False,
                "error": "Cart mandate not found"
            }

        # Verify signature
        if not self._verify_signature(mandate):
            return {
                "valid": False,
                "error": "Invalid signature - cart may have been tampered with"
            }

        # Check validation token
        if mandate.signature[:32] != validation_token:
            return {
                "valid": False,
                "error": "Invalid validation token"
            }

        # Check expiry
        if datetime.now() > mandate.expires_at:
            mandate.status = "expired"
            return {
                "valid": False,
                "error": "Cart mandate has expired"
            }

        # Check if already processed
        if mandate.status == "processed":
            return {
                "valid": False,
                "error": "Cart mandate already processed"
            }

        # Validate calculations
        if not mandate.validate():
            return {
                "valid": False,
                "error": "Cart mandate validation failed"
            }

        return {
            "valid": True,
            "cart_id": cart_id,
            "total_amount": mandate.total_amount,
            "currency": mandate.currency
        }

    def authorize_cart_mandate(
        self,
        cart_id: str,
        authorization_proof: str,
        customer_confirmation: bool
    ) -> Dict:
        """
        Authorize cart mandate for payment
        Requires explicit customer confirmation
        """
        # Get mandate
        mandate = self.mandates.get(cart_id)
        if not mandate:
            return {
                "authorized": False,
                "error": "Cart mandate not found"
            }

        # Require explicit confirmation
        if not customer_confirmation:
            return {
                "authorized": False,
                "error": "Customer confirmation required"
            }

        # Verify signature
        if not self._verify_signature(mandate):
            return {
                "authorized": False,
                "error": "Invalid signature"
            }

        # Check expiry
        if datetime.now() > mandate.expires_at:
            mandate.status = "expired"
            return {
                "authorized": False,
                "error": "Cart mandate expired"
            }

        # Check already processed
        if mandate.status == "processed":
            return {
                "authorized": False,
                "error": "Already processed"
            }

        # Authorize
        mandate.status = "authorized"

        return {
            "authorized": True,
            "cart_id": cart_id,
            "total_amount": mandate.total_amount,
            "currency": mandate.currency
        }

    def get_mandate_for_payment(self, cart_id: str) -> Optional[CartMandate]:
        """
        Get cart mandate for payment processing
        Payment gateway will use the EXACT amount from this sealed mandate
        """
        mandate = self.mandates.get(cart_id)

        if not mandate:
            return None

        # Verify mandate is authorized
        if mandate.status != "authorized":
            return None

        # Verify signature
        if not self._verify_signature(mandate):
            return None

        # Verify not expired
        if datetime.now() > mandate.expires_at:
            return None

        return mandate

    def mark_mandate_processed(
        self,
        cart_id: str,
        payment_id: str
    ):
        """Mark mandate as processed (prevents reuse)"""
        mandate = self.mandates.get(cart_id)
        if mandate:
            mandate.status = "processed"
            mandate.processed_at = datetime.now()
            mandate.payment_id = payment_id

    def get_statistics(self) -> Dict:
        """Get mandate statistics"""
        total = len(self.mandates)
        if total == 0:
            return {
                "total": 0,
                "awaiting_authorization": 0,
                "authorized": 0,
                "processed": 0,
                "expired": 0
            }

        stats = {
            "total": total,
            "awaiting_authorization": 0,
            "authorized": 0,
            "processed": 0,
            "expired": 0
        }

        for mandate in self.mandates.values():
            stats[mandate.status] = stats.get(mandate.status, 0) + 1

        return stats
