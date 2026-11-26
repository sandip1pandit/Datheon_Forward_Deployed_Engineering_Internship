# Enterprise AI Agent Microservice
## Task 4 – Client VPC Deployment

A Dockerized enterprise AI microservice built using FastAPI, Groq, Docker Compose, and Prometheus.

The service reuses the autonomous ERP/CRM agent from Task 3 and exposes it through HTTP endpoints. It includes a separate ERP backend for inventory, CRM, and support operations.

---

## 1. Architecture

The deployment contains three Docker services:

- **AI Service:** FastAPI application running the enterprise AI agent.
- **ERP Service:** Provides inventory, CRM, and support-ticket APIs.
- **Prometheus:** Collects and stores AI service metrics.

```text
              CLIENT APPLICATION
                      |
                      | HTTP Requests
                      v
             +---------------------+
             |    AI Service      |
             |    FastAPI         |
             |    Port 8000       |
             +---------------------+
                      |
             +--------+--------+
             |                 |
             v                 v
       +-----------+      +----------------+
       | Groq LLM  |      |  ERP Service   |
       | API       |      |  Port 8001     |
       +-----------+      +----------------+
                                  |
                         Inventory / CRM /
                         Support Tickets

             +---------------------+
             |     Prometheus      |
             |     Port 9090       |
             +---------------------+
                      |
                      | Scrapes /metrics
                      v
             +---------------------+
             |    AI Service      |
             +---------------------+
```

The AI service communicates with the ERP service internally through Docker networking using `http://erp-service:8001`.

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| Python 3.12 | Application runtime |
| FastAPI | REST APIs |
| Groq | LLM inference |
| Docker | Containerization |
| Docker Compose | Service orchestration |
| Prometheus | Metrics monitoring |
| pytest | Automated testing |
| httpx | HTTP client and benchmarking |

## 3. Prerequisites

The client environment requires:

- Docker Desktop or Docker Engine
- Docker Compose
- A valid Groq API key
- Available ports 8000, 8001, and 9090

## 4. Project Structure

```text
TASK4/
|
|-- src/
|   |-- main.py
|   |-- metrics.py
|   |-- agent/
|   |-- api/
|   |   |-- erp_main.py
|   |   |-- mock_data.py
|   |-- core/
|   |-- tools/
|
|-- tests/
|   |-- test_api.py
|
|-- benchmarks/
|   |-- benchmark.py
|
|-- prometheus/
|   |-- prometheus.yml
|
|-- Dockerfile
|-- docker-compose.yml
|-- requirements.txt
|-- .env.example
|-- .dockerignore
|-- .gitignore
|-- README.md
```

## 5. Environment Configuration

Create a `.env` file in the project root.

Configure:

```dotenv
GROQ_API_KEY=your_actual_groq_api_key
MODEL_NAME=openai/gpt-oss-120b
API_HOST=0.0.0.0
API_PORT=8000
```

Replace the placeholder with your own Groq API key.

**Security recommendations:**

- Never commit `.env` to Git.
- Never hardcode API keys in source code.
- Restrict access to environment secrets.
- Rotate credentials if they are exposed.

## 6. Deployment Instructions

### Step 1: Build and start services

```powershell
docker compose up --build -d
```

### Step 2: Check running containers

```powershell
docker compose ps
```

### Step 3: View application logs

AI service:

```powershell
docker compose logs -f ai-service
```

ERP service:

```powershell
docker compose logs -f erp-service
```

Prometheus:

```powershell
docker compose logs -f prometheus
```

### Step 4: Stop services

```powershell
docker compose down
```

To also remove stored Prometheus data:

```powershell
docker compose down -v
```

## 7. API Documentation

### AI Service

Base URL:

```text
http://localhost:8000
```

#### Health Check

Endpoint:

```http
GET /health
```

Example response:

```json
{
  "status": "healthy",
  "service": "enterprise-ai-agent"
}
```

#### Chat Endpoint

Endpoint:

```http
POST /chat
```

Request:

```json
{
  "message": "What products are available?"
}
```

Example response:

```json
{
  "status": "completed",
  "response": "Here are the available products..."
}
```

The service also supports approval and rejection requests using the approval ID returned by the agent.

#### Root Endpoint

```http
GET /
```

Returns service name, version, and running status.

#### Metrics Endpoint

```http
GET /metrics
```

Returns Prometheus-formatted application metrics.

### ERP Backend Service

Base URL:

```text
http://localhost:8001
```

