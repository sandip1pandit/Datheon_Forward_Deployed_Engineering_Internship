from qdrant_client import QdrantClient, models

from ..models import UserContext, DocumentMetadata
from ..security import can_access_document
from ..ingestion import COLLECTION_NAME, get_vector_client


def build_access_filter(user: UserContext) -> models.Filter:
    """Build Qdrant filters using trusted authenticated user information."""

    conditions = [
        models.FieldCondition(
            key="tenant_id",
            match=models.MatchValue(value=user.tenant_id)
        ),
        models.FieldCondition(
            key="access_level",
            range=models.Range(lte=int(user.clearance_level))
        )
    ]

    # Tenant admins can access every department in their own tenant.
    if "tenant_admin" not in user.roles:
        conditions.append(
            models.FieldCondition(
                key="department",
                match=models.MatchValue(value=user.department)
            )
        )

    return models.Filter(must=conditions)


def search_documents(
    query: str,
    user: UserContext,
    limit: int = 10,
    client: QdrantClient | None = None
) -> list[dict]:
    """
    Search documents accessible to the authenticated user.

    Security filters are applied inside Qdrant before results are returned.
    A second permission check protects against incorrectly stored metadata.
    """

    if not query or not query.strip():
        return []

    if limit < 1:
        raise ValueError("limit must be at least 1")

    if client is None:
        client = get_vector_client()

    from ..ingestion import get_embedding_model

    embedding_model = get_embedding_model()
    query_vector = embedding_model.encode(query).tolist()

    access_filter = build_access_filter(user)
    # Check whether the collection exists
    if not client.collection_exists(COLLECTION_NAME):
        return []

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        query_filter=access_filter,
        limit=limit,
        with_payload=True
    ).points

    authorized_results = []

    for point in results:
        payload = point.payload or {}

        try:
            document = DocumentMetadata(
                document_id=payload["document_id"],
                tenant_id=payload["tenant_id"],
                department=payload["department"],
                access_level=payload["access_level"],
                source_path=payload["source_path"],
                page_number=payload.get("page_number")
            )
        except (KeyError, ValueError, TypeError):
            # Reject records with incomplete or invalid security metadata.
            continue

        if not can_access_document(user, document):
            continue

        authorized_results.append({
            "document_id": document.document_id,
            "text": payload.get("text", ""),
            "source_path": document.source_path,
            "page_number": document.page_number,
            "department": document.department,
            "access_level": int(document.access_level),
            "score": point.score
        })

    return authorized_results
