from functools import lru_cache

from sentence_transformers import CrossEncoder


RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


@lru_cache(maxsize=1)
def get_reranker() -> CrossEncoder:
    """Load the cross-encoder once and reuse it."""
    return CrossEncoder(RERANKER_MODEL)


def rerank_documents(
    query: str,
    documents: list[dict],
    top_k: int = 5
) -> list[dict]:
    """
    Rank retrieved documents using query-document relevance.

    Each document must contain a 'text' field.
    Returns documents sorted by descending relevance score.
    """

    if not query or not query.strip() or not documents:
        return []

    if top_k < 1:
        raise ValueError("top_k must be at least 1")

    if any(not isinstance(doc.get("text"), str) for doc in documents):
        raise ValueError("Every document must contain a text string")

    reranker = get_reranker()

    pairs = [
        (query, document["text"])
        for document in documents
    ]

    scores = reranker.predict(pairs)

    ranked_documents = []

    for document, score in zip(documents, scores):
        ranked_document = document.copy()
        ranked_document["rerank_score"] = float(score)
        ranked_documents.append(ranked_document)

    ranked_documents.sort(
        key=lambda item: item["rerank_score"],
        reverse=True
    )

    return ranked_documents[:top_k]
