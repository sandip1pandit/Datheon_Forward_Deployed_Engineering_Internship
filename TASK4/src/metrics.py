
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Total HTTP requests
HTTP_REQUESTS = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"]
)

# HTTP request processing time
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "endpoint"]
)

# Total LLM tokens
LLM_TOKENS = Counter(
    "llm_tokens_total",
    "Total LLM tokens consumed",
    ["token_type"]
)

# Total application errors
HTTP_ERRORS = Counter(
    "http_errors_total",
    "Total number of HTTP errors",
    ["endpoint", "error_type"]
)


def record_token_usage(prompt_tokens: int, completion_tokens: int):
    """Record actual LLM token consumption."""

    if prompt_tokens > 0:
        LLM_TOKENS.labels(token_type="prompt").inc(prompt_tokens)

    if completion_tokens > 0:
        LLM_TOKENS.labels(token_type="completion").inc(completion_tokens)


def get_metrics():
    """Generate Prometheus-compatible metrics."""

    return generate_latest(), CONTENT_TYPE_LATEST
