
import uuid

from src.models import Chunk
from src.vector_store import upsert_chunks, get_collection


def test_upsert_chunks():

    # Step 1: Create sample chunks
    chunks = [
        Chunk(
            chunk_id="test-0",
            source_path="sample.md",
            file_type="markdown",
            text="Legacy invoice system still in use",
            chunk_index=0,
            metadata={
                "client_id": "client_001",
                "department": "engineering",
                "access_tier": "confidential",
            }
        ),
        Chunk(
            chunk_id="test-1",
            source_path="sample.md",
            file_type="markdown",
            text="Daily plant records stored in PDF files",
            chunk_index=1,
            metadata={
                "client_id": "client_001",
                "department": "operations",
                "access_tier": "internal",
            }
        )
    ]

    # Step 2: Create sample embeddings
    embeddings = [
        [0.1] * 384,
        [0.2] * 384
    ]

    # Step 3: Convert readable chunk IDs into deterministic UUIDs
    point_ids = [
        str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk.chunk_id))
        for chunk in chunks
    ]

    # Step 4: Store chunks and embeddings in Qdrant
    stored = upsert_chunks(
        chunks,
        embeddings,
        persist_dir="data/test_vector_db",
        collection_name="test_documents"
    )

    assert stored == 2

    # Step 5: Connect to the test collection
    client = get_collection(
        persist_dir="data/test_vector_db",
        collection_name="test_documents"
    )

    try:
        # Step 6: Retrieve the stored records
        records = client.retrieve(
            collection_name="test_documents",
            ids=point_ids,
            with_payload=True,
            with_vectors=True
        )

        # Step 7: Verify the retrieved records
        assert len(records) == 2

        assert records[0].payload["text"] == (
            "Legacy invoice system still in use"
        )

        assert records[0].payload["client_id"] == "client_001"

        assert records[0].payload["chunk_id"] == "test-0"

        assert len(records[0].vector) == 384

        assert records[1].payload["chunk_id"] == "test-1"

        print("\nStored records:", len(records))
        print("First record text:", records[0].payload["text"])
        print("First record chunk ID:", records[0].payload["chunk_id"])
        print("First Qdrant point ID:", records[0].id)
        print("First vector dimensions:", len(records[0].vector))

    finally:
        client.close()
