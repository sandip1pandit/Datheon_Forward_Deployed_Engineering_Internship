from src.agent.approval import execute_approved_action


def test_rejected_action():
    result = execute_approved_action(
        "update_lead",
        {"lead_id": 102, "status": "qualified"},
        False
    )

    assert result["status"] == "rejected"


def test_invalid_approved_action():
    result = execute_approved_action(
        "update_lead",
        {"lead_id": -5, "status": "unknown"},
        True
    )

    assert result["status"] == "error"


def test_non_write_tool_approval():
    result = execute_approved_action(
        "get_inventory",
        {},
        True
    )

    assert result["status"] == "error"