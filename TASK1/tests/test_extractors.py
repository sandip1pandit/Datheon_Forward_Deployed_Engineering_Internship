from pathlib import Path
from src.extractors import (
    extract_csv,
    extract_file,
    extract_markdown,
    extract_pdf,
)
from src.chunking import chunk_document
from src.extractors import extract_csv, extract_file, extract_markdown
from src.metadata import enrich_metadata

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "raw" / "csv" / "sample.csv"
MD_PATH = ROOT / "data" / "raw" / "markdown" / "sample.md"


def test_extract_csv_includes_rows():
    document = extract_csv(CSV_PATH)
    assert document.file_type == "csv"
    assert "Acme Corp" in document.text
    assert document.metadata["row_count"] == 3


def test_extract_markdown_keeps_headings():
    document = extract_markdown(MD_PATH)
    assert document.file_type == "markdown"
    assert "Legacy plant notes" in document.text

def test_extract_pdf_includes_page_text_and_count():
    pdf_path = ROOT / "tests" / "fixtures" / "test_sample.pdf"

    document = extract_pdf(pdf_path)

    assert document.file_type == "pdf"
    assert document.metadata["page_count"] == 2
    assert "PDF extraction test page one" in document.text
    assert "PDF extraction test page two" in document.text

def test_extract_file_routes_by_extension():
    document = extract_file(CSV_PATH)
    assert document.source_path.endswith("sample.csv")


def test_enrich_metadata_adds_filename():
    document = enrich_metadata(extract_file(MD_PATH))
    assert document.metadata["filename"] == "sample.md"
    assert document.metadata["parent_dir"] == "markdown"


def test_chunk_document_respects_size():
    document = extract_file(MD_PATH)
    chunks = chunk_document(document, chunk_size=80, chunk_overlap=20)
    assert chunks
    assert all(len(chunk.text) <= 80 for chunk in chunks)
    assert chunks[0].chunk_index == 0
