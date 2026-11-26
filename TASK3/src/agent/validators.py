from pydantic import BaseModel, Field
from typing import Literal


class GetProductArgs(BaseModel):
    product_id: str = Field(min_length=1)


class UpdateLeadArgs(BaseModel):
    lead_id: int = Field(gt=0)
    status: Literal["new", "contacted", "qualified", "lost"]


class CreateTicketArgs(BaseModel):
    customer_name: str = Field(min_length=2, max_length=100)
    issue: str = Field(min_length=5, max_length=500)
    priority: Literal["low", "medium", "high"] = "medium"