# Latency Breakdown & Rate Limiting Runbook

## Latency SLA
- Diff parsing: < 150ms
- Context window packing: < 250ms
- Multi-model evaluation: < 3500ms
- Report synthesis: < 300ms

## Rate Limiting Handling
When encountering HTTP 429 / RESOURCE_EXHAUSTED responses:
1. Trigger full-jitter exponential backoff (base: 250ms, max: 8000ms).
2. Failover to secondary tiered model provider after 2 consecutive timeouts.
3. Emit structured telemetry events with provider, retry count, and queue dwell time.
