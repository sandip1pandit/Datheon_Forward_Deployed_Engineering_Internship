
from __future__ import annotations

import os

from sentence_transformers import SentenceTransformer

from src.models import Chunk

_model: SentenceTransformer | None = None


def get_embedding_model() -> SentenceTransformer:
    global _model

    if _model is None:
        model_name = os.getenv(
            "EMBEDDING_MODEL",
            "sentence-transformers/all-MiniLM-L6-v2"
        )

        _model = SentenceTransformer(model_name)

    return _model



def embed_chunks(
    chunks: list[Chunk],
    batch_size: int = 32,
) -> list[list[float]]:

    if not chunks:
        return []

    if batch_size <= 0:
        raise ValueError("batch_size must be greater than zero")

    model = get_embedding_model()

    vectors = model.encode(
        [chunk.text for chunk in chunks],
        batch_size=batch_size,
        convert_to_numpy=True,
        show_progress_bar=False,
    )

    return [vector.tolist() for vector in vectors]



def embed_query(query: str) -> list[float]:

    if not query.strip():
        raise ValueError("Query cannot be empty")

    model = get_embedding_model()

    vector = model.encode(
        query,
        convert_to_numpy=True
    )

    return vector.tolist()
