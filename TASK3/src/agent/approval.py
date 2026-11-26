from pydantic import ValidationError

from src.agent.tool_executor import (
    TOOL_FUNCTIONS,
    WRITE_TOOLS,
    TOOL_VALIDATORS,
)


def execute_approved_action(
    tool_name: str,
    arguments: dict,
    approved: bool
):

    if tool_name not in WRITE_TOOLS:
        return {
            "status": "error",
            "message": "This is not an approval-required operation."
        }

    if not approved:
        return {
            "status": "rejected",
            "message": "The action was rejected by the user."
        }

    try:
        validator = TOOL_VALIDATORS[tool_name]

        validated = validator(**arguments)
        arguments = validated.model_dump()

        result = TOOL_FUNCTIONS[tool_name](**arguments)

        return {
            "status": "success",
            "tool": tool_name,
            "result": result
        }

    except (ValidationError, TypeError, ValueError) as error:
        return {
            "status": "error",
            "message": str(error)
        }

    except Exception as error:
        return {
            "status": "error",
            "message": f"Approved action failed: {error}"
        }
# Stores actions waiting for human approval
pending_approvals = {}


def request_approval(tool_name: str, arguments: dict):
    from uuid import uuid4

    approval_id = str(uuid4())

    pending_approvals[approval_id] = {
        "tool": tool_name,
        "arguments": arguments
    }

    return {
        "status": "approval_required",
        "approval_id": approval_id,
        "tool": tool_name,
        "arguments": arguments,
        "message": "Human approval is required before this action."
    }
def process_approval(approval_id: str, approved: bool):
    pending = pending_approvals.pop(approval_id, None)

    if pending is None:
        return {
            "status": "error",
            "message": "Approval request not found or already processed."
        }

    return execute_approved_action(
        tool_name=pending["tool"],
        arguments=pending["arguments"],
        approved=approved
    )