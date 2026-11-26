from pathlib import Path
from uuid import uuid4

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient, models

from ..models import ClearanceLevel


# Project paths
TASK_ROOT = Path(__file__).resolve().parents[2]
QDRANT_PATH = TASK_ROOT / "data" / "qdrant"

# Models and configuration
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
COLLECTION_NAME = "enterprise_documents"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def split_text(text: str) -> list[str]:
    """Split text into overlapping chunks."""

    text = " ".join(text.split())

    if not text:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + CHUNK_SIZE
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - CHUNK_OVERLAP

    return chunks


def extract_pdf_pages(pdf_path: str) -> list[dict]:
    """Extract text while preserving original page numbers."""

    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported")

    reader = PdfReader(str(path))
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            pages.append({
                "page_number": page_number,
                "text": text
            })

    return pages


def get_embedding_model():
    """Load the embedding model."""

    return SentenceTransformer(EMBEDDING_MODEL)


def get_vector_client():
    """Create a persistent local Qdrant client."""

    QDRANT_PATH.mkdir(parents=True, exist_ok=True)
    return QdrantClient(path=str(QDRANT_PATH))


def ensure_collection(client, vector_size: int):
    """Create the collection if it does not already exist."""

    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=vector_size,
                distance=models.Distance.COSINE
            )
        )


def ingest_pdf(
    pdf_path: str,
    tenant_id: str,
    department: str,
    access_level: ClearanceLevel,
) -> dict:
    """
    Extract, chunk, embed and store a PDF in Qdrant.

    Each chunk stores its tenant, department, clearance
    and original page number.
    """

    if not tenant_id.strip():
        raise ValueError("tenant_id cannot be empty")

    if not department.strip():
        raise ValueError("department cannot be empty")

    pages = extract_pdf_pages(pdf_path)

    if not pages:
        raise ValueError("No extractable text found in the PDF")

    document_id = str(uuid4())
    source_path = str(Path(pdf_path).resolve())

    chunks = []

    for page in pages:
        page_chunks = split_text(page["text"])

        for chunk_index, chunk_text in enumerate(page_chunks):
            chunks.append({
                "text": chunk_text,
                "page_number": page["page_number"],
                "chunk_index": chunk_index
            })

    if not chunks:
        raise ValueError("No chunks were generated")

    model = get_embedding_model()

    embeddings = model.encode(
        [chunk["text"] for chunk in chunks],
        normalize_embeddings=True,
        show_progress_bar=True
    )

    vector_size = model.get_sentence_embedding_dimension()

    client = get_vector_client()

    try:
        ensure_collection(client, vector_size)

        points = []

        for chunk, embedding in zip(chunks, embeddings):
            points.append(
                models.PointStruct(
                    id=str(uuid4()),
                    vector=embedding.tolist(),
                    payload={
                        "document_id": document_id,
                        "tenant_id": tenant_id,
                        "department": department,
                        "access_level": int(access_level),
                        "source_path": source_path,
                        "page_number": chunk["page_number"],
                        "chunk_index": chunk["chunk_index"],
                        "text": chunk["text"]
                    }
                )
            )

        client.upsert(
            collection_name=COLLECTION_NAME,
            points=points,
            wait=True
        )

    finally:
        client.close()

    return {
        "document_id": document_id,
        "source_path": source_path,
        "pages_processed": len(pages),
        "chunks_stored": len(chunks),
        "tenant_id": tenant_id,
        "department": department,
        "access_level": access_level.name
    }
def delete_document(document_id: str):
    client = get_vector_client()

    try:
        if not client.collection_exists(COLLECTION_NAME):
            return

        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(value=document_id)
                        )
                    ]
                )
            ),
            wait=True
        )
    finally:
        client.close()