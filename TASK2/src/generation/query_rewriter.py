import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

MODEL_NAME = "llama-3.3-70b-versatile"


def rewrite_query(query: str, chat_history: list[dict] | None = None) -> str:
    """
    Rewrite a user's question into a clear standalone retrieval query.

    Falls back to the original query if Groq is unavailable.
    """

    if not query or not query.strip():
        return ""

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        return query.strip()

    history_text = ""

    if chat_history:
        history_text = "\n".join(
            f"{message.get('role', 'user')}: {message.get('content', '')}"
            for message in chat_history[-5:]
        )

    try:
        client = Groq(api_key=api_key)

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You rewrite user questions for enterprise document "
                        "retrieval. Use conversation history to resolve "
                        "references. Return only one clear, standalone search "
                        "query. Do not answer the question. Do not add facts."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Conversation history:\n{history_text}\n\n"
                        f"Current question:\n{query}\n\n"
                        "Rewritten search query:"
                    )
                }
            ],
            temperature=0.0,
            max_tokens=150
        )

        rewritten = response.choices[0].message.content

        if rewritten and rewritten.strip():
            return rewritten.strip()

        return query.strip()

    except Exception:
        # Retrieval should continue even if the rewriting service fails.
        return query.strip()
