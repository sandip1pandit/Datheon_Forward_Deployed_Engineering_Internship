from src.generation.query_rewriter import rewrite_query


def test_empty_query():
    assert rewrite_query("") == ""


def test_query_fallback_without_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    result = rewrite_query("  What about security?  ")

    assert result == "What about security?"


def test_query_fallback_when_groq_fails(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")

    class FakeGroq:
        def __init__(self, api_key):
            pass

        @property
        def chat(self):
            raise RuntimeError("Groq unavailable")

    monkeypatch.setattr(
        "src.generation.query_rewriter.Groq",
        FakeGroq
    )

    result = rewrite_query("Explain document security")

    assert result == "Explain document security"
