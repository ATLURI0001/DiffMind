# Mock LLM Evaluation Matrix & Testing Strategy

## Test Tiers
1. **Unit Tier**: Fast, deterministic mock responses testing parser resilience, JSON schema validation, and retry logic.
2. **Golden Dataset Tier**: Curated set of 50 synthetically corrupted diffs to benchmark recall and precision against known vulnerabilities.
3. **Integration Tier**: Live API end-to-end evaluation with strict budget limits.

## Target Accuracy Thresholds
- False Positive Rate: < 5% on formatting/linter warnings
- True Positive Rate: > 98% on critical SQLi, XSS, and authentication bypasses
