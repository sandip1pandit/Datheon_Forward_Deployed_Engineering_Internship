
import pytest

from src.models import (
    UserContext,
    DocumentMetadata,
    ClearanceLevel,
)
from src.security import (
    can_access_document,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)


@pytest.fixture
def employee():
    return UserContext(
        user_id="emp001",
        tenant_id="company_A",
        department="engineering",
        clearance_level=ClearanceLevel.CONFIDENTIAL,
        roles=["employee"],
    )


@pytest.fixture
def document():
    return DocumentMetadata(
        document_id="doc001",
        tenant_id="company_A",
        department="engineering",
        access_level=ClearanceLevel.INTERNAL,
        source_path="engineering/report.pdf",
        page_number=5,
    )


def test_authorized_employee_can_access_document(employee, document):
    assert can_access_document(employee, document) is True


def test_employee_cannot_access_another_tenant(employee, document):
    document.tenant_id = "company_B"

    assert can_access_document(employee, document) is False


def test_employee_cannot_access_higher_clearance_document(
    employee, document
):
    document.access_level = ClearanceLevel.SECRET

    assert can_access_document(employee, document) is False


def test_employee_cannot_access_another_department(employee, document):
    document.department = "HR"

    assert can_access_document(employee, document) is False


def test_tenant_admin_can_access_other_department(employee, document):
    employee.roles = ["tenant_admin"]
    document.department = "HR"

    assert can_access_document(employee, document) is True


def test_tenant_admin_cannot_access_another_tenant(employee, document):
    employee.roles = ["tenant_admin"]
    document.tenant_id = "company_B"

    assert can_access_document(employee, document) is False


def test_password_hashing():
    password = "SecurePassword123"

    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_jwt_token_creation_and_decoding(employee, monkeypatch):
    monkeypatch.setenv(
        "JWT_SECRET_KEY",
        "test-secret-key-for-testing-32-bytes-minimum"
    )

    token = create_access_token(employee)
    decoded_user = decode_access_token(token)

    assert decoded_user.user_id == employee.user_id
    assert decoded_user.tenant_id == employee.tenant_id
    assert decoded_user.department == employee.department
    assert decoded_user.clearance_level == employee.clearance_level
