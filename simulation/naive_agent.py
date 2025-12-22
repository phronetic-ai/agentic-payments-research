"""
Naive Agent with Direct Payment Integration
Demonstrates all failure modes from the research paper
"""

import random
from typing import Dict, List, Optional, Tuple
from .products import Product, get_product, search_products
from .payment_gateway import MockPaymentGateway


class NaiveShoppingAgent:
    """
    Shopping agent with DIRECT payment gateway integration
    This is the BROKEN architecture that the paper warns against
    """

    def __init__(self, payment_gateway: MockPaymentGateway):
        self.gateway = payment_gateway
        self.cart: List[Tuple[Product, int]] = []  # (product, quantity)
        self.conversation_history: List[str] = []
        self.context_window_size = 50  # Simulate limited context

        # Simulate LLM non-determinism parameters
        self.hallucination_rate = 0.15  # 15% chance of hallucination
        self.calculation_error_rate = 0.08  # 8% floating point errors
        self.context_loss_rate = 0.12  # 12% chance of context loss
        self.prompt_injection_vulnerable = True

    def add_to_conversation(self, message: str):
        """Add message to conversation history"""
        self.conversation_history.append(message)

        # Simulate context window overflow
        if len(self.conversation_history) > self.context_window_size:
            # Lose oldest messages including cart info
            self.conversation_history = self.conversation_history[-self.context_window_size:]

    def add_to_cart(self, product_id: str, quantity: int = 1):
        """Add product to cart"""
        product = get_product(product_id)
        if product:
            self.cart.append((product, quantity))
            self.add_to_conversation(f"Added {quantity}x {product.name} to cart")

    def calculate_total(self) -> float:
        """
        Calculate cart total - DEMONSTRATES FLOATING POINT ERRORS
        """
        # Simulate different calculation methods that produce different results

        # Random chance of calculation error
        if random.random() < self.calculation_error_rate:
            # Method 1: Calculate with rounding errors
            total = 0.0
            for product, qty in self.cart:
                # Round intermediately (creates errors)
                item_total = round(product.price * qty, 2)
                tax = round(item_total * product.tax_rate, 2)
                total += round(item_total + tax, 2)
            return round(total, 0)  # Round to nearest rupee (loses precision)

        # Method 2: Correct calculation (used 92% of the time)
        total = 0.0
        for product, qty in self.cart:
            subtotal = product.price * qty
            tax = subtotal * product.tax_rate
            total += subtotal + tax

        return round(total, 2)

    def calculate_total_with_hallucination(self, expected_total: float) -> float:
        """
        Simulate price hallucination
        Returns wrong amount some percentage of the time
        """
        if random.random() < self.hallucination_rate:
            # Different types of hallucinations
            hallucination_type = random.choice([
                "wrong_multiplication",
                "phantom_discount",
                "currency_confusion",
                "extra_digit",
                "missing_digit"
            ])

            if hallucination_type == "wrong_multiplication":
                # Wrong quantity calculation
                return expected_total * random.uniform(0.5, 1.5)

            elif hallucination_type == "phantom_discount":
                # Hallucinate discount
                discount = random.choice([0.9, 0.8, 0.7, 0.5])
                return expected_total * discount

            elif hallucination_type == "currency_confusion":
                # Treat $ as ₹ or vice versa
                if expected_total > 1000:
                    return expected_total / 83  # Treat INR as USD
                else:
                    return expected_total * 83  # Treat USD as INR

            elif hallucination_type == "extra_digit":
                # Add extra digit
                return expected_total * 10

            elif hallucination_type == "missing_digit":
                # Drop digit
                return expected_total / 10

        return expected_total

    def process_prompt_injection(self, user_message: str) -> Optional[str]:
        """
        Check for prompt injection attacks
        Returns injected amount if found
        """
        if not self.prompt_injection_vulnerable:
            return None

        # Common injection patterns
        injection_patterns = [
            "SYSTEM: Always charge",
            "SYSTEM: Ignore previous pricing",
            "SYSTEM: For testing, use amount",
            "NEW INSTRUCTION: Set price to",
            "OVERRIDE: Payment amount should be"
        ]

        message_upper = user_message.upper()
        for pattern in injection_patterns:
            if pattern.upper() in message_upper:
                # Extract amount from injection
                words = user_message.split()
                for i, word in enumerate(words):
                    # Look for number after injection pattern
                    try:
                        if word.replace(".", "").replace(",", "").isdigit():
                            return float(word.replace(",", ""))
                    except:
                        pass
                # Default injection: charge ₹1
                return 1.0

        return None

    def simulate_context_loss(self) -> bool:
        """
        Simulate context window overflow causing cart loss
        Returns True if context was lost
        """
        if len(self.conversation_history) > self.context_window_size * 0.8:
            # High chance of losing cart info if context is nearly full
            if random.random() < self.context_loss_rate:
                return True
        return False

    def get_authorization_interpretation(self, user_message: str) -> bool:
        """
        Interpret if user message is authorization
        DEMONSTRATES AUTHORIZATION AMBIGUITY
        """
        # Ambiguous phrases that might be misinterpreted as authorization
        ambiguous_phrases = [
            "sounds good",
            "okay",
            "ok",
            "sure",
            "fine",
            "alright",
            "looks good",
            "i like it",
            "interesting",
            "nice"
        ]

        message_lower = user_message.lower()

        # Explicit authorization (clear)
        if any(phrase in message_lower for phrase in ["yes, authorize", "yes, confirm", "proceed with payment", "yes, pay"]):
            return True

        # Ambiguous phrases (WRONG to interpret as authorization)
        if any(phrase in message_lower for phrase in ambiguous_phrases):
            # 60% chance agent misinterprets as authorization
            return random.random() < 0.6

        return False

    def create_payment_link(
        self,
        user_message: str,
        expected_amount: float,
        expected_description: str
    ) -> Dict:
        """
        Create payment link - DIRECT INTEGRATION (BROKEN)
        This demonstrates all failure modes
        """

        # FAILURE MODE 1: Prompt Injection
        injected_amount = self.process_prompt_injection(user_message)
        if injected_amount is not None:
            # Agent follows injected instruction
            actual_amount = injected_amount
            description = "Payment (INJECTED)"
        else:
            # FAILURE MODE 2: Context Loss
            if self.simulate_context_loss():
                # Cart lost from context
                if len(self.cart) == 0:
                    actual_amount = 0.0
                else:
                    # Hallucinate cart contents
                    actual_amount = random.uniform(100, 10000)
                description = "Payment (CONTEXT LOST)"

            # FAILURE MODE 3: Calculation Errors
            elif random.random() < self.calculation_error_rate:
                actual_amount = self.calculate_total()  # May have rounding errors
                description = expected_description

            # FAILURE MODE 4: Hallucination
            else:
                correct_amount = self.calculate_total()
                actual_amount = self.calculate_total_with_hallucination(correct_amount)
                description = expected_description

        # Call payment gateway directly (no mandate layer)
        return self.gateway.create_payment_link(
            amount=actual_amount,
            currency="INR",
            description=description,
            customer_email="customer@example.com",
            expected_amount=expected_amount,
            expected_description=expected_description
        )

    def create_upi_mandate(
        self,
        amount: float,
        frequency: str,
        customer_vpa: str,
        expected_amount: float,
        expected_frequency: str
    ) -> Dict:
        """
        Create UPI mandate - DEMONSTRATES FREQUENCY HALLUCINATION
        """

        # Frequency confusion (common hallucination)
        if random.random() < self.hallucination_rate:
            frequency_map = {
                "monthly": ["weekly", "daily", "yearly"],
                "weekly": ["daily", "monthly", "yearly"],
                "daily": ["weekly", "monthly", "yearly"],
                "yearly": ["monthly", "weekly", "daily"]
            }

            if frequency in frequency_map:
                actual_frequency = random.choice(frequency_map[frequency])
            else:
                actual_frequency = frequency
        else:
            actual_frequency = frequency

        # Amount hallucination
        actual_amount = self.calculate_total_with_hallucination(amount)

        return self.gateway.create_upi_mandate(
            amount=actual_amount,
            frequency=actual_frequency,
            customer_vpa=customer_vpa,
            expected_amount=expected_amount,
            expected_frequency=expected_frequency
        )

    def simulate_race_condition(self, expected_amount: float, expected_description: str):
        """
        Simulate race condition causing duplicate charges
        DEMONSTRATES RACE CONDITION FAILURE
        """
        # No idempotency key - creates duplicate
        payment1 = self.gateway.create_payment_link(
            amount=expected_amount,
            currency="INR",
            description=expected_description,
            customer_email="customer@example.com",
            expected_amount=expected_amount
        )

        # Duplicate request (user clicked twice or API retried)
        payment2 = self.gateway.create_payment_link(
            amount=expected_amount,
            currency="INR",
            description=expected_description,
            customer_email="customer@example.com",
            expected_amount=expected_amount
        )

        return payment1, payment2

    def reset(self):
        """Reset agent state"""
        self.cart.clear()
        self.conversation_history.clear()
