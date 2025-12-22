# Agentic Payments Research

Research proving LLM agents fail at payments without architectural safeguards, and validating a 0% failure rate mandate-based solution.

## Project Overview

The emergence of Large Language Model (LLM)-powered conversational agents in e-commerce presents a fundamental challenge: the incompatibility between probabilistic AI systems and deterministic financial transaction requirements. This repository contains the code and whitepaper for a comprehensive empirical study analyzing 160,000 simulated transactions across two architectural paradigms:

1.  **Direct Integration:** LLM agents directly call payment gateway APIs.
2.  **Mandate Architecture (PayCentral):** A cryptographically-sealed intermediate authorization layer that isolates LLM conversation from financial calculations.

Our research conclusively demonstrates that direct integration is catastrophically unsafe, while the mandate-based architecture achieves perfect reliability.

## Key Findings

| Metric | Direct LLM-Payment Integration | PayCentral Mandate Architecture |
|---|---|---|
| **Failure Rate** | **36.98%** | **0.00%** |
| **Security Vulnerabilities** | 5 critical flaws (Prompt Injection: 51%, Race Conditions: 100%) | 0 vulnerabilities |
| **Regulatory Compliance** | Non-compliant (PCI DSS, PSD2, RBI) | Fully compliant |
| **Annual Financial Risk** (100K transactions) | **₹332.82 crores** ($40M USD) | **₹7.74 lakhs** ($93K USD) |
| **Statistical Confidence** | 99.9% (N=80,000 per architecture) | 99.9% (N=80,000 per architecture) |

## The Problem: Probabilistic AI vs. Deterministic Finance

LLMs are inherently probabilistic; the same input can yield different outputs. Financial transactions, however, demand exact, verifiable, and cryptographically guaranteed correctness. Direct integration exposes payment systems to various failure modes:

*   **Price Hallucination:** LLMs generating incorrect payment amounts.
*   **Prompt Injection:** Adversarial instructions manipulating transaction details.
*   **Context Window Overflow:** Loss of cart contents in long conversations.
*   **Floating-Point Errors:** Imprecise calculations leading to discrepancies.
*   **Authorization Ambiguity:** LLMs misinterpreting natural language as payment authorization.
*   **Race Conditions:** Duplicate charges from concurrent requests.
*   **UPI Mandate Frequency Errors:** Incorrect subscription billing cycles.
*   **Currency Confusion:** Mismanagement of currency types.

## The Solution: Mandate Architecture

The PayCentral mandate architecture solves this by introducing a **deterministic layer** between the LLM agent and the payment gateway. The LLM agent only identifies products and quantities. All financial calculations, cryptographic sealing (HMAC-SHA256), and verification occur in a separate, trusted service, ensuring payments are secure and deterministic regardless of LLM behavior.

## Repository Structure

```
agentic-payments-research/
├── whitepaper/                                      # Research whitepaper and appendices
│   └── Determinism_in_Agentic_Payments_Whitepaper.md
│
├── simulation/                                      # Monte Carlo simulation framework
│   ├── run_simulation.py                           # Main simulation runner for direct integration (various gateways)
│   ├── naive_agent.py                              # LLM agent for direct integration
│   ├── test_scenarios.py                           # Defines 8 failure modes tested
│   ├── products.py                                 # Product catalog for simulations
│   ├── payment_gateway.py                          # Mock payment gateway for simulation
│   ├── simulation_results.json                     # Simulation results for mock gateway
│   ├── FRAMEWORK_GUIDE.md                          # Complete guide for framework reusability
│   ├── mcp/                                        # Placeholder payment gateways (Stripe, Razorpay, Generic MCP)
│   │   ├── stripe_payment_gateway.py
│   │   ├── razorpay_payment_gateway.py
│   │   ├── generic_mcp_payment_gateway.py
│   │   └── simulation_results/                     # Simulation results for different gateways
│   │       ├── simulation_results_mock.json
│   │       ├── simulation_results_stripe.json
│   │       ├── simulation_results_razorpay.json
│   │       └── simulation_results_genericmcp.json
│   └── mandate/                                    # Secure mandate-based architecture simulation
│       ├── run_mandate_simulation.py               # Runner for mandate simulation
│       ├── mandate_agent.py                        # Secure LLM agent for mandate architecture
│       ├── cart_mandate.py                         # Defines cryptographically sealed cart mandates
│       ├── secure_payment_gateway.py               # Secure payment gateway for mandate architecture
│       ├── mandate_test_scenarios.py               # Test scenarios for mandate architecture
│       ├── products.py                             # Product catalog for mandate simulations
│       └── mandate_simulation_results.json         # Results of mandate simulation (0% failure)
│
└── validation/                                      # Real API testing to validate simulation accuracy
    ├── validate_with_real_apis.py                  # Script to run tests against real LLM APIs (via OpenRouter)
    ├── real_api_validation_results_trail1.json     # Results of real API validation (trial 1)
    ├── real_api_validation_results_trail2.json     # Results of real API validation (trial 2)
    ├── requirements.txt                            # Python dependencies for validation
    ├── .env.example                                # Example environment variables file
    └── README.md                                   # Validation documentation
```

## How to Use This Repository (Quick Start Guide)

