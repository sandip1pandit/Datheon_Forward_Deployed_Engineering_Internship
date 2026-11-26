import httpx

from src.core.retry import retry_read_operation

API_BASE_URL = "http://127.0.0.1:8001"


def get_inventory():
    """Retrieve all available inventory products."""

    def operation():
        response = httpx.get(
            f"{API_BASE_URL}/inventory",
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    return retry_read_operation(operation)


def get_product(product_id: str):
    """Retrieve details of a specific product."""

    def operation():
        response = httpx.get(
            f"{API_BASE_URL}/inventory/{product_id}",
            timeout=10
        )
        response.raise_for_status()
        return response.json()

    return retry_read_operation(operation)


def update_lead(lead_id: int, status: str):
    """Update the status of a CRM lead."""

    response = httpx.patch(
        f"{API_BASE_URL}/leads/{lead_id}",
        json={"status": status},
        timeout=10
    )
    response.raise_for_status()
    return response.json()


def create_ticket(
    customer_name: str,
    issue: str,
    priority: str = "medium"
):
    """Create a new customer support ticket."""

    response = httpx.post(
        f"{API_BASE_URL}/tickets",
        json={
            "customer_name": customer_name,
            "issue": issue,
            "priority": priority
        },
        timeout=10
    )
    response.raise_for_status()
    return response.json()