Available endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | ERP health check |
| GET | `/inventory` | Retrieve all products |
| GET | `/inventory/{product_id}` | Retrieve a specific product |
| PATCH | `/leads/{lead_id}` | Update a CRM lead |
| POST | `/tickets` | Create a support ticket |

The AI service accesses these endpoints internally through the Docker network.

## 8. Client Integration Example

Python example using `httpx`:

```python
import httpx

BASE_URL = "http://localhost:8000"

response = httpx.post(
    f"{BASE_URL}/chat",
    json={
        "message": "What products are available?"
    },
    timeout=120
)

response.raise_for_status()

print(response.json())
```

Health check:

```python
response = httpx.get(
    f"{BASE_URL}/health",
    timeout=5
)

print(response.json())
```

The client only needs to communicate with the AI service. The AI service handles communication with the ERP backend.

## 9. Prometheus Monitoring

Prometheus dashboard:

```text
http://localhost:9090
```

AI service metrics endpoint:

```text
http://localhost:8000/metrics
```

Prometheus scrapes the AI service every five seconds.

The service exposes:

| Metric | Description |
|---|---|
| `http_requests_total` | Total HTTP requests |
| `http_request_duration_seconds` | Request latency distribution |
| `llm_tokens_total` | Prompt and completion token usage |
| `http_errors_total` | HTTP and application errors |

Example PromQL queries:

Total requests:

```promql
sum(http_requests_total)
```

Average request latency over five minutes:

```promql
rate(http_request_duration_seconds_sum[5m])
/
rate(http_request_duration_seconds_count[5m])
```

Request rate:

```promql
rate(http_requests_total[5m])
```

Error rate:

```promql
rate(http_errors_total[5m])
```

Total prompt tokens:

```promql
llm_tokens_total{token_type="prompt"}
```

Total completion tokens:

```promql
llm_tokens_total{token_type="completion"}
```

## 10. Latency Benchmarking

The project includes a Python benchmarking utility.

First, install dependencies if benchmarking outside Docker:

```powershell
pip install -r requirements.txt
```

Run 100 health-check requests with concurrency 10:

```powershell
python benchmarks/benchmark.py --endpoint /health --requests 100 --concurrency 10
```

Benchmark the chat endpoint:

```powershell
python benchmarks/benchmark.py --endpoint /chat --requests 5 --concurrency 1
```

The benchmark reports:

- Minimum latency
- Maximum latency
- Average latency
- P50 latency
- P95 latency
- P99 latency
- Successful and failed requests
- Requests per second

**Note:** Chat benchmarking invokes the LLM and may consume API quota. Start with a small number of requests.

### Verified Benchmark Results

The following results were obtained during local testing:

| Measurement | Result |
|---|---:|
| Endpoint | `/health` |
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
| Throughput | 264.16 requests/sec |

These measurements represent the health endpoint, not LLM inference latency.

## 11. Health Checks and Reliability

Both application services include Docker health checks:

- AI service: `http://localhost:8000/health`
- ERP service: `http://localhost:8001/health`

Docker Compose waits for the ERP service to become healthy before starting the AI service. Prometheus waits for the AI service to become healthy.

The services use restart policies to recover from container failures.

## 12. Security Considerations

- API keys are supplied through environment variables.
- `.env` is excluded from Git and Docker build context.
- The application runs as a non-root container user.
- Prometheus and application services communicate through an internal Docker network.
- The API validates incoming chat messages.
- Production deployments should use TLS, authentication, network restrictions, and a managed secrets system.

## 13. Running Tests

Run:

```powershell
python -m pytest tests -v
```

The automated tests cover:

- Root endpoint
- Health endpoint
- Chat endpoint
- Input validation
- Error handling
- Prometheus metrics
- Unknown endpoints

## 14. Production Deployment Notes

For a real client VPC deployment:

1. Provision a Linux VM or container host.
2. Configure private networking and firewall rules.
3. Store Groq credentials in the client's secrets manager.
4. Deploy the Docker Compose services.
5. Restrict access to the API and Prometheus ports.
6. Configure TLS and API authentication.
7. Monitor latency, token consumption, and errors.
8. Perform load testing before production rollout.

## 15. Limitations

- Groq inference requires internet connectivity.
- ERP/CRM mock data is in-memory and is not persistent.
- Approval state is currently in-memory.
- Prometheus application counters reset when the API process restarts.
- Prometheus storage persists through a Docker volume.
- The ERP backend currently does not expose its own Prometheus application metrics.
- Production use requires persistent storage and stronger access controls.

---

**Project:** Task 4 – Client VPC Deployment
**Service:** Enterprise AI Agent Microservice
**Version:** 1.0.0
