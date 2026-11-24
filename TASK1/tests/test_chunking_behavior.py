from datetime import date

from src.metadata import enrich_metadata
from src.models import ExtractedDocument
from src.chunking import chunk_document


def test_chunking_behavior():

    text = (
        "Artificial intelligence is transforming industries. "
        "Machine learning helps computers learn from data. "
        "Vector databases store numerical representations."
    )

    document = ExtractedDocument(
        source_path="sample.md",
        file_type="markdown",
        text=text
    )

    chunks = chunk_document(
        document,
        chunk_size=60,
        chunk_overlap=15
    )

    for chunk in chunks:
        print("\nChunk:", chunk.chunk_index)
        print("Text:", chunk.text)
        print("Length:", len(chunk.text))

    print("\nTotal chunks:", len(chunks))

def test_metadata_propagation_to_chunks():

    document = ExtractedDocument(
        source_path="sample.csv",
        file_type="csv",
        text=(
            "Artificial intelligence processes data. "
            "Machine learning identifies patterns. "
            "Vector databases store embeddings."
        )
    )

    document = enrich_metadata(
        document,
        client_id="client_001",
        department="operations",
        access_tier="internal",
        document_date=date(2026, 11, 20),
    )

    chunks = chunk_document(document)

    assert len(chunks) > 0

    for chunk in chunks:
        assert chunk.metadata["client_id"] == "client_001"
        assert chunk.metadata["department"] == "operations"
        assert chunk.metadata["access_tier"] == "internal"
        assert chunk.metadata["date"] == "2026-11-20"
        assert chunk.metadata["ingestion_status"] == "pending"
        assert chunk.metadata["extracted_at"] == (
            document.extracted_at.isoformat()
        )

def demonstrate_word_splitting():

    text = "I love learning Python programming"

    words = text.split()

    chunk_size = 3
    overlap = 1

    start = 0

    while start < len(words):

        end = min(start + chunk_size, len(words))

        chunk = " ".join(words[start:end])

        print("Chunk:", chunk)

        if end == len(words):
            break

        start = end - overlap


if __name__ == "__main__":
    demonstrate_word_splitting()