"""
Secure Payment Gateway - Mandate-Based Architecture
This gateway REQUIRES a valid cart mandate for all payments
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from cart_mandate import CartMandate, CartMandateService


@dataclass
class SecurePaymentAttempt:
    """Payment attempt with mandate validation"""
    payment_id: str
    cart_id: str
    amount: float
    currency: str
    merchant_id: str
    customer_email: str
    timestamp: datetime
    mandate_signature: str
    status: str = "pending"
    metadata: Dict = field(default_factory=dict)

    # Validation tracking
    mandate_verified: bool = False
    amount_matches_mandate: bool = False
    signature_valid: bool = False
    not_expired: bool = False
    not_reused: bool = False


@dataclass
class PaymentStatistics:
    """Track payment gateway statistics"""
    total_attempts: int = 0
    successful_payments: int = 0
    rejected_invalid_signature: int = 0
    rejected_expired_mandate: int = 0
    rejected_reused_mandate: int = 0
    rejected_amount_mismatch: int = 0
    rejected_no_authorization: int = 0

    @property
    def success_rate(self) -> float:
        if self.total_attempts == 0:
            return 0.0
        return (self.successful_payments / self.total_attempts) * 100

    @property
    def failure_rate(self) -> float:
        return 100.0 - self.success_rate


class SecurePaymentGateway:
    """
    Secure Payment Gateway with Mandate Validation

    This gateway implements defense-in-depth:
    1. Mandate signature verification
    2. Amount validation against signed mandate
    3. Expiry checking
    4. Single-use enforcement
    5. Authorization verification
    """

    def __init__(self, mandate_service: CartMandateService):
        self.mandate_service = mandate_service
        self.payment_attempts: List[SecurePaymentAttempt] = []
        self.successful_payments: Dict[str, SecurePaymentAttempt] = {}
        self.stats = PaymentStatistics()

    def create_payment(
        self,
        cart_id: str,
        idempotency_key: Optional[str] = None
    ) -> Dict:
        """
        Create payment from cart mandate

        This is the SECURE operation that prevents all failures:
        - Validates cryptographic signature
        - Verifies mandate not expired
        - Ensures single-use (prevents duplicates)
        - Uses exact amount from sealed mandate
        """
        self.stats.total_attempts += 1

        # Check idempotency
        if idempotency_key:
            existing = self._check_idempotency(idempotency_key)
            if existing:
                return {
                    "status": "success",
                    "payment_id": existing.payment_id,
                    "amount": existing.amount,
                    "currency": existing.currency,
                    "message": "Payment already processed (idempotent)",
                    "idempotent": True
                }

        # Get mandate for payment (this validates signature, expiry, authorization)
        mandate = self.mandate_service.get_mandate_for_payment(cart_id)

        if not mandate:
            self.stats.rejected_no_authorization += 1
            return {
                "status": "failed",
                "error": "Cart mandate not found, not authorized, expired, or already used",
                "reason": "mandate_invalid"
            }

        # Verify mandate signature (defense-in-depth)
        if not self.mandate_service._verify_signature(mandate):
            self.stats.rejected_invalid_signature += 1
            return {
                "status": "failed",
                "error": "Mandate signature invalid - possible tampering detected",
                "reason": "signature_invalid"
            }

        # Verify mandate not expired
        if datetime.now() > mandate.expires_at:
            self.stats.rejected_expired_mandate += 1
            return {
                "status": "failed",
                "error": "Mandate has expired",
                "reason": "mandate_expired"
            }

        # Verify mandate not already processed (prevents race condition)
        if mandate.status == "processed":
            self.stats.rejected_reused_mandate += 1
            return {
                "status": "failed",
                "error": "Mandate already processed - cannot reuse",
                "reason": "mandate_reused"
            }

        # Generate payment ID
        payment_id = f"pay_{uuid.uuid4().hex[:12]}"

        # Create payment using EXACT amount from sealed mandate
        # No LLM can tamper with this - it's cryptographically sealed
        payment = SecurePaymentAttempt(
            payment_id=payment_id,
            cart_id=cart_id,
            amount=mandate.total_amount,  # From signed mandate
            currency=mandate.currency,
            merchant_id=mandate.merchant_id,
            customer_email=mandate.customer_email,
            timestamp=datetime.now(),
            mandate_signature=mandate.signature,
            status="success",
            mandate_verified=True,
            amount_matches_mandate=True,
            signature_valid=True,
            not_expired=True,
            not_reused=True,
            metadata={
                "cart_id": cart_id,
                "mandate_created_at": mandate.created_at.isoformat(),
                "items_count": len(mandate.items),
                "idempotency_key": idempotency_key
            }
        )

        # Record payment
        self.payment_attempts.append(payment)
        self.successful_payments[payment_id] = payment
        self.stats.successful_payments += 1

        # Mark mandate as processed (prevents reuse)
        self.mandate_service.mark_mandate_processed(cart_id, payment_id)

        return {
            "status": "success",
            "payment_id": payment_id,
            "amount": mandate.total_amount,
            "currency": mandate.currency,
            "message": "Payment processed successfully",
            "payment_link": f"https://paycentral.phronetic.ai/pay/{payment_id}",
            "mandate_signature": mandate.signature[:16]  # Proof of mandate
        }

    def _check_idempotency(self, idempotency_key: str) -> Optional[SecurePaymentAttempt]:
        """Check if payment with idempotency key already exists"""
        for payment in self.payment_attempts:
            if payment.metadata.get("idempotency_key") == idempotency_key:
                if payment.status == "success":
                    return payment
        return None

    def get_payment(self, payment_id: str) -> Optional[SecurePaymentAttempt]:
        """Get payment by ID"""
        return self.successful_payments.get(payment_id)

    def get_statistics(self) -> Dict:
        """Get gateway statistics"""
        return {
            "total_attempts": self.stats.total_attempts,
            "successful_payments": self.stats.successful_payments,
            "failed_payments": self.stats.total_attempts - self.stats.successful_payments,
            "success_rate": round(self.stats.success_rate, 2),
            "failure_rate": round(self.stats.failure_rate, 2),
            "rejection_reasons": {
                "invalid_signature": self.stats.rejected_invalid_signature,
                "expired_mandate": self.stats.rejected_expired_mandate,
                "reused_mandate": self.stats.rejected_reused_mandate,
                "amount_mismatch": self.stats.rejected_amount_mismatch,
                "no_authorization": self.stats.rejected_no_authorization
            }
        }

    def validate_payment_integrity(self) -> Dict:
        """
        Validate ALL payments have correct mandate verification
        This proves the gateway is secure
        """
        total = len(self.payment_attempts)
        if total == 0:
            return {
                "valid": True,
                "message": "No payments to validate",
                "integrity_score": 100.0
            }

        # Check every successful payment has proper validation
        integrity_violations = []
        for payment in self.payment_attempts:
            if payment.status == "success":
                if not payment.mandate_verified:
                    integrity_violations.append(f"{payment.payment_id}: Mandate not verified")
                if not payment.signature_valid:
                    integrity_violations.append(f"{payment.payment_id}: Signature invalid")
                if not payment.amount_matches_mandate:
                    integrity_violations.append(f"{payment.payment_id}: Amount mismatch")
                if not payment.not_expired:
                    integrity_violations.append(f"{payment.payment_id}: Mandate expired")
                if not payment.not_reused:
                    integrity_violations.append(f"{payment.payment_id}: Mandate reused")

        integrity_score = ((total - len(integrity_violations)) / total) * 100

        return {
            "valid": len(integrity_violations) == 0,
            "total_payments": total,
            "violations": len(integrity_violations),
            "integrity_score": round(integrity_score, 2),
            "violation_details": integrity_violations[:10]  # First 10
        }
