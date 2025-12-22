"""
Payment Gateway for Simulation
Tracks all payment attempts and their details
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import uuid


@dataclass
class PaymentAttempt:
    """Record of a payment attempt"""
    payment_id: str
    amount: float
    currency: str
    description: str
    customer_email: str
    timestamp: datetime
    status: str = "pending"  # pending, success, failed
    metadata: Dict = field(default_factory=dict)

    # Expected values (for validation)
    expected_amount: Optional[float] = None
    expected_description: Optional[str] = None

    @property
    def is_correct(self) -> bool:
        """Check if payment matches expected values"""
        if self.expected_amount is not None:
            if abs(self.amount - self.expected_amount) > 0.01:  # Allow 1 paisa tolerance
                return False
        if self.expected_description is not None:
            if self.description != self.expected_description:
                return False
        return True

    @property
    def error_type(self) -> Optional[str]:
        """Determine type of error"""
        if self.is_correct:
            return None

        if self.expected_amount is not None and abs(self.amount - self.expected_amount) > 0.01:
            diff = abs(self.amount - self.expected_amount)
            if diff > 1000:
                return "major_price_error"
            elif self.amount == 0:
                return "zero_charge"
            elif self.amount < self.expected_amount:
                return "undercharge"
            else:
                return "overcharge"

        if self.expected_description != self.description:
            return "description_mismatch"

        return "unknown_error"


class MockPaymentGateway:
    """
    Mock payment gateway that simulates payment processing
    Tracks all attempts for analysis
    """

    def __init__(self):
        self.payments: List[PaymentAttempt] = []
        self.idempotency_keys: Dict[str, str] = {}  # Track idempotency

    def create_payment_link(
        self,
        amount: float,
        currency: str,
        description: str,
        customer_email: str,
        expected_amount: Optional[float] = None,
        expected_description: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Create a payment link

        Args:
            amount: Amount to charge
            currency: Currency code
            description: Payment description
            customer_email: Customer email
            expected_amount: What amount SHOULD be charged (for validation)
            expected_description: What description SHOULD be (for validation)
            idempotency_key: Optional idempotency key
            metadata: Optional metadata

        Returns:
            Payment link details
        """

        # Check idempotency
        if idempotency_key:
            if idempotency_key in self.idempotency_keys:
                # Return existing payment
                existing_payment_id = self.idempotency_keys[idempotency_key]
                existing_payment = next(
                    p for p in self.payments if p.payment_id == existing_payment_id
                )
                return {
                    "payment_id": existing_payment.payment_id,
                    "payment_link": f"https://payment.gateway.com/pay/{existing_payment.payment_id}",
                    "amount": existing_payment.amount,
                    "currency": existing_payment.currency,
                    "status": "duplicate_prevented"
                }

        # Create new payment
        payment_id = f"pay_{uuid.uuid4().hex[:12]}"

        payment = PaymentAttempt(
            payment_id=payment_id,
            amount=amount,
            currency=currency,
            description=description,
            customer_email=customer_email,
            timestamp=datetime.now(),
            expected_amount=expected_amount,
            expected_description=expected_description,
            metadata=metadata or {}
        )

        self.payments.append(payment)

        if idempotency_key:
            self.idempotency_keys[idempotency_key] = payment_id

        return {
            "payment_id": payment_id,
            "payment_link": f"https://payment.gateway.com/pay/{payment_id}",
            "amount": amount,
            "currency": currency,
            "status": "created"
        }

    def create_upi_mandate(
        self,
        amount: float,
        frequency: str,
        customer_vpa: str,
        expected_amount: Optional[float] = None,
        expected_frequency: Optional[str] = None
    ) -> Dict:
        """Create UPI mandate"""
        mandate_id = f"mandate_{uuid.uuid4().hex[:12]}"

        # Track as special payment type
        payment = PaymentAttempt(
            payment_id=mandate_id,
            amount=amount,
            currency="INR",
            description=f"UPI Mandate - {frequency}",
            customer_email=customer_vpa,
            timestamp=datetime.now(),
            expected_amount=expected_amount,
            metadata={
                "type": "upi_mandate",
                "frequency": frequency,
                "expected_frequency": expected_frequency
            }
        )

        self.payments.append(payment)

        return {
            "mandate_id": mandate_id,
            "amount": amount,
            "frequency": frequency,
            "status": "created"
        }

    def get_statistics(self) -> Dict:
        """Get payment statistics"""
        total = len(self.payments)
        if total == 0:
            return {
                "total": 0,
                "correct": 0,
                "incorrect": 0,
                "success_rate": 0.0,
                "error_breakdown": {}
            }

        correct = sum(1 for p in self.payments if p.is_correct)
        incorrect = total - correct

        # Count error types
        error_breakdown = {}
        for payment in self.payments:
            if not payment.is_correct:
                error_type = payment.error_type
                error_breakdown[error_type] = error_breakdown.get(error_type, 0) + 1

        return {
            "total": total,
            "correct": correct,
            "incorrect": incorrect,
            "success_rate": (correct / total) * 100,
            "failure_rate": (incorrect / total) * 100,
            "error_breakdown": error_breakdown
        }

    def get_payment_details(self, payment_id: str) -> Optional[PaymentAttempt]:
        """Get details of a specific payment"""
        for payment in self.payments:
            if payment.payment_id == payment_id:
                return payment
        return None

    def reset(self):
        """Reset gateway state"""
        self.payments.clear()
        self.idempotency_keys.clear()
