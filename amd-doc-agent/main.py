import logging
import os
import time
from collections import deque
from functools import lru_cache
from math import ceil
from threading import Lock

import redis
from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel

from cache import get_cache, set_cache
from src.chain import ask_with_context, build_answer_chain
from src.embedder import load_vectorstore
from src.retriever import retrieve_multilingual

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

request_metrics = deque(maxlen=1000)
metrics_lock = Lock()

DIAGNOSTIC_PATHS = {
    "/health/live",
    "/health/ready",
    "/metrics/summary"
}

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

    logger.info("Building answer chain")
    answer_chain = build_answer_chain()
    
    logger.info(
        "Answer chain initialization complete duration_ms=%.1f",
        (time.perf_counter() - chain_start) * 1000
    )
    
    return vs, document_chunks, answer_chain

def calculate_percentile(values: list[float], percentile: float) -> float | None:
    if not values:
        return None

    ordered = sorted(values)
    index = max(0, ceil(percentile * len(ordered)) - 1)

    return ordered[index]

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

@app.get("/metrics/summary")
def metrics_summary():
    with metrics_lock:
        samples = list(request_metrics)

    count = len(samples)

    if count == 0:
        return {
            "samped_requests": 0,
            "p50_latency_ms": None,
            "p95_latency_ms": None,
            "http_5xx_count": 0,
            "http_5xx_rate_percent": None
        }

    durations = [sample["duration_ms"] for sample in samples]
    server_errors = sum(
        sample["status_code"] >= 500
        for sample in samples
    )

    hits = [
        s for s in samples
        if s.get("cache_status") == "hit"
    ]
    misses = [
        s for s in samples
        if s.get("cache_status") == "miss"
    ]
    unavailable = [
        s for s in samples
        if s.get("cache_status") == "unavailable"
    ]

    def latency_summary(records):
        values = [s["duration_ms"] for s in records]

        return {
            "count": len(values),
            "p50_latency_ms": (
                round(calculate_percentile(values, 0.50), 1)
                if values else None
            ),
            "p95_latency_ms": (
                round(calculate_percentile(values, 0.95), 1)
                if values else None
            )
        }

    return {
        "sample_requests": count,
        "p50_latency_ms": (round(calculate_percentile(durations, 0.50), 1) if durations else None),
        "p95_latency_ms": (round(calculate_percentile(durations, 0.95), 1) if durations else None),
        "http_5xx_count": server_errors,
        "http_5xx_rate_percent": (round(server_errors / count * 100, 2) if count else None),
        "cache_hit": latency_summary(hits),
        "cache_miss": latency_summary(misses),
        "cache_unavailable_count": len(unavailable)
    }

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.perf_counter()
    
    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        
        if request.url.path not in DIAGNOSTIC_PATHS:
            with metrics_lock:
                request_metrics.append({
                    "duration_ms": duration_ms,
                    "status_code": 500,
                    "cache_status": getattr(request.state, "cache_status", "unknown")
                })

        logger.exception(
            "Request failed method=%s path=%s duration_ms=%.1f",
            request.method,
            request.url.path,
            duration_ms
        )
        raise
        
    duration_ms = (time.perf_counter() - start) * 1000
    
    response.headers["X-Process-Time"] = (f"{duration_ms / 1000:.3f}s")
    
    if request.url.path not in DIAGNOSTIC_PATHS:
        with metrics_lock:
            request_metrics.append({
                "duration_ms": duration_ms,
                "status_code": response.status_code,
                "cache_status": getattr(request.state, "cache_status", "unknown")
            })

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
    http_request: Request,
    cache_client: redis.Redis = Depends(get_redis_client)
):
    try:
        cache_start = time.perf_counter()
        
        try:
            cached = get_cache(cache_client, request.question)
        except redis.exceptions.RedisError:
            logger.warning("Redis cache read failed; continuing without cache", exc_info=True)
            cached = None
            http_request.state.cache_status = "unavailable"
        else:
            http_request.state.cache_status = "hit" if cached else "miss"

        cache_lookup_ms = (time.perf_counter() - cache_start) * 1000
        
        logger.info(
            "Cache lookup completed duration_ms=%.1f hit=%s",
            cache_lookup_ms,
            bool(cached)
        )
    
        if cached:
            logger.debug("Cache hit")
            return AnswerResponse(**cached)
        
        vs, document_chunks, answer_chain = get_rag_components()

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
        answer = ask_with_context(
                answer_chain,
                request.question,
                retrieved_chunks
            )

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
                "Redis cache write failed; returning uncached answer"
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