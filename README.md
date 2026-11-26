
# Datheon Forward Engineering Internship — Final Project Report

## Repository Overview

- **Repository:** `Datheon_Forward_Engineering_Internship`
- **GitHub:** https://github.com/sandip1pandit/Datheon_Forward_Engineering_Internship
- **Primary branch:** `main`
- **Submission scope:** Tasks 1–4
- **Final Task 4 commit:** `65dcc08`

This repository contains four engineering tasks covering document ingestion, secure retrieval-augmented generation, autonomous tool-using agents, and containerized microservice deployment.

---

## Task 1 — Legacy Data ETL Pipeline

**Commit:** `141bce3` — `Add Task 1 legacy data ETL pipeline`

### Objective

Build a document ingestion and retrieval pipeline for legacy enterprise data.

### Features

- Extract content from PDF, CSV, and Markdown documents.
- Preserve important document metadata, including department, access tier, and creation date.
- Split extracted content into chunks suitable for embedding and retrieval.
- Generate embeddings and store document representations in Qdrant.
- Support semantic search and metadata-based filtering.
- Support batch ingestion.
- Include tests and documentation.

### Supporting Commits

- `526b967` — Add embedding-based semantic chunking.
- `6c1108b` — Fix processed output collisions and add PDF extraction test.
- `f486b0d` — Add enterprise metadata propagation and date filtering.

---

## Task 2 — Enterprise Multi-Tenant RAG System

**Commit:** `e1fed61` — `Complete Task 2 enterprise multi-tenant RAG system`

### Objective

Build an enterprise RAG system that retrieves relevant information while enforcing tenant isolation and role-based access control.

### Features

- Multi-tenant document and retrieval isolation.
- Role-based access control (RBAC).
- Query rewriting to improve retrieval.
- Cross-encoder reranking of retrieved results.
- Citation verification.
- Hallucination guardrails and abstention when evidence is insufficient.
- Authorization checks before reranking and answer generation.

---

## Task 3 — Autonomous Field Agent

**Commit:** `4b76928` — `Complete Task 3 Autonomous Field Agent`

### Objective

Build an autonomous agent that can select and execute enterprise tools through API integrations, while controlling sensitive write operations.

### Features

- Tool-calling agent for enterprise inventory, CRM, and support workflows.
- Inventory lookup and product lookup.
- CRM lead updates.
- Support-ticket creation.
- Human approval flow for write operations.
- Approval and rejection handling.
- Tool argument validation and execution.
- Event logging and configuration/retry support.
- ERP API integration using FastAPI.

---

## Task 4 — Client VPC Deployment: Dockerized Microservice and Latency Benchmarks

**Commit:** `65dcc08` — `Complete Task 4 Dockerized AI microservice deployment`

### Objective

Package the AI agent as a deployable microservice, integrate it with an ERP backend, and expose operational metrics for monitoring.

### Architecture

The Docker Compose deployment contains three services:

1. **AI service** — FastAPI application exposing the enterprise agent.
2. **ERP service** — FastAPI backend providing mock inventory, CRM, and support-ticket endpoints.
3. **Prometheus** — Scrapes application metrics from the AI service.

### Features

- Dockerfile for the AI service.
- Docker Compose orchestration for all three services.
- Environment-based configuration and secret handling.
- `.env.example` template; actual `.env` file is excluded from version control.
- Health-check endpoints and container health checks.
- Prometheus metrics for HTTP request counts, request latency, error counts, and LLM token usage.
- Internal Docker networking between the AI service and ERP service.
- Client integration documentation.
- HTTP benchmark script.

### API Endpoints

#### AI Service — Port 8000

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Service information |
| GET | `/health` | Health status |
| POST | `/chat` | Submit a message to the AI agent |
| GET | `/metrics` | Prometheus metrics |

#### ERP Service — Port 8001

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | ERP service information |
| GET | `/health` | Health status |
| GET | `/inventory` | List inventory |
| GET | `/inventory/{product_id}` | Retrieve a product |
| PATCH | `/leads/{lead_id}` | Update a lead |
| POST | `/tickets` | Create a support ticket |

### Validation Results

- Python compilation completed successfully.
- Automated API tests: **8 passed**.
- Docker Compose configuration validation completed successfully.
- AI service and ERP service reported healthy.
- Prometheus scrape target confirmed **UP**.
- AI chat endpoint successfully returned inventory information.
- Prometheus metrics endpoint exposed HTTP request, latency, and LLM token metrics.

### Health Endpoint Benchmark

Benchmark command:

```powershell
.\.venv\Scripts\python.exe .\benchmarks\benchmark.py --endpoint /health --requests 100 --concurrency 10
```

Recorded results:

| Metric | Result |
|---|---:|
| Total requests | 100 |
| Successful requests | 100 |
| Failed requests | 0 |
| Total duration | 0.379 seconds |
| Minimum latency | 6.49 ms |
| Maximum latency | 167.64 ms |
| Average latency | 24.61 ms |
| P50 latency | 20.11 ms |
| P95 latency | 49.00 ms |
| P99 latency | 64.52 ms |
| Throughput | 264.16 requests/second |

**Note:** These measurements are for the `/health` endpoint. They are not LLM inference latency measurements.

---

## Git Commit History

The final verified commit history on `main` was:

| Commit | Description |
|---|---|
| `65dcc08` | Complete Task 4 Dockerized AI microservice deployment |
| `4b76928` | Complete Task 3 Autonomous Field Agent |
| `e1fed61` | Complete Task 2 enterprise multi-tenant RAG system |
| `f486b0d` | Add enterprise metadata propagation and date filtering |
| `6c1108b` | Fix processed output collisions and add PDF extraction test |
| `526b967` | Add embedding-based semantic chunking |
| `141bce3` | Add Task 1 legacy data ETL pipeline |

The local `main` branch was confirmed synchronized with `origin/main`.

---

## Repository Structure

```text
FDE/
├── FINAL_SUBMISSION_REPORT.md
├── TASK1/
├── TASK2/
├── TASK3/
└── TASK4/
    ├── benchmarks/
    ├── prometheus/
    ├── src/
    │   ├── agent/
    │   ├── api/
    │   ├── core/
    │   └── tools/
    └── tests/
```

---

## Final Status

The four task commits are present on the `main` branch, and the branch was confirmed synchronized with `origin/main`.

**Outstanding repository note:** At the final status check, `TASK2/test_admin_access.py` appeared as an untracked file. It was not included in the Task 4 commit. Review this file and decide whether it belongs in the Task 2 submission before considering the repository completely clean.

---

*Prepared as a consolidated overview of the Datheon Forward Engineering Internship Tasks 1–4.*
