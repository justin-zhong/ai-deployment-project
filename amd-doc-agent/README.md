---
title: AMD Doc Agent
emoji: 🤖
colorFrom: red
colorTo: blue
sdk: docker
pinned: false
---

[English](README.md) | [中文](README_CN.md)

# 🔍 Project 4: AMD Technical Document Multi-Document Q&A System

> **Project Series:** [Projects 1–2: RAG Knowledge Base](../rag-knowledge-bot) → [Project 3: Bootgen Agent](../bootgen-agent) → **Project 4: Multi-Document RAG + Deployment (Current)**

A multi-document RAG (Retrieval-Augmented Generation) system designed for AMD
FPGA/SoC technical documentation. Building on the previous projects, this
version introduces multi-document retrieval, multilingual search, RAGAS-based
evaluation, a FastAPI backend, Redis caching, and cloud deployment.

🚀 **Live Demo:** https://huggingface.co/spaces/chongyuanz/amd-doc-agent

## Knowledge Base

| Document | Content | Language |
|---|---|---|
| UG1283 | Bootgen User Guide | Chinese |
| UG1085 | Zynq UltraScale+ Technical Reference Manual | English |
| UG1137 | Zynq UltraScale+ MPSoC Software Developer Guide | English |

Together, the three documents cover the end-to-end workflow from **hardware
architecture → software development → boot image generation**, enabling
cross-document technical queries.

## Demo

> **Q:** What is the role of FSBL?
>
> **A:** According to UG1085, the FSBL begins execution after the CSU ROM
> enters the post-configuration phase and is responsible for system
> tamper-response handling. According to UG1137, the FSBL copies bitstream
> blocks directly from the flash device and performs authentication.
> According to UG1283, FSBL participates in multiple security-related stages
> of the boot process, including encryption and signing.
>
> *(Information retrieved from UG1085, UG1137, and UG1283.)*

## Core Features

### Multi-Document Retrieval

Three technical documents are embedded into a shared FAISS vector store. Each
chunk is tagged with source metadata such as `source` and `filename`, allowing
the retriever to search across documents and preserve document provenance.

### Multilingual Retrieval with Query Translation

A mixed Chinese-English knowledge base introduces a retrieval bias: Chinese
queries tend to have higher embedding similarity with Chinese chunks, causing
English documents to be systematically under-retrieved.

To address this, the system uses **Query Translation** before retrieval:

1. Generate an English translation of the user's query using an LLM.
2. Search using both the original Chinese query and the translated English query.
3. Merge and deduplicate the results.
4. Select the final top-k chunks.

This significantly improves retrieval of relevant English documentation for
Chinese queries.

### Source Attribution

Each chunk stores source information in `metadata["source"]`. The generation
prompt instructs the LLM to identify the source documents used in its answer,
making responses traceable to the underlying technical documentation.

### FastAPI Backend

In addition to the Streamlit UI, the system provides a RESTful API for
integration with other applications.

The API response includes:

- `answer`
- `question`
- `sources`

Middleware also records the response time for each request.

### Redis Caching

Repeated queries are served directly from Redis instead of running through
the complete RAG pipeline again.

| Configuration | Response Time |
|---|---:|
| Full RAG pipeline | ~13 seconds |
| Redis cache hit | ~0.005 seconds |

This represents approximately a **2,600× reduction in latency on cache hits**.

Cache keys are normalized by converting text to lowercase and removing
whitespace, reducing unnecessary cache misses caused by minor differences in
query formatting.

### RAGAS Evaluation

RAGAS is used to quantitatively evaluate system quality. This provides a more
semantic evaluation approach than the keyword-matching evaluation used in
Project 2.

| Metric | Baseline Vector Retrieval | Hybrid Retrieval + Query Translation | Improvement |
|---|---:|---:|---:|
| Faithfulness | 0.39 | **0.80** | +105% |
| Answer Relevancy | 0.54 | 0.50 | — |
| Context Precision | 0.06 | **0.16** | +171% |

The addition of BM25 hybrid retrieval and Query Translation improved
**Faithfulness by 105%** and **Context Precision by 171%**, significantly
reducing unsupported or hallucinated responses in the evaluation set.

The remaining low scores primarily originate from the retrieval layer:
residual PDF noise remains after preprocessing, and semantic mismatch still
exists between Chinese queries and English technical documentation. These
remain key areas for further optimization.

### Cloud Deployment

The application is containerized with Docker and deployed to
**Hugging Face Spaces** using the CPU Free tier, making the system publicly
accessible.

## Tech Stack

