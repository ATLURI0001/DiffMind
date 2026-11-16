# Multi-Model Consensus Architecture Specification

## Overview
DiffMind coordinates multiple LLM providers (e.g. Gemini, Claude, GPT) to analyze code changes and synthesize a unified, high-confidence review report.

## Consensus Mechanism
1. **Parallel Inference**: Candidate models independently parse the unified Git diff.
2. **Conflict Resolution**: Disagreements on issue severity (CRITICAL vs WARNING) are weighted by calibrated historical accuracy metrics.
3. **Token Budget Enforcement**: Context window truncation heuristics prioritize AST-modified function boundaries over unmodified contextual lines.

## Token Quotas
- Per-PR Maximum Context: 128,000 tokens
- Max Analysis Latency: 4.5 seconds per 500 lines of diff
