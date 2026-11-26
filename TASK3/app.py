from src.agent.logger import get_execution_logs
import json
import re

import streamlit as st
from src.agent.agent import run_agent

st.set_page_config(
    page_title="Autonomous Field Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Autonomous Field Agent")
st.caption("Enterprise ERP/CRM Tool Orchestration")

st.divider()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_approval_id" not in st.session_state:
    st.session_state.pending_approval_id = None


def format_response(response):
    """Convert agent responses into displayable text."""
    if isinstance(response, dict):
        return json.dumps(response, indent=2)
    return str(response)


# Display conversation history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# Chat input is disabled while approval is pending
user_input = st.chat_input(
    "Ask me to check inventory, update a lead, or create a ticket...",
    disabled=st.session_state.pending_approval_id is not None
)

# Process user request
if user_input:

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Agent is processing your request..."):
            result = run_agent(user_input)

        response = format_response(result.get("response"))

        st.markdown(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })

    # Extract approval ID from the agent response
    if result.get("status") == "approval_required":
        match = re.search(
            r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-"
            r"[0-9a-fA-F]{12}\b",
            response
        )

        if match:
            st.session_state.pending_approval_id = match.group(0)

    st.rerun()


# Human approval controls
if st.session_state.pending_approval_id:

    st.divider()
    st.subheader("Human Approval Required")

    st.write(
        "The agent is waiting for your decision. "
        "Review the requested operation before proceeding."
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Approve", type="primary", use_container_width=True):

            approval_id = st.session_state.pending_approval_id

            with st.spinner("Executing approved operation..."):
                result = run_agent("approve " + approval_id)

            response = format_response(result.get("response"))

            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

            st.session_state.pending_approval_id = None
            st.rerun()

    with col2:
        if st.button("Reject", use_container_width=True):

            approval_id = st.session_state.pending_approval_id

            result = run_agent("reject " + approval_id)

            response = format_response(result.get("response"))

            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })

            st.session_state.pending_approval_id = None
            st.rerun()
# Agent execution logs
st.divider()

with st.expander("View Agent Execution Logs"):

    logs = get_execution_logs()

    if logs:
        for log in reversed(logs):
            st.caption(
                f"{log['timestamp']} | "
                f"{log['event'].upper()}"
            )
            st.write(log["message"])
            st.divider()
    else:
        st.info("No execution logs available yet.")