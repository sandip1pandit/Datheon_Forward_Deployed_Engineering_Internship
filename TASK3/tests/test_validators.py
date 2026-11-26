import pytest
from pydantic import ValidationError

from src.agent.validators import (
    GetProductArgs,
    UpdateLeadArgs,
    CreateTicketArgs,
)


def test_valid_product_arguments():
    result = GetProductArgs(product_id="LAP-101")
    assert result.product_id == "LAP-101"


def test_invalid_product_arguments():
    with pytest.raises(ValidationError):
        GetProductArgs(product_id="")


def test_valid_lead_arguments():
    result = UpdateLeadArgs(
        lead_id=102,
        status="qualified"
    )
    assert result.status == "qualified"


def test_invalid_lead_arguments():
    with pytest.raises(ValidationError):
        UpdateLeadArgs(
            lead_id=-5,
            status="unknown"
        )


def test_valid_ticket_arguments():
    result = CreateTicketArgs(
        customer_name="Rahul Sharma",
        issue="Unable to access account",
        priority="high"
    )
    assert result.priority == "high"


def test_invalid_ticket_arguments():
    with pytest.raises(ValidationError):
        CreateTicketArgs(
            customer_name="R",
            issue="Bug",
            priority="urgent"
        )