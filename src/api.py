from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import asyncio
from pathlib import Path

app = FastAPI(
    title="K-Drama GraphRAG API",
    description="Query a knowledge graph of 100 top K-dramas using GraphRAG",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    question: str
    method: str = "global"

class QueryResponse(BaseModel):
    question: str
    method: str
    answer: str

ROOT = Path("./graphrag_input")

@app.get("/")
def root():
    return {"status": "running", "message": "K-Drama GraphRAG API"}

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    if request.method not in ["global", "local"]:
        raise HTTPException(status_code=400, detail="Method must be 'global' or 'local'")

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")

    try:
        import subprocess
        env = os.environ.copy()
        env["GRAPHRAG_API_KEY"] = os.getenv("GRAPHRAG_API_KEY", "")
        
        result = subprocess.run(
            [
                "graphrag", "query",
                "--root", "./graphrag_input",
                "--method", request.method,
                "--query", request.question
            ],
            capture_output=True,
            text=True,
            timeout=180,
            env=env,
            cwd="/Users/shravani/PROJECT-KD"
        )

        print("STDOUT:", result.stdout[:500])
        print("STDERR:", result.stderr[:200])

        output = result.stdout
        if "SUCCESS:" in output:
            answer = output.split("SUCCESS:", 1)[1].strip()
            if "Global Search Response:" in answer:
                answer = answer.split("Global Search Response:", 1)[1].strip()
            elif "Local Search Response:" in answer:
                answer = answer.split("Local Search Response:", 1)[1].strip()
        else:
            answer = output.strip() or result.stderr or "No response generated"

        return QueryResponse(
            question=request.question,
            method=request.method,
            answer=answer
        )

    except Exception as e:
        print("EXCEPTION:", str(e))
        raise HTTPException(status_code=500, detail=str(e))