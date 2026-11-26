import os
from datetime import datetime, timedelta, timezone

import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pwdlib import PasswordHash
from pydantic import ValidationError

from .models import UserContext, DocumentMetadata

load_dotenv()

ALGORITHM = "HS256"
bearer_scheme = HTTPBearer()
password_hasher = PasswordHash.recommended()


def get_secret_key():
    secret = os.getenv("JWT_SECRET_KEY")

    if not secret:
        raise RuntimeError("JWT_SECRET_KEY is not configured")

    return secret


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hasher.verify(password, hashed_password)


def create_access_token(
    user: UserContext,
    expires_minutes: int = 60
) -> str:

    payload = {
        "sub": user.user_id,
        "tenant_id": user.tenant_id,
        "department": user.department,
        "clearance_level": int(user.clearance_level),
        "roles": user.roles,
        "exp": datetime.now(timezone.utc)
        + timedelta(minutes=expires_minutes)
    }

    return jwt.encode(
        payload,
        get_secret_key(),
        algorithm=ALGORITHM
    )


def decode_access_token(token: str) -> UserContext:
    try:
        payload = jwt.decode(
            token,
            get_secret_key(),
            algorithms=[ALGORITHM]
        )

        return UserContext(
            user_id=payload["sub"],
            tenant_id=payload["tenant_id"],
            department=payload["department"],
            clearance_level=payload["clearance_level"],
            roles=payload["roles"]
        )

    except (jwt.InvalidTokenError, KeyError, ValidationError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> UserContext:

    return decode_access_token(credentials.credentials)


def can_access_document(
    user: UserContext,
    document: DocumentMetadata
) -> bool:

    # A user can only access documents belonging to their tenant.
    if user.tenant_id != document.tenant_id:
        return False

    # Check the user's security clearance.
    if user.clearance_level < document.access_level:
        return False

    # Tenant admins can access all departments within their tenant.
    if "tenant_admin" in user.roles:
        return True

    # Regular users can access their own department's documents.
    return user.department == document.department
