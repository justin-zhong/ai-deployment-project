from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import time
from src.embedder import load_vectorstore
from src.retriever import get_retriever, retrieve_multilingual
from src.chain import build_rag_chain, ask

import redis
from cache import get_cache, set_cache

import pickle

r = redis.Redis(host="localhost", port=6379, db=0)

app = FastAPI(title="AMD Doc Agent API")

with open("vectorstore/chunks.pkl", "rb") as f:
    document_chunks = pickle.load(f)

vs = load_vectorstore()
retriever = get_retriever(vs, document_chunks)
chain = build_rag_chain(retriever, vs, document_chunks)

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
def ask_question(request: QuestionRequest):
    cached = get_cache(r, request.question)
    if cached:
        return AnswerResponse(**cached)
    try:
        retrieved_chunks = retrieve_multilingual(vs, document_chunks, request.question, k=4)
        sources = {chunk.metadata["source"] for chunk in chunks}
        answer = ask(chain, request.question)

        response =  AnswerResponse(
            answer=answer,
            question=request.question,
            sources = list(sources)
        )

        set_cache(r, request.question, response.model_dump())
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))