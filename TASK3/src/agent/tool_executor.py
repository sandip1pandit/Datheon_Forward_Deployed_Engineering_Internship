import json
from pydantic import ValidationError

from src.tools.erp_tools import (
    get_inventory,
    get_product,
    update_lead,
    create_ticket,
)

from src.agent.validators import (
    GetProductArgs,
    UpdateLeadArgs,
    CreateTicketArgs,
)


TOOL_FUNCTIONS = {
    "get_inventory": get_inventory,
    "get_product": get_product,
    "update_lead": update_lead,
    "create_ticket": create_ticket,
}

WRITE_TOOLS = {
    "update_lead",
    "create_ticket",
}

TOOL_VALIDATORS = {
    "get_product": GetProductArgs,
    "update_lead": UpdateLeadArgs,
    "create_ticket": CreateTicketArgs,
}


def execute_tool(tool_name: str, arguments: str):

    if tool_name not in TOOL_FUNCTIONS:
        return {
            "status": "error",
            "message": f"Unknown tool: {tool_name}"
        }

    try:
        parsed_arguments = json.loads(arguments)

        if not isinstance(parsed_arguments, dict):
            raise ValueError("Tool arguments must be a JSON object.")

        # Validate arguments before execution
        validator = TOOL_VALIDATORS.get(tool_name)

        if validator:
            validated = validator(**parsed_arguments)
            parsed_arguments = validated.model_dump()

        # Require approval for write operations
        if tool_name in WRITE_TOOLS:
            return {
                "status": "approval_required",
                "tool": tool_name,
                "arguments": parsed_arguments,
                "message": "Human approval is required before this action."
            }

        result = TOOL_FUNCTIONS[tool_name](**parsed_arguments)

        return {
            "status": "success",
            "tool": tool_name,
            "result": result
        }

    except (json.JSONDecodeError, TypeError, ValueError, ValidationError) as error:
        return {
            "status": "error",
            "message": str(error)
        }

    except Exception as error:
        return {
            "status": "error",
            "message": f"Tool execution failed: {error}"
        }