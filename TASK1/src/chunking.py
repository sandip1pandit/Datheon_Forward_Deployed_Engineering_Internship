
from __future__ import annotations

import math
import os
import re

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.embeddings import get_embedding_model
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

    # Semantic similarity threshold.
    similarity_threshold = float(
        os.getenv("SEMANTIC_SIMILARITY_THRESHOLD", "0.50")
    )

    # Validate configuration.
    if size <= 0:
        raise ValueError("CHUNK_SIZE must be greater than zero")

    if overlap < 0:
        raise ValueError("CHUNK_OVERLAP cannot be negative")

    if overlap >= size:
        raise ValueError(
            "CHUNK_OVERLAP must be smaller than CHUNK_SIZE"
        )

    if not -1.0 <= similarity_threshold <= 1.0:
        raise ValueError(
            "SEMANTIC_SIMILARITY_THRESHOLD must be between -1 and 1"
        )

    # Clean document text.
    cleaned = re.sub(r"\n{3,}", "\n\n", document.text).strip()

    if not cleaned:
        return []

    # Perform semantic chunking.
    semantic_groups = _semantic_split(
        cleaned,
        chunk_size=size,
        chunk_overlap=overlap,
        similarity_threshold=similarity_threshold,
    )

    chunks: list[Chunk] = []

    # Convert text groups into Chunk objects.
    for index, text in enumerate(semantic_groups):
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


def _semantic_split(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
    similarity_threshold: float,
) -> list[str]:

    # Split document into sentences.
    sentences = _split_into_sentences(text)

    if not sentences:
        return []

    # A single sentence cannot be compared semantically.
    if len(sentences) == 1:
        return _recursive_split(
            sentences[0],
            chunk_size,
            chunk_overlap,
        )

    # Generate sentence embeddings using the existing model.
    model = get_embedding_model()

    embeddings = model.encode(
        sentences,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    # Group semantically related sentences.
    semantic_groups: list[str] = []
    current_group = [sentences[0]]

    for index in range(1, len(sentences)):

        previous_embedding = embeddings[index - 1]
        current_embedding = embeddings[index]

        similarity = _cosine_similarity(
            previous_embedding,
            current_embedding,
        )

        current_text = " ".join(current_group)
        candidate_text = current_text + " " + sentences[index]

        # Start a new group if meaning changes or size is exceeded.
        if (
            similarity < similarity_threshold
            or len(candidate_text) > chunk_size
        ):
            semantic_groups.append(current_text.strip())
            current_group = [sentences[index]]
        else:
            current_group.append(sentences[index])

    # Add the final group.
    if current_group:
        semantic_groups.append(" ".join(current_group).strip())

    # Enforce chunk size and overlap using recursive splitting.
    final_chunks: list[str] = []

    for group in semantic_groups:
        final_chunks.extend(
            _recursive_split(
                group,
                chunk_size,
                chunk_overlap,
            )
        )

    return [chunk for chunk in final_chunks if chunk.strip()]


def _split_into_sentences(text: str) -> list[str]:

    # Split on sentence endings and paragraph boundaries.
    sentences = re.split(
        r"(?<=[.!?])\s+|\n{2,}",
        text,
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


def _cosine_similarity(
    vector_a,
    vector_b,
) -> float:

    # Calculate cosine similarity between two embeddings.
    dot_product = sum(
        float(a) * float(b)
        for a, b in zip(vector_a, vector_b)
    )

    norm_a = math.sqrt(
        sum(float(value) ** 2 for value in vector_a)
    )

    norm_b = math.sqrt(
        sum(float(value) ** 2 for value in vector_b)
    )

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)


def _recursive_split(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[str]:

    # Fallback for oversized semantic groups.
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

    return splitter.split_text(text.strip())


class PathSafe(str):

    def __new__(cls, value: str) -> "PathSafe":

        safe = re.sub(
            r"[^a-zA-Z0-9]+",
            "-",
            value,
        ).strip("-").lower()

        return str.__new__(
            cls,
            safe or "document",
        )
