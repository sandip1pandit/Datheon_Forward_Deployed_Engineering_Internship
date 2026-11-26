
import os
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load local .env when running outside Docker.
# Docker environment variables take precedence.
load_dotenv(PROJECT_ROOT / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL_NAME = os.getenv(
    "MODEL_NAME",
    "openai/gpt-oss-120b"
)


def validate_config():
    """Validate required environment configuration."""

    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Configure it using environment variables."
        )

    return True
