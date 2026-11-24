
from langchain_text_splitters import RecursiveCharacterTextSplitter


text = """
# Engineering Department

The factory uses an old invoice system.

Operators maintain daily records.

These records are stored in PDF files.
"""

splitter = RecursiveCharacterTextSplitter(
    chunk_size=80,
    chunk_overlap=15,
    separators=["\n\n", "\n", ". ", " ", ""]
)

chunks = splitter.split_text(text)

for index, chunk in enumerate(chunks):
    print(f"\nChunk {index}:")
    print(chunk)
    print("Length:", len(chunk))

print("\nTotal chunks:", len(chunks))
