from datetime import date, datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


AccessTier = Literal[
    "public",
    "internal",
    "confidential",
    "restricted"
]

IngestionStatus = Literal[
    "pending",
    "processed",
    "failed"
]


class ExtractedDocument(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    source_path: str
    file_type: str
    text: str

    # Existing flexible metadata
    metadata: dict[str, Any] = Field(default_factory=dict)

    # Enterprise metadata
    client_id: str | None = None
    department: str | None = None
    access_tier: AccessTier | None = None
    document_date: date | None = None
    ingestion_status: IngestionStatus = "pending"

    # Extraction timestamp
    extracted_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class Chunk(BaseModel):
    chunk_id: str
    source_path: str
    file_type: str
    text: str
    chunk_index: int
    metadata: dict[str, Any] = Field(default_factory=dict)
