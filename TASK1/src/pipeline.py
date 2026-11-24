
from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import date
from dotenv import load_dotenv

from src.chunking import chunk_document
from src.embeddings import embed_chunks
from src.extractors import extract_file, iter_raw_files
from src.metadata import enrich_metadata
from src.vector_store import upsert_chunks

load_dotenv()

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
METADATA_PATH = ROOT / "data" / "metadata.json"

def run(
    raw_dir: Path = RAW_DIR,
    processed_dir: Path = PROCESSED_DIR,
    persist_dir: Path | None = None,
    collection_name: str | None = None,
    batch_size: int = 32,
) -> dict:

    processed_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    files = iter_raw_files(raw_dir)
    metadata_manifest = json.loads(
        METADATA_PATH.read_text(encoding="utf-8")
    )
    summary = {
        "files": 0,
        "chunks": 0,
        "skipped": [],
    }

    all_chunks = []

    # Phase 1: Extract, enrich and chunk every document
    for file_path in files:

        try:
            file_metadata = metadata_manifest.get(file_path.name, {})

            document_date = (
                date.fromisoformat(file_metadata["date"])
                if file_metadata.get("date")
                else None
            )

            document = enrich_metadata(
                extract_file(file_path),
                client_id=file_metadata.get("client_id"),
                department=file_metadata.get("department"),
                access_tier=file_metadata.get("access_tier"),
                document_date=document_date,
            )

            chunks = chunk_document(document)

            all_chunks.extend(chunks)

            _write_processed(
                processed_dir,
                raw_dir,
                file_path,
                document.text,
                chunks,
            )

            summary["files"] += 1

            print(
                f"Prepared {file_path.name}: "
                f"{len(chunks)} chunks"
            )

        except Exception as error:
            summary["skipped"].append({
                "file": str(file_path),
                "error": str(error),
            })

            print(f"Skipped {file_path}: {error}")

    # Phase 2: Generate embeddings for all collected chunks
    if all_chunks:

        try:
            embeddings = embed_chunks(
                all_chunks,
                batch_size=batch_size,
            )

            # Phase 3: Store all chunks in one Qdrant upsert call
            stored = upsert_chunks(
                all_chunks,
                embeddings,
                persist_dir=persist_dir,
                collection_name=collection_name,
            )

            summary["chunks"] = stored

            print(
                f"\nBatch ingestion completed: "
                f"{stored} chunks stored"
            )

        except Exception as error:

            summary["skipped"].append({
                "file": "batch_ingestion",
                "error": str(error),
            })

            summary["files"] = 0

            print(f"Batch ingestion failed: {error}")

    summary_path = processed_dir / "run_summary.json"

    summary_path.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    return summary


def _write_processed(
    processed_dir: Path,
    raw_dir: Path,
    file_path: Path,
    text: str,
    chunks,
) -> None:

    # Preserve the source directory structure.
    relative_path = file_path.relative_to(raw_dir)
    output_dir = processed_dir / relative_path.parent

    output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    stem = file_path.stem

    # Save extracted text.
    (output_dir / f"{stem}.txt").write_text(
        text,
        encoding="utf-8",
    )

    # Save chunks with metadata.
    chunk_payload = [
        chunk.model_dump()
        for chunk in chunks
    ]

    (output_dir / f"{stem}.chunks.json").write_text(
        json.dumps(
            chunk_payload,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

def main() -> None:

    parser = argparse.ArgumentParser(
        description="Legacy Data ETL pipeline"
    )

    parser.add_argument(
        "--raw",
        type=Path,
        default=RAW_DIR,
    )

    parser.add_argument(
        "--processed",
        type=Path,
        default=PROCESSED_DIR,
    )

    args = parser.parse_args()

    result = run(
        args.raw,
        args.processed,
    )

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
