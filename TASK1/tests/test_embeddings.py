from src.models import Chunk
from src.embeddings import embed_chunks


def test_embed_chunks():

    chunks = [
        Chunk(
            chunk_id="sample-0",
            source_path="sample.md",
            file_type="markdown",
            text="Legacy invoice system still in use",
            chunk_index=0
        ),
        Chunk(
            chunk_id="sample-1",
            source_path="sample.md",
            file_type="markdown",
            text="Daily plant records stored in PDF files",
            chunk_index=1
        )
    ]

    vectors = embed_chunks(chunks)

    print("\nNumber of vectors:", len(vectors))
    print("First vector dimensions:", len(vectors[0]))
    print("Second vector dimensions:", len(vectors[1]))

    assert len(vectors) == 2
    assert len(vectors[0]) == 384
    assert len(vectors[1]) == 384

    print("\nEmbedding function test passed!")