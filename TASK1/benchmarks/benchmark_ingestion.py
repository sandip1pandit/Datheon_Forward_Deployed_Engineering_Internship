
from pathlib import Path
import json
import time

from src.pipeline import run
from src.embeddings import get_embedding_model


ROOT = Path(__file__).resolve().parents[1]

RAW_DIR = ROOT / "data" / "raw"
VECTOR_DB_DIR = ROOT / "data" / "benchmark_vector_db"

BATCH_SIZES = [1, 2, 4, 8, 32]


def benchmark_ingestion():

    # Load model before benchmarking
    get_embedding_model()

    results = []

    for batch_size in BATCH_SIZES:

        print(f"\nTesting batch size: {batch_size}")

        processed_dir = (
            ROOT / "data" / f"benchmark_processed_{batch_size}"
        )

        collection_name = f"benchmark_batch_{batch_size}"

        start_time = time.perf_counter()

        result = run(
            raw_dir=RAW_DIR,
            processed_dir=processed_dir,
            persist_dir=VECTOR_DB_DIR,
            collection_name=collection_name,
            batch_size=batch_size,
        )

        elapsed_time = time.perf_counter() - start_time

        files = result["files"]
        chunks = result["chunks"]

        report = {
            "batch_size": batch_size,
            "execution_time_seconds": round(elapsed_time, 4),
            "files_processed": files,
            "chunks_stored": chunks,
            "files_per_second": round(files / elapsed_time, 4)
            if elapsed_time > 0 else 0,
            "chunks_per_second": round(chunks / elapsed_time, 4)
            if elapsed_time > 0 else 0,
            "skipped": result["skipped"],
        }

        results.append(report)

        print(json.dumps(report, indent=2))

    report_path = ROOT / "benchmarks" / "batch_comparison.json"

    report_path.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )

    print("\n========== BATCH SIZE COMPARISON ==========")
    print(json.dumps(results, indent=2))
    print(f"\nResults saved to: {report_path}")


if __name__ == "__main__":
    benchmark_ingestion()
