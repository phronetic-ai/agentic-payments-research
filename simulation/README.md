# Simulation (80,000 transactions)

Monte Carlo simulation testing LLM payment behavior.

## Run Tests

### Direct Integration (Broken)
```bash
python run_simulation.py 10000
# 10000 = trials PER scenario
# 8 scenarios × 10,000 = 80,000 total transactions
# Result: 36.98% failure rate
# Output: simulation_results.json
```

### Mandate Architecture (Secure)
```bash
cd mandate
python run_mandate_simulation.py 10000
# Result: 0% failure rate
# Output: mandate_simulation_results.json
```

## Files

- **naive_agent.py** - Direct integration agent (fails)
- **test_scenarios.py** - 8 failure modes
- **mandate/** - Secure architecture with cryptographic sealing

## For Researchers: Reusability

**This framework can be adapted for ANY domain testing LLM reliability.**

The methodology (Monte Carlo simulation + real API validation) is universal, even though this implementation is payment-specific.

### What You Can Reuse:
- Simulation runner pattern (`run_simulation.py`)
- Base scenario class (`TestScenario`)
- Probability-based failure modeling
- Validation approach (80K simulated + 240 real API calls)

### What You Replace:
- Agent implementation (your domain instead of payments)
- Test scenarios (your failure modes)
- Test data (your domain-specific cases)

### Example Adaptations:
- **Medical:** Test diagnostic hallucination rates
- **Legal:** Test citation fabrication rates
- **Code:** Test security vulnerability injection rates
- **Finance:** Test calculation error rates

**See [REUSABILITY_GUIDE.md](REUSABILITY_GUIDE.md) for complete adaptation guide with examples.**

### Cost Savings:
- **With framework:** 80K tests FREE (simulation) + 240 tests $15 (validation) = **$15 total**
- **Without framework:** 80K real API tests = **$4,800**
- **Savings:** 99.7% cost reduction + 1000x faster
