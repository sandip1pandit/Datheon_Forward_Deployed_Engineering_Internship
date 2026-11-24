
from pathlib import Path

from src.models import (
    AccessTier,
    ExtractedDocument,
    IngestionStatus,
)


def enrich_metadata(
    document: ExtractedDocument,
    *,
    client_id: str | None = None,
    department: str | None = None,
    access_tier: AccessTier | None = None,
    ingestion_status: IngestionStatus | None = None,
) -> ExtractedDocument:

    path = Path(document.source_path)

    # Update enterprise fields only when supplied.
    if client_id is not None:
        document.client_id = client_id

    if department is not None:
        document.department = department

    if access_tier is not None:
        document.access_tier = access_tier

    if ingestion_status is not None:
        document.ingestion_status = ingestion_status

    # Preserve existing document metadata.
    document.metadata.update({
        "filename": path.name,
        "parent_dir": path.parent.name,
        "suffix": path.suffix.lower(),
        "file_type": document.file_type,
        "source_path": str(path),
    })

    # Add enterprise metadata to the metadata dictionary.
    document.metadata.update({
        "client_id": document.client_id,
        "department": document.department,
        "access_tier": document.access_tier,
        "ingestion_status": document.ingestion_status,
    })

    return document