This guide will help you set up the environment, read the whitepaper, and run the various simulations and real API validation tests.

### 1. Prerequisites

*   **Python 3.8+**: Ensure Python is installed and accessible via `python3`.
*   **pip**: Python's package installer, usually comes with Python.
*   **git**: For cloning the repository.

### 2. Installation

Clone the repository and install the required Python packages:

```bash
# Clone the repository
git clone git@github.com:supreeth-ravi/agentic-payments-research.git
cd agentic-payments-research

# Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate # On Windows use `venv\Scripts\activate`

# Install Python dependencies for validation (simulation has no dependencies)
cd validation
pip install -r requirements.txt
cd ..
```

*(Note: The simulation framework has no external dependencies. Only the validation tests require dependencies, which are listed in `validation/requirements.txt`.)*

### 3. Read the Whitepaper

To delve into the core research, methodology, and findings:

```bash
open whitepaper/Determinism_in_Agentic_Payments_Whitepaper.md
```

### 4. Run Simulations (80,000 transactions, free)

The simulation framework allows you to test both the direct integration and the mandate architecture with various payment gateway implementations.

**General Command Structure for Direct Integration Simulation:**
```bash
python3 -m simulation.run_simulation [trials_per_scenario] [gateway_name]
```
-   `trials_per_scenario`: Number of times each of the 8 test scenarios will run (e.g., `10000` for 80,000 total transactions per gateway).
-   `gateway_name`: Specify which payment gateway's placeholder to use. Options: `mock`, `stripe`, `razorpay`, `mcp`.

**Examples for Direct Integration Simulation:**

```bash
# Run with the original Mock Payment Gateway
python3 -m simulation.run_simulation 10000 mock
# Expected Result (Mock): ~37% overall failure rate, results saved to simulation/simulation_results.json

# Run with the Stripe Placeholder Gateway
python3 -m simulation.run_simulation 10000 stripe
# Expected Result (Stripe Placeholder): Similar failure rate to Mock, results saved to simulation/mcp/simulation_results/simulation_results_stripe.json

# Run with the Razorpay Placeholder Gateway
python3 -m simulation.run_simulation 10000 razorpay
# Expected Result (Razorpay Placeholder): Similar failure rate to Mock, results saved to simulation/mcp/simulation_results/simulation_results_razorpay.json

# Run with the Generic Multi-Channel Payment (MCP) Gateway
python3 -m simulation.run_simulation 10000 mcp
# Expected Result (Generic MCP Placeholder): Similar failure rate to Mock, results saved to simulation/mcp/simulation_results/simulation_results_genericmcp.json
```

**Run Mandate Architecture Simulation:**

To test the secure mandate-based architecture:

```bash
python3 -m simulation.mandate.run_mandate_simulation 10000
# Expected Result: 0% failure rate, results saved to simulation/mandate/mandate_simulation_results.json
```

### 5. Run Real API Tests (approx. 240-1100+ calls, ~$15+ estimated cost)

Validate simulation accuracy by testing against real production LLMs via the OpenRouter API.

**Prerequisites:**

*   An OpenRouter API Key. You can get one from [openrouter.ai](https://openrouter.ai).
*   Funding in your OpenRouter account.

**Instructions:**

```bash
# Navigate to the validation directory
cd validation

# Export your OpenRouter API key
export OPENROUTER_API_KEY="your-openrouter-api-key"

# Run the validation script
python3 validate_with_real_apis.py
# Results will be saved to validation/real_api_validation_results_trail*.json
```

*(Note: The cost and number of API calls depend on the specific validation trial configuration in `validate_with_real_apis.py`.)*

## Framework Reusability for Researchers

The simulation framework is designed to be reusable for **ANY research testing LLM reliability in critical applications**. While this implementation tests payment systems, the methodology (Monte Carlo simulation + real API validation) can be adapted for:

*   **Medical diagnosis:** Test diagnostic hallucination rates.
*   **Legal research:** Test citation fabrication rates.
*   **Code generation:** Test security vulnerability rates.
*   **Financial analysis:** Test calculation error rates.
*   **Any critical domain:** Prove LLM safety before deployment.

**Benefits:**

*   99.7% cost reduction ($15 vs $4,800 for 160K transactions).
*   1000x faster results.
*   Statistically significant (80K+ tests per architecture).
*   Real API validation included.

See [simulation/FRAMEWORK_GUIDE.md](simulation/FRAMEWORK_GUIDE.md) for a complete adaptation guide with examples.

## Contact

**Supreeth Ravi** - Principal Author & Research Lead
*   Email: supreeth.ravi@phronetic.ai
*   Website: [https://supreethravi.com](https://supreethravi.com)
*   LinkedIn: [https://www.linkedin.com/in/supreeth-ravi/](https://www.linkedin.com/in/supreeth-ravi/)

## Citation

If you reference this work, please cite the whitepaper as:

```
PayCentral Research Team. (2025). "Determinism in Agentic Payments:
Why Direct LLM-Payment Integration Fails and How Mandate Architecture
Achieves 0% Failure Rate - An Empirical Study of 160,000 Transactions."
PayCentral Technical Whitepaper. https://paycentral.com/research/determinism-whitepaper
```