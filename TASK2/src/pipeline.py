from .generation import rewrite_query, generate_answer
from .ingestion import get_vector_client
from .retrieval import search_documents
from .reranking import rerank_documents


def answer_question(
    query: str,
    user,
    chat_history: list[dict] | None = None,
    retrieval_limit: int = 10,
    top_k: int = 5
) -> dict:
    """
    Execute the complete secure RAG pipeline.

    1. Rewrite the question.
    2. Retrieve only documents authorized for the user.
    3. Rerank the authorized documents.
    4. Generate an evidence-grounded answer.
    """

    if not query or not query.strip():
        return {
            "query": query,
            "rewritten_query": "",
            "answer": "Please enter a question.",
            "citations": [],
            "retrieved_count": 0
        }

    rewritten_query = rewrite_query(query, chat_history)

    client = get_vector_client()

    try:
        # Security filtering happens inside Qdrant before reranking.
        documents = search_documents(
            query=rewritten_query,
            user=user,
            limit=retrieval_limit,
            client=client
        )
    finally:
        client.close()

    # Never send an empty or unauthorized result set to the reranker.
    if not documents:
        result = generate_answer(rewritten_query, [])
        return {
            "query": query,
            "rewritten_query": rewritten_query,
            "answer": result["answer"],
            "citations": [],
            "retrieved_count": 0
        }

    ranked_documents = rerank_documents(
        query=rewritten_query,
        documents=documents,
        top_k=top_k
    )

    result = generate_answer(
        query=rewritten_query,
        documents=ranked_documents
    )

    return {
        "query": query,
        "rewritten_query": rewritten_query,
        "answer": result["answer"],
        "citations": result["citations"],
        "retrieved_count": len(ranked_documents)
    }
