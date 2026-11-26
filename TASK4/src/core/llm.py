
from groq import Groq

from src.core.config import GROQ_API_KEY, MODEL_NAME, validate_config


# Validate configuration before creating the client
validate_config()

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)


def generate_response(prompt: str) -> str:
    """Generate a response using the Groq LLM."""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content
