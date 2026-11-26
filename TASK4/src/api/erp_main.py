
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.api.mock_data import inventory, leads, tickets

app = FastAPI(
    title="Enterprise ERP Backend",
    description="Mock inventory, CRM and support-ticket API",
    version="1.0.0"
)


class LeadUpdate(BaseModel):
    status: str = Field(..., min_length=1)


class TicketCreate(BaseModel):
    customer_name: str = Field(..., min_length=1)
    issue: str = Field(..., min_length=1)
    priority: str = "medium"


@app.get("/")
def root():
    return {
        "service": "Enterprise ERP Backend",
        "status": "running"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/inventory")
def get_inventory():
    return inventory


@app.get("/inventory/{product_id}")
def get_product(product_id: str):
    for product in inventory:
        if product["product_id"] == product_id:
            return product

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )


@app.patch("/leads/{lead_id}")
def update_lead(lead_id: int, request: LeadUpdate):
    for lead in leads:
        if lead["lead_id"] == lead_id:
            lead["status"] = request.status
            return {
                "message": "Lead updated successfully",
                "lead": lead
            }

    raise HTTPException(
        status_code=404,
        detail="Lead not found"
    )


@app.post("/tickets", status_code=201)
def create_ticket(request: TicketCreate):
    ticket = {
        "ticket_id": len(tickets) + 1,
        "customer_name": request.customer_name,
        "issue": request.issue,
        "priority": request.priority,
        "status": "open"
    }

    tickets.append(ticket)

    return {
        "message": "Ticket created successfully",
        "ticket": ticket
    }
