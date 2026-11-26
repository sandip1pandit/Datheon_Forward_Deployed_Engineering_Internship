
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Literal
from uuid import uuid4

from src.api.mock_data import inventory, leads, tickets

app = FastAPI(
    title="Enterprise ERP/CRM Mock API",
    description="Mock enterprise API for the Autonomous Field Agent",
    version="1.0.0"
)


# Request schemas

class LeadUpdate(BaseModel):
    status: Literal["new", "contacted", "qualified", "lost"]


class TicketCreate(BaseModel):
    customer_name: str = Field(min_length=2, max_length=100)
    issue: str = Field(min_length=5, max_length=500)
    priority: Literal["low", "medium", "high"] = "medium"


# Health endpoint

@app.get("/")
def home():
    return {"message": "Enterprise ERP/CRM API is running"}


# ERP: Inventory lookup

@app.get("/inventory")
def get_inventory():
    return {"inventory": inventory}


@app.get("/inventory/{product_id}")
def get_product(product_id: str):
    for product in inventory:
        if product["product_id"] == product_id:
            return product

    raise HTTPException(
        status_code=404,
        detail="Product not found"
    )


# CRM: Update lead

@app.patch("/leads/{lead_id}")
def update_lead(lead_id: int, update: LeadUpdate):
    for lead in leads:
        if lead["lead_id"] == lead_id:
            lead["status"] = update.status
            return {
                "message": "Lead updated successfully",
                "lead": lead
            }

    raise HTTPException(
        status_code=404,
        detail="Lead not found"
    )


# Support: Create ticket

@app.post("/tickets", status_code=201)
def create_ticket(ticket: TicketCreate):
    new_ticket = {
        "ticket_id": str(uuid4()),
        "customer_name": ticket.customer_name,
        "issue": ticket.issue,
        "priority": ticket.priority,
        "status": "open"
    }

    tickets.append(new_ticket)

    return {
        "message": "Support ticket created successfully",
        "ticket": new_ticket
    }


@app.get("/tickets")
def get_tickets():
    return {"tickets": tickets}
