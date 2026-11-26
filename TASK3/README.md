
# Autonomous Field Agent – Enterprise ERP/CRM Tool Orchestration

## Overview

The Autonomous Field Agent is an AI-powered application that understands business requests and executes operations using enterprise ERP/CRM tools.

It uses Groq function calling to select the appropriate tool, validates its arguments, executes API operations, and requests human approval before sensitive write operations.

## Features

- AI-powered tool selection using Groq.
- Mock ERP/CRM REST API built with FastAPI.
- Inventory lookup and product details.
- CRM lead status updates.
- Customer support ticket creation.
- Input validation using Pydantic.
- Human approval and rejection for write operations.
- Unique approval IDs to authorize pending actions.
- Automatic retry for temporary read-operation failures.
- Execution logs for agent actions and observations.
- Streamlit user interface.

## Available Tools

| Tool | Description | Approval |
|---|---|---|
| get_inventory | Retrieve all inventory | Not required |
| get_product | Retrieve product details | Not required |
| update_lead | Update CRM lead status | Required |
| create_ticket | Create a support ticket | Required |

## Project Structure

```text
TASK3/
├── app.py
├── requirements.txt
├── .env
├── .gitignore
├── data/
├── src/
│   ├── agent/
│   │   ├── agent.py
│   │   ├── approval.py
│   │   ├── logger.py
│   │   ├── tool_definitions.py
│   │   ├── tool_executor.py
│   │   └── validators.py
│   ├── api/
│   │   ├── main.py
│   │   └── mock_data.py
│   ├── core/
│   │   ├── config.py
│   │   ├── llm.py
│   │   └── retry.py
│   └── tools/
│       └── erp_tools.py
└── tests/
    ├── test_agent.py
    ├── test_approval.py
    ├── test_retry.py
    ├── test_tool_executor.py
    └── test_validators.py
```

## Technologies Used

- Python 3.12
- Groq API
- FastAPI
- Streamlit
- Pydantic
- HTTPX
- Pytest

## Installation

Clone the repository and navigate to the TASK3 directory.

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the TASK3 directory:

```env
GROQ_API_KEY=your_groq_api_key
```

Never commit your actual API key.

## Running the Application

### 1. Start the FastAPI ERP/CRM backend

```bash
python -m uvicorn src.api.main:app --reload --port 8001
```

API documentation:

http://127.0.0.1:8001/docs

### 2. Start the Streamlit interface

Open another terminal in the TASK3 directory:

```bash
streamlit run app.py
```

## Human Approval Workflow

Read operations execute directly.

Write operations require explicit human approval.

Example:

1. User requests a CRM lead update.
2. Agent selects the update_lead tool.
3. The executor validates the arguments.
4. The system generates a unique approval ID.
5. The user reviews the operation.
6. The user approves or rejects it.
7. The operation executes only after approval.

## Testing

Run the complete automated test suite:

```bash
python -m pytest -v
```

Latest verified result: 23 tests passed.

## Execution Logging

The application records:

- USER: Incoming request.
- AGENT: Selected tool.
- ACTION: Tool execution.
- OBSERVATION: Tool result.
- APPROVAL: Approval or rejection.
- FINAL: Final agent response.

These are execution events, not hidden model reasoning.

## Current Limitations

- The ERP/CRM backend uses mock in-memory data.
- Inventory, leads, and tickets reset when the API server restarts.
- Pending approvals are stored in application memory.
- This project is a prototype and is not connected to a production ERP/CRM system.

## Future Improvements

- Persistent database integration.
- Authentication and role-based access control.
- Persistent approval records.
- Production ERP/CRM integrations.
- Improved monitoring and audit logging.
