from src.agent.approval import (
    request_approval,
    process_approval,
    pending_approvals,
)


def test_approval_request_creation():
    request = request_approval(
        "update_lead",
        {"lead_id": 102, "status": "qualified"}
    )

    assert request["status"] == "approval_required"
    assert request["approval_id"] in pending_approvals


def test_approval_execution():
    request = request_approval(
        "update_lead",
        {"lead_id": 102, "status": "qualified"}
    )

    result = process_approval(
        request["approval_id"],
        True
    )

    assert result["status"] == "success"
    assert request["approval_id"] not in pending_approvals


def test_approval_rejection():
    request = request_approval(
        "update_lead",
        {"lead_id": 102, "status": "qualified"}
    )

    result = process_approval(
        request["approval_id"],
        False
    )

    assert result["status"] == "rejected"
    assert request["approval_id"] not in pending_approvals


def test_duplicate_approval():
    result = process_approval(
        "invalid-approval-id",
        True
    )

    assert result["status"] == "error"
from src.agent import agent as agent_module


def test_agent_rejects_invalid_approval_id():
    result = agent_module.run_agent("approve invalid-id")

    assert result["status"] == "error"
    assert result["response"] == "Invalid or expired approval ID."


def test_agent_requires_approval_id():
    result = agent_module.run_agent("approve")

    assert result["status"] == "error"
    assert "exact approval ID" in result["response"]


def test_agent_uses_exact_approval_id(monkeypatch):
    approval_id = "test-approval-123"

    monkeypatch.setitem(
        agent_module.pending_approvals,
        approval_id,
        {"tool": "update_lead", "arguments": {}}
    )

    def mock_process_approval(received_id, approved):
        assert received_id == approval_id
        assert approved is True
        return {"status": "success"}

    monkeypatch.setattr(
        agent_module,
        "process_approval",
        mock_process_approval
    )

    result = agent_module.run_agent("approve " + approval_id)

    assert result["status"] == "success"