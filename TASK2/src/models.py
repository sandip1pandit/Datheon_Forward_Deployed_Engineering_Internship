from enum import IntEnum
from pydantic import BaseModel, Field


class ClearanceLevel(IntEnum):
    PUBLIC = 0
    INTERNAL = 1
    CONFIDENTIAL = 2
    SECRET = 3


class UserContext(BaseModel):
    user_id: str
    tenant_id: str
    department: str
    clearance_level: ClearanceLevel
    roles: list[str] = Field(default_factory=list)


class DocumentMetadata(BaseModel):
    document_id: str
    tenant_id: str
    department: str
    access_level: ClearanceLevel
    source_path: str
    page_number: int | None = None
