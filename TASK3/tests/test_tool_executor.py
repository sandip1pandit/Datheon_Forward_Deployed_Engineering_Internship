from src.agent.tool_executor import execute_tool


def test_unknown_tool():
    result = execute_tool("unknown_tool", "{}")

    assert result["status"] == "error"


def test_invalid_json():
    result = execute_tool("get_product", "invalid json")

    assert result["status"] == "error"


def test_invalid_lead_arguments():
    result = execute_tool(
        "update_lead",
        '{"lead_id": -5, "status": "unknown"}'
    )

    assert result["status"] == "error"


def test_write_tool_requires_approval():
    result = execute_tool(
        "update_lead",
        '{"lead_id": 102, "status": "qualified"}'
    )

    assert result["status"] == "approval_required"