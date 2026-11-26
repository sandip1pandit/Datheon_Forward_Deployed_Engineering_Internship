import logging
import os
import tempfile
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4
from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
)
from fastapi.concurrency import run_in_threadpool

from .models import ClearanceLevel, UserContext
from .security import get_current_user, create_access_token
from .user_store import initialize_database, authenticate_user
from .ingestion import ingest_pdf
from .pipeline import answer_question
from .schemas import (
    LoginRequest,
    TokenResponse,
    ChatRequest,
    IngestionResponse,
)

logger = logging.getLogger(__name__)

MAX_UPLOAD_SIZE = 10 * 1024 * 1024

MAX_UPLOAD_SIZE = 10 * 1024 * 1024


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Enterprise Multi-Tenant RAG API",
    description="Secure document ingestion and question answering with RBAC.",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
def root():
    return {
        "message": "Enterprise RAG API is running",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/auth/token", response_model=TokenResponse)
def login(request: LoginRequest):
    user = authenticate_user(
        request.username,
        request.password
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    token = create_access_token(user)

    return TokenResponse(access_token=token)



@app.post("/documents/ingest", response_model=IngestionResponse)
async def ingest_document(
    file: UploadFile = File(...),
    department: str = Form(...),
    access_level: ClearanceLevel = Form(...),
    current_user: UserContext = Depends(get_current_user)
):
    # Only tenant admins can upload documents.
    if "tenant_admin" not in current_user.roles:
        raise HTTPException(
            status_code=403,
            detail="Tenant admin role required"
        )

    # Prevent assigning clearance above the admin's own level.
    if access_level > current_user.clearance_level:
        raise HTTPException(
            status_code=403,
            detail="Cannot assign access above your clearance"
        )

    if not department.strip():
        raise HTTPException(
            status_code=400,
            detail="Department cannot be empty"
        )

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported"
        )

    content = await file.read(MAX_UPLOAD_SIZE + 1)

    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=413,
            detail="PDF exceeds the 10 MB upload limit"
        )

    if not content.startswith(b"%PDF-"):
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not a valid PDF"
        )

    # Permanent PDF storage
    upload_dir = Path(__file__).resolve().parents[1] / "data" / "raw" / "pdf"
    stored_path = upload_dir / f"{uuid4().hex}.pdf"

    try:
        upload_dir.mkdir(parents=True, exist_ok=True)
        stored_path.write_bytes(content)

        result = await run_in_threadpool(
            ingest_pdf,
            pdf_path=str(stored_path),
            tenant_id=current_user.tenant_id,
            department=department.strip(),
            access_level=access_level
        )

        return result

    except (ValueError, FileNotFoundError) as error:
        stored_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        stored_path.unlink(missing_ok=True)
        logger.exception("Document ingestion failed")
        raise HTTPException(
            status_code=500,
            detail="Unable to ingest document"
        )

    finally:
        await file.close()



@app.post("/chat")
async def chat(
    request: ChatRequest,
    current_user: UserContext = Depends(get_current_user)
):
    try:
        result = await run_in_threadpool(
            answer_question,
            query=request.query,
            user=current_user,
            chat_history=request.chat_history
        )

        return result

    except Exception:
        logger.exception("Chat request failed")
        raise HTTPException(
            status_code=500,
            detail="Unable to process the question"
        )
