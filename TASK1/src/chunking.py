
from __future__ import annotations

import os
import re

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.models import Chunk, ExtractedDocument


def chunk_document(
    document: ExtractedDocument,
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> list[Chunk]:

    # Read configuration from arguments or environment variables.
    size = (
        chunk_size
        if chunk_size is not None
        else int(os.getenv("CHUNK_SIZE", "800"))
    )

    overlap = (
        chunk_overlap
        if chunk_overlap is not None
        else int(os.getenv("CHUNK_OVERLAP", "120"))
    )

    # Validate chunk configuration.
    if size <= 0:
        raise ValueError("CHUNK_SIZE must be greater than zero")

    if overlap < 0:
        raise ValueError("CHUNK_OVERLAP cannot be negative")

    if overlap >= size:
        raise ValueError(
            "CHUNK_OVERLAP must be smaller than CHUNK_SIZE"
        )

    # Split document text recursively.
    pieces = _split_text(
        document.text,
        chunk_size=size,
        chunk_overlap=overlap,
    )

    chunks: list[Chunk] = []

    # Convert each text piece into a Chunk object.
    for index, text in enumerate(pieces):
        chunks.append(
            Chunk(
                chunk_id=f"{PathSafe(document.source_path)}-{index}",
                source_path=document.source_path,
                file_type=document.file_type,
                text=text,
                chunk_index=index,
                metadata={
                    **document.metadata,
                    "chunk_index": index,
                },
            )
        )

    return chunks


def _split_text(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:

    # Normalize excessive blank lines.
    cleaned = re.sub(r"\n{3,}", "\n\n", text).strip()

    if not cleaned:
        return []

    # Configure recursive splitting.
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=[
            "\n\n",
            "\n",
            ". ",
            "? ",
            "! ",
            " ",
            "",
        ],
    )

    return splitter.split_text(cleaned)


class PathSafe(str):

    def __new__(cls, value: str) -> "PathSafe":

        safe = re.sub(
            r"[^a-zA-Z0-9]+",
            "-",
            value,
        ).strip("-").lower()

        return str.__new__(cls, safe or "document")
