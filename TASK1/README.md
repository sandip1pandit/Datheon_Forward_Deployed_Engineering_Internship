# Legacy Data ETL Pipeline

A Python-based data ingestion and vector ETL pipeline designed to process legacy PDF, CSV, and Markdown documents. It extracts text, enriches documents with source metadata, splits content into chunks, generates semantic embeddings, and stores vectors in a local Qdrant database.

## Features

- **Multi-format extraction:** Supports PDF, CSV, and Markdown files.
- **Metadata enrichment:** Preserves source information, filenames, file types, client IDs, departments, and access tiers.
- **Text chunking:** Splits documents into manageable chunks with configurable chunk size and overlap.
- **Semantic embeddings:** Generates 384-dimensional embeddings using Sentence Transformers.
- **Vector storage:** Stores embeddings and document metadata in a persistent local Qdrant database.
- **Semantic search:** Retrieves relevant document chunks using query embeddings.
- **Metadata filtering:** Filters search results using client ID, department, access tier, and file type.
- **Batch ingestion:** Processes multiple documents and stores their chunks in a batch.
- **Performance benchmarking:** Compares embedding batch sizes and measures ingestion throughput.

## Architecture

```text
                 Raw Documents
              PDF | CSV | Markdown
                       |
                       v
                 Text Extraction
                       |
                       v
                Metadata Enrichment
                       |
                       v
                  Text Chunking
                       |
                       v
                Embedding Generation
                       |
                       v
                  Qdrant Vector DB
                       |
                       v
                Semantic Search
```

Extracted text and chunk information are also saved separately:

```text
Processed Documents
       |
       +-- Extracted text (.txt)
       |
       +-- Chunk data (.chunks.json)
```

## Project Structure

```text
TASK1/
│
├── benchmarks/
│   ├── benchmark_ingestion.py
│   └── batch_comparison.json
│
├── data/
│   ├── raw/
│   │   ├── pdf/
│   │   ├── csv/
│   │   └── markdown/
│   │
│   ├── processed/
│   ├── vector_db/
│   └── benchmark_vector_db/
│
├── src/
│   ├── __init__.py
│   ├── models.py
│   ├── extractors.py
│   ├── metadata.py
│   ├── chunking.py
│   ├── embeddings.py
│   ├── vector_store.py
│   └── pipeline.py
│
├── tests/
│   ├── test_extractors.py
│   ├── test_metadata.py
│   ├── test_chunking_behavior.py
│   ├── test_embeddings.py
│   ├── test_query_embedding.py
│   ├── test_vector_store.py
│   ├── test_vector_search.py
│   └── test_metadata_filtering.py
│
├── .env
├── .env.example
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

## Technology Stack

| Component | Technology |
|---|---|
| Programming language | Python 3.12 |
| PDF extraction | PyPDF |
| Text processing | LangChain Text Splitters |
| Data validation | Pydantic |
| Embedding model | Sentence Transformers |
| Embedding dimensions | 384 |
| Vector database | Qdrant |
| Testing | Pytest |

## Installation

Clone the repository and navigate to the project directory.

```bash
cd FDE/TASK1
```

Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your environment configuration:

```powershell
copy .env.example .env
```

Place your source documents into the appropriate directories:

```text
data/raw/
├── pdf/
├── csv/
└── markdown/
```

The embedding model is downloaded automatically on its first use.

## Running the Pipeline

Run the ingestion pipeline from the project root:

```bash
python -m src.pipeline
```

The pipeline performs the following operations:

1. Discovers supported source files.
2. Extracts document text.
3. Enriches documents with metadata.
4. Splits text into chunks.
5. Generates embeddings in batches.
6. Stores vectors and metadata in Qdrant.
7. Saves extracted text and chunk JSON files.

**Output locations:**

- Processed documents: `data/processed/`
- Vector database: `data/vector_db/`
- Run summary: `data/processed/run_summary.json`

## Semantic Search and Metadata Filtering

The vector store supports semantic retrieval using query embeddings.

Example:

```python
from src.embeddings import embed_query
from src.vector_store import search_chunks

query = "Which plant still uses the legacy invoice system?"

query_vector = embed_query(query)

results = search_chunks(
    query_vector=query_vector,
    limit=5,
)

for result in results:
    print(result["score"])
    print(result["text"])
```

Metadata filters can also be applied:

```python
results = search_chunks(
    query_vector=query_vector,
    limit=5,
    client_id="client_001",
    department="operations",
    access_tier="internal",
)
```

Available filters:

- `client_id`
- `department`
- `access_tier`
- `file_type`

## Batch Ingestion Benchmark

The project includes a benchmark script to compare embedding batch sizes.

Run:

```bash
python -m benchmarks.benchmark_ingestion
```

The benchmark evaluates these batch sizes:

```text
1, 2, 4, 8, 32
```

It records:

- Execution time
- Number of files processed
- Number of chunks stored
- Files processed per second
- Chunks processed per second

Results are saved to:

```text
benchmarks/batch_comparison.json
```

### Preliminary Benchmark Results

The following measurements were obtained using two sample files containing two total chunks.

| Batch Size | Execution Time (seconds) | Chunks/Second |
|---:|---:|---:|
| 1 | 0.4872 | 4.1053 |
| 2 | 0.4017 | 4.9790 |
| 4 | 0.3817 | 5.2391 |
| 8 | 0.3650 | 5.4798 |
| 32 | 0.2636 | 7.5885 |

Batch size 32 achieved the lowest execution time in this preliminary experiment.

**Note:** These results are indicative only. The dataset is small, and each configuration was measured once. Larger datasets and repeated runs are required for reliable performance comparisons.

## Running Tests

Run the complete test suite:

```bash
python -m pytest -v
```

The tests cover:

- File extraction
- Metadata enrichment and validation
- Chunking behavior
- Embedding generation
- Query embeddings
- Vector storage
- Semantic search
- Metadata filtering

**Latest verification:** 15 tests passed.

## Configuration

The embedding model defaults to:

```text
sentence-transformers/all-MiniLM-L6-v2
```

The model produces 384-dimensional embeddings.

Embedding batch size defaults to 32 and can be changed when calling `embed_chunks()`.

The local Qdrant database is persisted on disk, so data remains available between pipeline runs.

## Limitations

- PDF extraction works best with text-based PDFs. Scanned documents require OCR.
- The embedding model is downloaded locally on first use.
- Benchmark results depend on hardware, dataset size, and model initialization.
- The current benchmark dataset is too small to establish production-scale throughput.

## Future Improvements

- OCR support for scanned PDF documents.
- Larger-scale ingestion benchmarking.
- Improved ingestion failure reporting and recovery.
- Additional metadata filtering and validation tests.
- Support for more document formats.

---

**Project:** Legacy Data ETL Pipeline
**Focus:** Document Processing | Embeddings | Vector Databases | Batch Ingestion | Semantic Search