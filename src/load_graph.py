import os
from pathlib import Path
from huggingface_hub import snapshot_download


def download_graph_if_needed():
    output_path = Path("graphrag_input/output")
    lancedb_path = output_path / "lancedb"

    # Check both parquet files AND lancedb exist locally
    parquet_ok = output_path.exists() and any(output_path.glob("*.parquet"))
    lancedb_ok = lancedb_path.exists() and any(lancedb_path.iterdir())

    if parquet_ok and lancedb_ok:
        print("Graph + embeddings already exist locally, skipping download")
        return

    print("Downloading graph index from Hugging Face...")
    output_path.mkdir(parents=True, exist_ok=True)

    snapshot_download(
        repo_id="shrav2324/kdrama-graphrag-index",
        repo_type="dataset",
        local_dir=str(output_path),
        token=os.getenv("HF_TOKEN"),
    )
    print(f"Download complete. Parquet files: {list(output_path.glob('*.parquet'))}")
    print(f"LanceDB tables: {list(lancedb_path.iterdir()) if lancedb_path.exists() else 'missing'}")