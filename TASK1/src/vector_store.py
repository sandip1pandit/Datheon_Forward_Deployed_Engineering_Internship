
from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
    Filter,
    FieldCondition,
    MatchValue,
)
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

from src.models import Chunk


VECTOR_SIZE = 384


def get_collection(
    persist_dir: str | None = None,
    collection_name: str | None = None,
) -> QdrantClient:

    directory = persist_dir or os.getenv(
        "QDRANT_DIR",
        "data/vector_db"
    )

    name = collection_name or os.getenv(
        "COLLECTION_NAME",
        "legacy_documents"
    )

    Path(directory).mkdir(
        parents=True,
        exist_ok=True
    )

    client = QdrantClient(path=directory)

    if not client.collection_exists(name):
        client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )

    return client


def upsert_chunks(
    chunks: list[Chunk],
    embeddings: list[list[float]],
    persist_dir: str | None = None,
    collection_name: str | None = None,
) -> int:

    if not chunks:
        return 0

    if len(chunks) != len(embeddings):
        raise ValueError(
            "Each chunk must have a matching embedding"
        )

    name = collection_name or os.getenv(
        "COLLECTION_NAME",
        "legacy_documents"
    )

    client = get_collection(
        persist_dir,
        name
    )

    try:
        points = []

        for chunk, embedding in zip(chunks, embeddings):

            if len(embedding) != VECTOR_SIZE:
                raise ValueError(
                    f"Embedding must contain {VECTOR_SIZE} dimensions"
                )

            point_id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    chunk.chunk_id
                )
            )

            payload = {
                **chunk.metadata,
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "source_path": chunk.source_path,
                "file_type": chunk.file_type,
                "chunk_index": chunk.chunk_index,
            }

            points.append(
                PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=payload,
                )
            )

        client.upsert(
            collection_name=name,
            points=points,
        )

        return len(points)

    finally:
        client.close()



def search_chunks(
    query_vector: list[float],
    limit: int = 5,
    persist_dir: str | None = None,
    collection_name: str | None = None,
    client_id: str | None = None,
    department: str | None = None,
    access_tier: str | None = None,
    file_type: str | None = None,
) -> list[dict[str, Any]]:

    if len(query_vector) != VECTOR_SIZE:
        raise ValueError(
            f"Query vector must contain {VECTOR_SIZE} dimensions"
        )

    if limit <= 0:
        raise ValueError(
            "Search limit must be greater than zero"
        )

    name = collection_name or os.getenv(
        "COLLECTION_NAME",
        "legacy_documents"
    )

    # Build metadata filtering conditions
    conditions = []

    if client_id is not None:
        conditions.append(
            FieldCondition(
                key="client_id",
                match=MatchValue(value=client_id)
            )
        )

    if department is not None:
        conditions.append(
            FieldCondition(
                key="department",
                match=MatchValue(value=department)
            )
        )

    if access_tier is not None:
        conditions.append(
            FieldCondition(
                key="access_tier",
                match=MatchValue(value=access_tier)
            )
        )

    if file_type is not None:
        conditions.append(
            FieldCondition(
                key="file_type",
                match=MatchValue(value=file_type)
            )
        )

    # Create a Qdrant filter only when conditions exist
    query_filter = Filter(must=conditions) if conditions else None

    client = get_collection(
        persist_dir,
        name
    )

    try:
        response = client.query_points(
            collection_name=name,
            query=query_vector,
            query_filter=query_filter,
            limit=limit,
            with_payload=True,
            with_vectors=False,
        )

        results = []

        for point in response.points:

            result = {
                "id": point.id,
                "score": point.score,
                **(point.payload or {}),
            }

            results.append(result)

        return results

    finally:
        client.close()