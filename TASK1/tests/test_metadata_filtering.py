
from src.models import Chunk
from src.vector_store import upsert_chunks, search_chunks


def test_metadata_filtering():

    # 1. Create three documents belonging to different departments/clients
    chunks = [
        Chunk(
            chunk_id="filter-test-1",
            source_path="invoice_001.csv",
            file_type="csv",
            text="Legacy invoice system used by Acme Corp",
            chunk_index=0,
            metadata={
                "client_id": "client_001",
                "department": "operations",
                "access_tier": "internal",
                "date": "2026-11-20",
            }
        ),
        Chunk(
            chunk_id="filter-test-2",
            source_path="invoice_002.csv",
            file_type="csv",
            text="Invoice records belonging to another client",
            chunk_index=0,
            metadata={
                "client_id": "client_002",
                "department": "operations",
                "access_tier": "internal",
                "date": "2026-11-20",
            }
        ),
        Chunk(
            chunk_id="filter-test-3",
            source_path="finance.md",
            file_type="markdown",
            text="Financial records for Acme Corp",
            chunk_index=0,
            metadata={
                "client_id": "client_001",
                "department": "finance",
                "access_tier": "confidential",
                "date": "2026-11-15",
            }
        ),
    ]

    # 2. Create sample embeddings
    embeddings = [
        [0.1] * 384,
        [0.2] * 384,
        [0.3] * 384,
    ]

    # 3. Store documents in a separate test collection
    stored = upsert_chunks(
        chunks,
        embeddings,
        persist_dir="data/test_filter_vector_db",
        collection_name="filter_test_documents",
    )

    assert stored == 3

    # 4. Create a sample query vector
    query_vector = [0.1] * 384

    # 5. Search using multiple metadata filters
    results = search_chunks(
        query_vector=query_vector,
        limit=5,
        persist_dir="data/test_filter_vector_db",
        collection_name="filter_test_documents",
        client_id="client_001",
        department="operations",
        access_tier="internal",
    )

    # 6. Verify that only the matching document is returned
    assert len(results) == 1

    assert results[0]["chunk_id"] == "filter-test-1"
    assert results[0]["client_id"] == "client_001"
    assert results[0]["department"] == "operations"
    assert results[0]["access_tier"] == "internal"

    print("\nMetadata filtering test passed!")
    print("Matching documents:", len(results))
    print("Retrieved chunk:", results[0]["chunk_id"])
    print("Client:", results[0]["client_id"])
    print("Department:", results[0]["department"])
    print("Access tier:", results[0]["access_tier"])
def test_document_date_filtering():

    query_vector = [0.1] * 384

    results = search_chunks(
        query_vector=query_vector,
        limit=5,
        persist_dir="data/test_filter_vector_db",
        collection_name="filter_test_documents",
        document_date="2026-11-20",
    )

    assert len(results) == 2

    for result in results:
        assert result["date"] == "2026-11-20"

    print("\nDocument date filtering test passed!")
    print("Matching documents:", len(results))