
import pytest
from pydantic import ValidationError

from src.models import ExtractedDocument
from src.metadata import enrich_metadata


def test_enterprise_metadata():
    document = ExtractedDocument(
        source_path="data/raw/markdown/engineering.md",
        file_type="markdown",
        text="Engineering documentation"
    )

    result = enrich_metadata(
        document,
        client_id="client_001",
        department="engineering",
        access_tier="confidential",
        ingestion_status="processed"
    )

    assert result.client_id == "client_001"
    assert result.department == "engineering"
    assert result.access_tier == "confidential"
    assert result.ingestion_status == "processed"


def test_metadata_dictionary_is_updated():
    document = ExtractedDocument(
        source_path="data/raw/csv/sample.csv",
        file_type="csv",
        text="Plant information",
        metadata={"row_count": 3}
    )

    result = enrich_metadata(
        document,
        client_id="client_001",
        department="operations",
        access_tier="internal"
    )

    assert result.metadata["row_count"] == 3
    assert result.metadata["filename"] == "sample.csv"
    assert result.metadata["client_id"] == "client_001"
    assert result.metadata["department"] == "operations"


def test_invalid_access_tier():
    document = ExtractedDocument(
        source_path="sample.md",
        file_type="markdown",
        text="Sample"
    )

    with pytest.raises(ValidationError):
        document.access_tier = "secret"


def test_default_ingestion_status():
    document = ExtractedDocument(
        source_path="sample.md",
        file_type="markdown",
        text="Sample"
    )

    assert document.ingestion_status == "pending"
