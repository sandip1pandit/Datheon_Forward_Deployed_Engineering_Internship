import json
import sqlite3
from pathlib import Path

from .models import UserContext, ClearanceLevel
from .security import hash_password, verify_password


TASK_ROOT = Path(__file__).resolve().parents[1]
DATABASE_PATH = TASK_ROOT / "data" / "users.db"


def get_connection():
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                department TEXT NOT NULL,
                clearance_level INTEGER NOT NULL,
                roles TEXT NOT NULL
            )
        """)


def create_user(
    username: str,
    password: str,
    tenant_id: str,
    department: str,
    clearance_level: ClearanceLevel,
    roles: list[str] | None = None
):
    if not all(value.strip() for value in (
        username, password, tenant_id, department
    )):
        raise ValueError("User details cannot be empty")

    if len(password) < 8:
        raise ValueError("Password must contain at least 8 characters")

    roles = roles or ["employee"]

    password_hash = hash_password(password)

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO users (
                username, password_hash, tenant_id,
                department, clearance_level, roles
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                username,
                password_hash,
                tenant_id,
                department,
                int(clearance_level),
                json.dumps(roles)
            )
        )


def authenticate_user(username: str, password: str) -> UserContext | None:
    with get_connection() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        ).fetchone()

    if row is None:
        return None

    if not verify_password(password, row["password_hash"]):
        return None

    return UserContext(
        user_id=row["username"],
        tenant_id=row["tenant_id"],
        department=row["department"],
        clearance_level=ClearanceLevel(row["clearance_level"]),
        roles=json.loads(row["roles"])
    )
