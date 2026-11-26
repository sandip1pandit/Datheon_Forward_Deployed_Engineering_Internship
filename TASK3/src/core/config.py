
import os
from pathlib import Path

from dotenv import load_dotenv

# Find the TASK3 project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Load environment variables from TASK3/.env
load_dotenv(PROJECT_ROOT / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

MODEL_NAME = "openai/gpt-oss-120b"


def validate_config():
    """Check whether required configuration exists."""

    if not GROQ_API_KEY:
        raise RuntimeError(
            "GROQ_API_KEY is missing. Check your TASK3/.env file."
        )

    return True
