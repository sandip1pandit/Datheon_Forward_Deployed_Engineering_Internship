from __future__ import annotations

import csv
from pathlib import Path

from pypdf import PdfReader

from src.models import ExtractedDocument

SUPPORTED_EXTENSIONS = {".pdf", ".csv", ".md", ".markdown"}


def extract_file(path: str | Path) -> ExtractedDocument:
    file_path = Path(path)
    suffix = file_path.suffix.lower()

    if suffix == ".pdf":
        return extract_pdf(file_path)
    if suffix == ".csv":
        return extract_csv(file_path)
    if suffix in {".md", ".markdown"}:
        return extract_markdown(file_path)

    raise ValueError(f"Unsupported file type: {suffix}")


def extract_pdf(path: Path) -> ExtractedDocument:
    reader = PdfReader(str(path))
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        pages.append(f"[page {index}]\n{page_text}".strip())

    return ExtractedDocument(
        source_path=str(path),
        file_type="pdf",
        text="\n\n".join(pages).strip(),
        metadata={"page_count": len(reader.pages)},
    )


def extract_csv(path: Path) -> ExtractedDocument:
    rows: list[str] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames or []
        for index, row in enumerate(reader, start=1):
            cells = [f"{key}: {value}" for key, value in row.items() if value]
            rows.append(f"row {index} | " + " | ".join(cells))

    return ExtractedDocument(
        source_path=str(path),
        file_type="csv",
        text="\n".join(rows).strip(),
        metadata={"column_count": len(fieldnames), "row_count": len(rows)},
    )


def extract_markdown(path: Path) -> ExtractedDocument:
    text = path.read_text(encoding="utf-8")
    return ExtractedDocument(
        source_path=str(path),
        file_type="markdown",
        text=text.strip(),
        metadata={"character_count": len(text)},
    )


def iter_raw_files(raw_dir: str | Path) -> list[Path]:
    root = Path(raw_dir)
    files = [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return sorted(files)
