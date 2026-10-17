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

logger = logging.getLogger(__name__)

redis_host = os.getenv("REDIS_HOST", "localhost")
r = redis.Redis(host=redis_host, port=6379, db=0)

def get_redis_client() -> redis.Redis:
    return r

app = FastAPI(title="AMD Doc Agent API")

@lru_cache(maxsize=1)
def get_rag_components():
    logger.info("Loading vector store")
    
    vs, document_chunks = load_vectorstore()
    logger.info("Vector store loaded: %d chunks", len(document_chunks))

    logger.info("Building RAG chain")
    retriever = get_retriever(vs, document_chunks)
    chain = build_rag_chain(retriever, vs, document_chunks)
    logger.info("RAG chain initialization complete")
    
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

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    process_time = time.time() - start
    response.headers["X-Process-Time"] = f"{process_time:.3f}s"
    return response

@app.post("/ask", response_model=AnswerResponse)
def ask_question(
    request: QuestionRequest,
    cache_client: redis.Redis = Depends(get_redis_client),
    rag_components: tuple = Depends(get_rag_components)
):
    vs, document_chunks, chain = rag_components
    
    try:
        cached = get_cache(cache_client, request.question)
    except redis.exceptions.RedisError:
        logger.warning("Redis cache read failed; continuing without cache", exc_info=True)
        cached = None
    
    if cached:
        logger.debug("Cache hit")
        return AnswerResponse(**cached)
        
    logger.debug("Cache miss")
    
    try:
        retrieved_chunks = retrieve_multilingual(vs, document_chunks, request.question, k=4)
        sources = {chunk.metadata["source"] for chunk in retrieved_chunks}
        answer = ask(chain, request.question)

        response =  AnswerResponse(
            answer=answer,
            question=request.question,
            sources = list(sources)
        )
        try:
            set_cache(cache_client, request.question, response.model_dump())
        except redis.exceptions.RedisError:
            logger.warning("Redis cache write failed; returning uncached answer", exc_info=True)
    
        return response
       
    except Exception as e:
        logger.exception("Failed to process /ask request")
        raise HTTPException(status_code=500, detail="Internal server error") from e