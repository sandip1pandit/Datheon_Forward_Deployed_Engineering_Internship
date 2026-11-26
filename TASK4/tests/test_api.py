
import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client(monkeypatch):
    # Avoid requiring a real Groq API key during tests.
    monkeypatch.setattr(
        "src.main.validate_config",
        lambda: True
    )

    with TestClient(app) as test_client:
        yield test_client


def test_root_endpoint(client):
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "running"


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_chat_endpoint(client, monkeypatch):
    def mock_run_agent(message):
        return {
            "status": "completed",
            "response": f"Processed: {message}"
        }

    monkeypatch.setattr(
        "src.main.run_agent",
        mock_run_agent
    )

    response = client.post(
        "/chat",
        json={"message": "Hello"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["response"] == "Processed: Hello"


def test_chat_empty_message(client):
    response = client.post(
        "/chat",
        json={"message": ""}
    )

    assert response.status_code == 422


def test_chat_missing_message(client):
    response = client.post(
        "/chat",
        json={}
    )

    assert response.status_code == 422


def test_chat_agent_error(client, monkeypatch):
    def mock_run_agent(message):
        raise RuntimeError("Test error")

    monkeypatch.setattr(
        "src.main.run_agent",
        mock_run_agent
    )

    response = client.post(
        "/chat",
        json={"message": "Test"}
    )

    assert response.status_code == 500


def test_metrics_endpoint(client):
    response = client.get("/metrics")

    assert response.status_code == 200
    assert "http_requests_total" in response.text
    assert "http_request_duration_seconds" in response.text
    assert "llm_tokens_total" in response.text


def test_unknown_endpoint(client):
    response = client.get("/unknown")

    assert response.status_code == 404
