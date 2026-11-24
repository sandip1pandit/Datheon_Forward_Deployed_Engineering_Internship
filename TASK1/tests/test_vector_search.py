
from src.embeddings import embed_query
from src.vector_store import search_chunks


def test_search_chunks():

    query = "Which plant still uses the legacy invoice system?"

    # Convert the question into an embedding
    query_vector = embed_query(query)

    # Search the Qdrant collection
    results = search_chunks(
        query_vector=query_vector,
        limit=5
    )

    print("\nSearch query:", query)
    print("Number of results:", len(results))

    for index, result in enumerate(results, start=1):

        print(f"\nResult {index}")
        print("Chunk ID:", result.get("chunk_id"))
        print("Score:", result.get("score"))
        print("Source:", result.get("source_path"))
        print("Text:", result.get("text"))

    assert len(results) > 0

    assert results[0].get("text") is not None
    assert results[0].get("score") is not None

    print("\nSemantic search test passed!")
