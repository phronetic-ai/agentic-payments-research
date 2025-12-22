"""
Placeholder Stripe Payment Gateway for Simulation
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


class StripePaymentGateway:
    """
    Placeholder Stripe payment gateway that simulates payment processing.
    """

    def __init__(self):
        self.payments: List[PaymentAttempt] = []
        self.idempotency_keys: Dict[str, str] = {}

    def create_payment_link(
        self,
        amount: float,
        currency: str,
        description: str,
        customer_email: str,
        expected_amount: Optional[float] = None, # Added for compatibility
        expected_description: Optional[str] = None, # Added for compatibility
        idempotency_key: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Simulates creating a payment link via Stripe.
        """
        payment_id = f"stripe_pay_{uuid.uuid4().hex[:12]}"
        
        # Placeholder for actual Stripe API call
        print(f"Stripe: Creating payment link for {amount} {currency}...")

        payment = PaymentAttempt(
            payment_id=payment_id,
            amount=amount,
            currency=currency,
            description=description,
            customer_email=customer_email,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        self.payments.append(payment)

        if idempotency_key:
            self.idempotency_keys[idempotency_key] = payment_id

        return {
            "payment_id": payment_id,
            "payment_link": f"https://stripe.com/pay/{payment_id}",
            "amount": amount,
            "currency": currency,
            "status": "created"
        }

    def create_upi_mandate(
        self,
        amount: float,
        frequency: str,
        customer_vpa: str,
        expected_amount: Optional[float] = None, # Added for compatibility
        expected_frequency: Optional[str] = None # Added for compatibility
    ) -> Dict:
        """
        Simulates creating a UPI mandate via Stripe. (If supported)
        """
        mandate_id = f"stripe_mandate_{uuid.uuid4().hex[:12]}"
        print(f"Stripe: Creating UPI mandate for {amount} {frequency}...")

        payment = PaymentAttempt(
            payment_id=mandate_id,
            amount=amount,
            currency="INR", # Assuming INR for UPI
            description=f"Stripe UPI Mandate - {frequency}",
            customer_email=customer_vpa,
            timestamp=datetime.now(),
            metadata={
                "type": "upi_mandate",
                "frequency": frequency
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
        """
        Placeholder for getting Stripe payment statistics.
        """
        return {"total_payments": len(self.payments), "provider": "Stripe"}

    def get_payment_details(self, payment_id: str) -> Optional[PaymentAttempt]:
        """
        Placeholder for getting details of a specific Stripe payment.
        """
        for payment in self.payments:
            if payment.payment_id == payment_id:
                return payment
        return None

    def reset(self):
        """Reset gateway state"""
        self.payments.clear()
        self.idempotency_keys.clear()
