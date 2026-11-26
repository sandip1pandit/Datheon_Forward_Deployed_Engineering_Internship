from unittest.mock import MagicMock

from src.models import UserContext, ClearanceLevel
from src import pipeline


def make_user():
    return UserContext(
        user_id="user-1",
        tenant_id="tenant-a",
        department="engineering",
        clearance_level=ClearanceLevel.INTERNAL
    )


def test_empty_query_does_not_search(monkeypatch):
    search_mock = MagicMock()

    monkeypatch.setattr(
        pipeline,
        "search_documents",
        search_mock
    )

    result = pipeline.answer_question("", make_user())

    assert result["retrieved_count"] == 0
    search_mock.assert_not_called()


def test_pipeline_returns_answer(monkeypatch):
    client = MagicMock()

    documents = [
        {
            "text": "MFA is required.",
            "source_path": "security.pdf",
            "page_number": 4
        }
    ]

    monkeypatch.setattr(
        pipeline,
        "rewrite_query",
        lambda query, history: query
    )

    monkeypatch.setattr(
        pipeline,
        "get_vector_client",
        lambda: client
    )

    monkeypatch.setattr(
        pipeline,
        "search_documents",
        lambda **kwargs: documents
    )

    monkeypatch.setattr(
        pipeline,
        "rerank_documents",
        lambda **kwargs: documents
    )

    monkeypatch.setattr(
        pipeline,
        "generate_answer",
        lambda query, documents: {
            "answer": "MFA is required [1].",
            "citations": [
                {
                    "document_number": 1,
                    "source_path": "security.pdf",
                    "page_number": 4
                }
            ]
        }
    )

    result = pipeline.answer_question(
        "What is the security policy?",
        make_user()
    )

    assert result["answer"] == "MFA is required [1]."
    assert result["retrieved_count"] == 1
    assert result["citations"][0]["page_number"] == 4
    client.close.assert_called_once()


def test_pipeline_abstains_when_no_documents(monkeypatch):
    client = MagicMock()

    monkeypatch.setattr(
        pipeline,
        "rewrite_query",
        lambda query, history: query
    )

    monkeypatch.setattr(
        pipeline,
        "get_vector_client",
        lambda: client
    )

    monkeypatch.setattr(
        pipeline,
        "search_documents",
        lambda **kwargs: []
    )

    monkeypatch.setattr(
        pipeline,
        "rerank_documents",
        MagicMock(side_effect=AssertionError(
            "Reranking should not run without documents"
        ))
    )

    monkeypatch.setattr(
        pipeline,
        "generate_answer",
        lambda query, documents: {
            "answer": "Insufficient evidence.",
            "citations": []
        }
    )

    result = pipeline.answer_question(
        "What is the policy?",
        make_user()
    )

    assert result["answer"] == "Insufficient evidence."
    assert result["retrieved_count"] == 0
    assert result["citations"] == []
    client.close.assert_called_once()
