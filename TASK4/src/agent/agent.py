
import json

from src.core.llm import client
from src.core.config import MODEL_NAME
from src.agent.tool_definitions import TOOLS
from src.agent.tool_executor import execute_tool
from src.agent.approval import (
    request_approval,
    process_approval,
    pending_approvals,
)
from src.agent.logger import log_event
from src.metrics import record_token_usage


def run_agent(user_message: str):

    log_event("user", user_message)

    message = user_message.strip().lower()
    parts = message.split()

    # Handle approval or rejection
    if parts and parts[0] in {"approve", "reject"}:

        if len(parts) != 2:
            return {
                "status": "error",
                "response": (
                    "Please provide the exact approval ID. "
                    "Example: approve <approval_id>"
                )
            }

        approval_id = parts[1]

        if approval_id not in pending_approvals:
            return {
                "status": "error",
                "response": "Invalid or expired approval ID."
            }

        approved = parts[0] == "approve"

        result = process_approval(approval_id, approved)

        log_event("approval", json.dumps(result))

        return {
            "status": result["status"],
            "response": result
        }

    approval_pending = False

    messages = [
        {
            "role": "system",
            "content": (
                "You are an autonomous enterprise ERP/CRM assistant. "
                "You have access to tools for inventory, CRM, and support operations. "
                "When a business operation matches an available tool, "
                "you MUST call the appropriate tool. "
                "Write operations require human approval. "
                "Never claim an operation was completed unless confirmed."
            )
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    for step in range(5):

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.2
        )

        # Record actual token usage for every LLM call.
        usage = response.usage

        if usage:
            record_token_usage(
                prompt_tokens=usage.prompt_tokens or 0,
                completion_tokens=usage.completion_tokens or 0
            )

        assistant_message = response.choices[0].message

        if not assistant_message.tool_calls:

            final_response = assistant_message.content or ""

            log_event("final", final_response)

            return {
                "status": (
                    "approval_required"
                    if approval_pending
                    else "completed"
                ),
                "response": final_response
            }

        messages.append(
            assistant_message.model_dump(exclude_none=True)
        )

        for tool_call in assistant_message.tool_calls:

            tool_name = tool_call.function.name
            arguments = tool_call.function.arguments

            log_event("agent", f"Selected tool: {tool_name}")
            log_event("action", f"Executing tool: {tool_name}")

            result = execute_tool(tool_name, arguments)

            if result.get("status") == "approval_required":

                result = request_approval(
                    tool_name,
                    result["arguments"]
                )

                approval_pending = True

            log_event(
                "observation",
                f"Tool result: {json.dumps(result)}"
            )

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

    log_event("error", "Maximum tool execution steps reached.")

    return {
        "status": (
            "approval_required"
            if approval_pending
            else "error"
        ),
        "response": "Maximum tool execution steps reached."
    }
