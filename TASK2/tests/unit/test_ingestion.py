import pytest

from src.ingestion import split_text, extract_pdf_pages


def test_split_text_returns_chunks():
    text = "A" * 2500

    chunks = split_text(text)

    assert len(chunks) == 3
    assert all(len(chunk) <= 1000 for chunk in chunks)


def test_split_text_preserves_content():
    text = "This is a sample document."

    chunks = split_text(text)

    assert len(chunks) == 1
    assert chunks[0] == text


def test_split_text_handles_empty_text():
    assert split_text("") == []
    assert split_text("   ") == []


def test_split_text_uses_overlap():
    text = "A" * 1500

    chunks = split_text(text)

    assert chunks[0][-200:] == chunks[1][:200]


def test_extract_pdf_rejects_missing_file():
    with pytest.raises(FileNotFoundError):
        extract_pdf_pages("missing_document.pdf")


def test_extract_pdf_rejects_non_pdf_file(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("Sample text")

    with pytest.raises(ValueError):
        extract_pdf_pages(str(file_path))
