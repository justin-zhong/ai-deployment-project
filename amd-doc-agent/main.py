from fastapi import Depends, FastAPI, HTTPException, Request
from functools import lru_cache
from pydantic import BaseModel
import time
from src.embedder import load_vectorstore
from src.retriever import get_retriever, retrieve_multilingual
from src.chain import build_rag_chain, ask

import redis
from cache import get_cache, set_cache
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

redis_host = os.getenv("REDIS_HOST", "localhost")
r = redis.Redis(host=redis_host, port=6379, db=0)

def get_redis_client() -> redis.Redis:
    return r

app = FastAPI(title="AMD Doc Agent API")

@lru_cache(maxsize=1)
def get_rag_components():
    start = time.perf_counter()
    
    logger.info("Loading vector store")
    vs, document_chunks = load_vectorstore()
    logger.info(
        "Vector store loaded: %d chunks duration_ms=%.1f",
        len(document_chunks),
        (time.perf_counter() - start) * 1000
    )

    chain_start = time.perf_counter()

    logger.info("Building RAG chain")
    retriever = get_retriever(vs, document_chunks)
    chain = build_rag_chain(retriever, vs, document_chunks)
    
    logger.info(
        "RAG chain initialization complete duration_ms=%.1f",
        (time.perf_counter() - chain_start) * 1000
    )
    
    return vs, document_chunks, chain

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str
    question: str
    sources: list[str]

@app.get("/")
def root():
    return {"message": "AMD Doc Agent API", "status": "running"}

@app.get("/health/live")
def health_live():
    return {"status": "alive"}

@app.get("/health/ready")
def health_ready():
    try:
        vs, document_chunks, chain = get_rag_components()
        
        if vs is None or chain is None or not document_chunks:
            raise RuntimeError("RAG components are not ready")
    
    except Exception as exc:
        logger.exception("Readiness check failed")
        raise HTTPException(
            status_code=503,
            detail="Service not ready"
        ) from exc
        
    return {
        "status": "ready",
        "document_chunks": len(document_chunks)
    }

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        
        logger.exception(
            "Request failed method=%s path=%s duration_ms=%.1f",
            request.method,
            request.url.path,
            duration_ms
        )
        raise
        
    duration_ms = (time.perf_counter() - start) * 1000
    
    response.headers["X-Process-Time"] = (f"{duration_ms / 1000:.3f}s")
    
    logger.info(
        "Request completed method=%s path=%s status_code=%s duration_ms=%.1f",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms
    )
    
    return response

@app.post("/ask", response_model=AnswerResponse)
def ask_question(
    request: QuestionRequest,
    cache_client: redis.Redis = Depends(get_redis_client),
    rag_components: tuple = Depends(get_rag_components)
):
    vs, document_chunks, chain = rag_components
    
    try:
        cache_start = time.perf_counter()
        
        try:
            cached = get_cache(cache_client, request.question)
        except redis.exceptions.RedisError:
            logger.warning("Redis cache read failed; continuing without cache", exc_info=True)
            cached = None
            
        cache_lookup_ms = (time.perf_counter() - cache_start) * 1000
        
        logger.info(
            "Cache lookup completed duration_ms=%.1f hit=%s",
            cache_lookup_ms,
            bool(cached)
        )
    
        if cached:
            logger.debug("Cache hit")
            return AnswerResponse(**cached)
        
        logger.debug("Cache miss")
    
        retrieval_start = time.perf_counter()
        retrieved_chunks = retrieve_multilingual(vs, document_chunks, request.question, k=4)
        retrieval_ms = (time.perf_counter() - retrieval_start) * 1000
        
        logger.info(
            "Document retrieval completed duration_ms=%.1f chunks=%d",
            retrieval_ms,
            len(retrieved_chunks)
        )
        
        sources = {chunk.metadata["source"] for chunk in retrieved_chunks}
        
        chain_start = time.perf_counter()
        answer = ask(chain, request.question)
        chain_ms = (time.perf_counter() - chain_start) * 1000
        
        logger.info(
            "RAG chain execution completed duration_ms=%.1f",
            chain_ms
        )

        response =  AnswerResponse(
            answer=answer,
            question=request.question,
            sources = list(sources)
        )
        
        cache_write_start = time.perf_counter()
        
        try:
            set_cache(cache_client, request.question, response.model_dump())
        except redis.exceptions.RedisError:
            cache_write_ms = (time.perf_counter() - cache_write_start) * 1000
            
            logger.warning(
                "Redis cache write failed; returning uncached answer",
                "duration_ms=%.1f",
                cache_write_ms,
                exc_info=True
            )
        else:
            cache_write_ms = (time.perf_counter() - cache_write_start) * 1000
            logger.info(
                "Cache write completed duration_ms=%.1f",
                cache_write_ms
            )
    
        return response
       
    except Exception as e:
        logger.exception("Failed to process /ask request")
        raise HTTPException(status_code=500, detail="Internal server error") from e