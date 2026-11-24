
from src.models import ExtractedDocument
from src.chunking import chunk_document


def test_chunking_behavior():

    text = (
        "Artificial intelligence is transforming industries. "
        "Machine learning helps computers learn from data. "
        "Vector databases store numerical representations."
    )

    document = ExtractedDocument(
        source_path="sample.md",
        file_type="markdown",
        text=text
    )

    chunks = chunk_document(
        document,
        chunk_size=60,
        chunk_overlap=15
    )

    for chunk in chunks:
        print("\nChunk:", chunk.chunk_index)
        print("Text:", chunk.text)
        print("Length:", len(chunk.text))

    print("\nTotal chunks:", len(chunks))

def demonstrate_word_splitting():

    text = "I love learning Python programming"

    words = text.split()

    chunk_size = 3
    overlap = 1

    start = 0

    while start < len(words):

        end = min(start + chunk_size, len(words))

        chunk = " ".join(words[start:end])

        print("Chunk:", chunk)

        if end == len(words):
            break

        start = end - overlap


if __name__ == "__main__":
    demonstrate_word_splitting()