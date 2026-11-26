from src.generation.answer_generator import (
    ABSTENTION_MESSAGE,
    generate_answer,
    verify_citations
)


def sample_documents():
    return [
        {
            "text": "Employees must use multi-factor authentication.",
            "source_path": "security.pdf",
            "page_number": 4
        }
    ]


def test_empty_documents_cause_abstention():
    result = generate_answer("What is the security policy?", [])

    assert result["answer"] == ABSTENTION_MESSAGE
    assert result["citations"] == []


def test_missing_api_key_causes_abstention(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    result = generate_answer(
        "What is the security policy?",
        sample_documents()
    )

    assert result["answer"] == ABSTENTION_MESSAGE


def test_valid_citation():
    assert verify_citations(
        "Employees must use MFA [1].",
        sample_documents()
    )


def test_invalid_citation():
    assert not verify_citations(
        "Employees must use MFA [2].",
        sample_documents()
    )


def test_missing_citation():
    assert not verify_citations(
        "Employees must use MFA.",
        sample_documents()
    )
