import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

sys.path.insert(0, str(Path(__file__).resolve().parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROJECT_ROOT  = Path(__file__).resolve().parent.parent
GRAPHRAG_ROOT = PROJECT_ROOT / "graphrag_input"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Loading GraphRAG engine from {GRAPHRAG_ROOT} ...")
    try:
        from query_engine import init_engine
        init_engine(str(GRAPHRAG_ROOT))
        logger.info("GraphRAG engine ready ✅")
    except Exception as e:
        logger.error(f"Engine load failed (queries will return 503): {e}")
    yield
    logger.info("Shutdown")


app = FastAPI(
    title="K-Drama GraphRAG API",
    description="Persistent in-memory GraphRAG over 1637 K-dramas",
    version="2.0.0",
    lifespan=lifespan,
)


class QueryRequest(BaseModel):
    question: str
    method: str = "global"


class QueryResponse(BaseModel):
    question: str
    method: str
    answer: str


@app.get("/")
def root():
    try:
        from query_engine import get_engine
        loaded = get_engine()._loaded
    except Exception:
        loaded = False
    return {"status": "running", "engine_loaded": loaded}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    if request.method not in ["global", "local"]:
        raise HTTPException(400, "method must be 'global' or 'local'")
    if not request.question.strip():
        raise HTTPException(400, "question cannot be empty")
    try:
        from query_engine import get_engine
        answer = get_engine().query_sync(request.question, request.method)
        return QueryResponse(
            question=request.question,
            method=request.method,
            answer=answer,
        )
    except RuntimeError as e:
        raise HTTPException(503, f"Engine not ready: {e}")
    except Exception as e:
        logger.exception("Query failed")
        raise HTTPException(500, str(e))