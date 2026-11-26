from types import SimpleNamespace
from unittest.mock import MagicMock

from src.models import UserContext, ClearanceLevel
from src.retrieval.search import build_access_filter, search_documents


def test_employee_filter_contains_tenant_department_and_clearance():
    user = UserContext(
        user_id="user-1",
        tenant_id="tenant-a",
        department="engineering",
        clearance_level=ClearanceLevel.INTERNAL
    )

    access_filter = build_access_filter(user)

    assert len(access_filter.must) == 3


def test_tenant_admin_filter_does_not_restrict_department():
    user = UserContext(
        user_id="admin-1",
        tenant_id="tenant-a",
        department="engineering",
        clearance_level=ClearanceLevel.SECRET,
        roles=["tenant_admin"]
    )

    access_filter = build_access_filter(user)

    assert len(access_filter.must) == 2


def test_search_returns_only_authorized_documents(monkeypatch):
    user = UserContext(
        user_id="user-1",
        tenant_id="tenant-a",
        department="engineering",
        clearance_level=ClearanceLevel.INTERNAL
    )

    authorized_payload = {
        "document_id": "doc-1",
        "tenant_id": "tenant-a",
        "department": "engineering",
        "access_level": 1,
        "source_path": "engineering.pdf",
        "page_number": 2,
        "text": "Engineering documentation"
    }

    unauthorized_payload = {
        "document_id": "doc-2",
        "tenant_id": "tenant-b",
        "department": "engineering",
        "access_level": 1,
        "source_path": "other.pdf",
        "page_number": 1,
        "text": "Other tenant documentation"
    }

    mock_client = MagicMock()
    mock_client.query_points.return_value.points = [
        SimpleNamespace(payload=authorized_payload, score=0.95),
        SimpleNamespace(payload=unauthorized_payload, score=0.90)
    ]

    mock_embedding_model = MagicMock()
    mock_embedding_model.encode.return_value.tolist.return_value = [0.1, 0.2]

    monkeypatch.setattr(
        "src.ingestion.get_embedding_model",
        lambda: mock_embedding_model
    )

    results = search_documents(
        query="engineering documentation",
        user=user,
        client=mock_client
    )

    assert len(results) == 1
    assert results[0]["document_id"] == "doc-1"
    assert results[0]["text"] == "Engineering documentation"


def test_search_rejects_empty_query():
    user = UserContext(
        user_id="user-1",
        tenant_id="tenant-a",
        department="engineering",
        clearance_level=ClearanceLevel.INTERNAL
    )

    assert search_documents("", user) == []
