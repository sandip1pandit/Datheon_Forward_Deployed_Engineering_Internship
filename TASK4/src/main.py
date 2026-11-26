
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel, Field
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from src.agent.agent import run_agent
from src.core.config import validate_config
from src.metrics import (
    HTTP_REQUESTS,
    REQUEST_LATENCY,
    HTTP_ERRORS,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    validate_config()
    logger.info("AI microservice started.")
    yield
    logger.info("AI microservice stopped.")


app = FastAPI(
    title="Enterprise AI Agent Microservice",
    description="Dockerized ERP/CRM AI agent with Prometheus monitoring.",
    version="1.0.0",
    lifespan=lifespan,
)


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Message for the enterprise AI agent."
    )


class ChatResponse(BaseModel):
    status: str
    response: str | dict


@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.perf_counter()

    try:
        response = await call_next(request)

        duration = time.perf_counter() - start_time
        endpoint = request.url.path

        HTTP_REQUESTS.labels(
            method=request.method,
            endpoint=endpoint,
            status=str(response.status_code)
        ).inc()

        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=endpoint
        ).observe(duration)

        if response.status_code >= 400:
            HTTP_ERRORS.labels(
                endpoint=endpoint,
                error_type=f"http_{response.status_code}"
            ).inc()

        return response

    except Exception as exc:
        duration = time.perf_counter() - start_time

        HTTP_REQUESTS.labels(
            method=request.method,
            endpoint=request.url.path,
            status="500"
        ).inc()

        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)

        HTTP_ERRORS.labels(
            endpoint=request.url.path,
            error_type=type(exc).__name__
        ).inc()

        logger.exception("Unhandled request error")
        raise


@app.get("/")
async def root():
    return {
        "service": "Enterprise AI Agent",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "enterprise-ai-agent"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        result = run_agent(request.message)

        if not isinstance(result, dict):
            raise ValueError("Agent returned an invalid response.")

        return ChatResponse(
            status=result.get("status", "unknown"),
            response=result.get("response", "")
        )

    except Exception as exc:
        logger.exception("Agent execution failed")

        raise HTTPException(
            status_code=500,
            detail="The AI agent could not process the request."
        ) from exc


@app.get("/metrics")
async def metrics():
    content = generate_latest()

    return Response(
        content=content,
        media_type=CONTENT_TYPE_LATEST
    )
