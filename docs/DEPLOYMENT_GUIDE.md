# Production Deployment Guide: Kubernetes Sidecar & Docker Compose

## Architecture
DiffMind operates as an asynchronous worker consuming webhook events from GitHub Enterprise and GitLab via a Redis message broker.

## Resource Allocation
- Memory Request / Limit: 512Mi / 2Gi
- CPU Request / Limit: 250m / 1000m
- Liveness Probe: HTTP GET /healthz (timeout 2s)
- Readiness Probe: HTTP GET /readyz (checks Redis connectivity and active worker pools)
