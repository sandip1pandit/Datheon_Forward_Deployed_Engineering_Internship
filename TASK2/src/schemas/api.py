from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ChatRequest(BaseModel):
    query: str = Field(min_length=1, max_length=5000)
    chat_history: list[dict] = Field(default_factory=list)


class IngestionResponse(BaseModel):
    document_id: str
    source_path: str
    pages_processed: int
    chunks_stored: int
    tenant_id: str
    department: str
    access_level: str
