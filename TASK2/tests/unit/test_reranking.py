from unittest.mock import MagicMock

import pytest

from src.reranking.cross_encoder import rerank_documents


def test_rerank_documents_sorts_by_relevance(monkeypatch):
    documents = [
        {"text": "Python is a programming language.", "source_path": "a.pdf"},
        {"text": "The weather is sunny today.", "source_path": "b.pdf"},
        {"text": "Python supports machine learning.", "source_path": "c.pdf"}
    ]

    mock_model = MagicMock()
    mock_model.predict.return_value = [0.4, 0.1, 0.9]

    monkeypatch.setattr(
        "src.reranking.cross_encoder.get_reranker",
        lambda: mock_model
    )

    results = rerank_documents(
        "Python machine learning",
        documents,
        top_k=2
    )

    assert len(results) == 2
    assert results[0]["source_path"] == "c.pdf"
    assert results[1]["source_path"] == "a.pdf"
    assert results[0]["rerank_score"] == 0.9


def test_rerank_empty_documents():
    assert rerank_documents("Python", []) == []


def test_rerank_empty_query():
    assert rerank_documents("", [{"text": "Python"}]) == []


def test_rerank_rejects_invalid_document():
    with pytest.raises(ValueError):
        rerank_documents("Python", [{"content": "Missing text field"}])


def test_rerank_rejects_invalid_top_k():
    with pytest.raises(ValueError):
        rerank_documents("Python", [{"text": "Python"}], top_k=0)