- **LangChain** — RAG framework for document loading, chunking, and retrieval
- **OpenAI** — `text-embedding-ada-002` embeddings
- **DeepSeek** — LLM generation
- **FAISS** — Local vector store
- **RAGAS** — RAG evaluation framework
- **FastAPI** — RESTful API backend
- **Redis** — Response caching
- **Streamlit** — Web UI
- **Docker** — Containerization
- **Hugging Face Spaces** — Cloud hosting

## Quick Start

### Local Streamlit Application

```bash
pip install -r requirements.txt
cp .env.example .env

# Add OPENAI_API_KEY and DEEPSEEK_API_KEY to .env

streamlit run app.py

# Local FastAPI Server
uvicorn main:app --reload
# Open http://localhost:8000/docs to access the interactive API documentation.

# Start Redis with Docker
docker run -d -p 6379:6379 redis

# Run the Complete Application with Docker
docker build -t amd-doc-agent .
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_key \
  -e DEEPSEEK_API_KEY=your_key \
  amd-doc-agent
```

## Project Structure

```
├── data/                  # Three AMD technical documentation PDFs
├── src/
│   ├── loader.py          # Multi-document loading, noise cleaning, and source metadata
│   ├── embedder.py        # Embedding generation and FAISS storage
│   ├── retriever.py       # Similarity search + multilingual retrieval
│   │                       # (Query Translation)
│   ├── chain.py            # RAG chain and source attribution prompt
│   ├── evaluator.py       # Keyword-based evaluation (baseline)
│   └── evaluator_ragas.py # RAGAS evaluation (advanced)
├── main.py                # FastAPI entry point (REST API + Redis cache)
├── cache.py               # Redis caching logic
├── app.py                 # Streamlit entry point
├── Dockerfile
├── requirements.txt
└── README.md
```

## Project Evolution

```
Project 1: Basic RAG
  · Single-document PDF/TXT support
  · Local execution
  · Keyword-based evaluation
    ↓ Add domain-specific documentation + PDF noise cleaning

Project 2: AMD Bootgen Q&A
  · UG1283 single-document knowledge base
  · PDF noise cleaning
  · 15-question evaluation module
    ↓ Add Agent + tool calling + MCP + LangSmith

Project 3: Bootgen Agent
  · LangChain Agent → LangGraph
  · Four domain-specific tools
  · MCP Server
  · LangSmith tracing
    ↓ Add multi-document retrieval + multilingual search
      + RAGAS + FastAPI + Redis + deployment

Project 4: AMD Multi-Document Q&A System (Current)
  · Three-document mixed-language knowledge base
  · Query Translation
  · RAGAS evaluation
  · FastAPI + Redis caching
  · Docker + Hugging Face Spaces deployment
```

## Technical Challenges and Findings

**Multilingual Retrieval Bias**
With OpenAI embeddings, Chinese queries tend to have higher similarity with
Chinese chunks than English chunks. As a result, English documentation can be
systematically under-retrieved.
**Solution:** Query Translation generates an English version of the user's
query before retrieval, enabling parallel Chinese and English searches.

This substantially improves cross-language retrieval for the mixed-language
knowledge base.

**Impact of PDF Noise on Retrieval**
Technical documentation often contains repeated headers, footers, page
numbers, and other PDF artifacts. These repeated elements can contaminate the
embedding space and artificially increase similarity between unrelated chunks.

Regex-based cleaning combined with skipping cover and table-of-contents pages
reduced the number of chunks from approximately 2,000 to 1,792, improving
retrieval discrimination.

**Evolution of the Evaluation Framework**
Project 2 used keyword matching to evaluate answers. While simple, this
approach cannot reliably capture semantic correctness.

Project 4 introduced RAGAS, using metrics such as Faithfulness and Context
Precision to quantitatively evaluate the RAG pipeline.

The evaluation showed that retrieval quality was the primary bottleneck,
providing a clear direction for further optimization.

**Practical Impact of Redis Caching**
For identical queries, response latency decreased from approximately
13 seconds for the complete RAG pipeline to 0.005 seconds on a Redis
cache hit — approximately a 2,600× reduction.

Query normalization, including lowercasing and whitespace removal, helps
reduce unnecessary cache misses from minor formatting differences.

## Known Limitations and Future Directions

- Parsing quality for tables and multi-column layouts in English PDFs remains
limited.
- Query Translation introduces an additional LLM call and therefore adds some
latency.
- The RAGAS Answer Relevancy metric has compatibility issues with the
DeepSeek API because the API does not support n > 1.
The knowledge base can be expanded to additional AMD documentation such as
AM011 and UG1304.
- A managed vector database such as Pinecone could be considered as the
knowledge base grows.
- A reranking model could be introduced to further improve retrieval
precision.
