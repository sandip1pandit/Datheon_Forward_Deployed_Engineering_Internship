
from src.embeddings import embed_query


def test_embed_query():

    query = "Which plant still uses the legacy invoice system?"

    vector = embed_query(query)

    print("\nVector dimensions:", len(vector))
    print("First five values:", vector[:5])

    assert len(vector) == 384
    assert all(isinstance(value, float) for value in vector)
    assert all(value == value for value in vector)

    print("\nQuery embedding test passed!")
