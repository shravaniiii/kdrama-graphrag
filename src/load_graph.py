import os
from pathlib import Path
from huggingface_hub import snapshot_download

def download_graph_if_needed():
    output_path = Path("graphrag_input/output")
    
    if output_path.exists() and any(output_path.iterdir()):
        print("Graph already exists locally, skipping download")
        return
    
    print("Downloading graph from Hugging Face...")
    output_path.mkdir(parents=True, exist_ok=True)
    
    snapshot_download(
        repo_id="shrav2324/kdrama-graphrag-index",
        repo_type="dataset",
        local_dir=str(output_path),
        token=os.getenv("HF_TOKEN")
    )
    print("Graph downloaded successfully!")