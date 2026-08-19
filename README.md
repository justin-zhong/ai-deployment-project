[English](README.md) | [中文](README_CN.md)

# LLM Application Engineering Projects

Hands-on AI application engineering projects built around AMD FPGA/SoC
technical domains, covering **RAG, LLM Agents, MCP, retrieval optimization,
evaluation, API development, caching, and cloud deployment**.

The projects progress from a basic RAG pipeline to a deployed multi-document
RAG system and a domain-specific LangGraph Agent.

🚀 **[Live Demo — AMD Technical Document RAG System](https://huggingface.co/spaces/chongyuanz/amd-doc-agent)**

---

## Projects

| Project | Directory | Core Technologies | Highlights |
|---|---|---|---|
| Projects 1–2 | `rag-knowledge-bot/` | RAG, FAISS, LangChain | Chunking experiments, PDF noise cleaning, evaluation |
| Project 3 | `bootgen-agent/` | LangGraph, MCP, LangSmith | 4-tool Agent, MCP Server, end-to-end tracing |
| Project 4 | `amd-doc-agent/` | Multi-document RAG, FastAPI, Redis | Query Translation, RAGAS evaluation, Hugging Face deployment |

---

## Project Evolution

```text
Project 1: Basic RAG
  · Built a single-document PDF/TXT Q&A pipeline
  · Experimented with chunk size and overlap
  · Validated the end-to-end RAG workflow
    ↓
Project 2: Domain-Specific RAG
  · Applied RAG to AMD technical documentation (UG1283)
  · Cleaned PDF artifacts such as headers, footers, and page numbers
  · Built a 15-question evaluation set with keyword-based evaluation
  · Analyzed retrieval limitations in technical documentation
    ↓
Project 3: Bootgen Intelligent Assistant Agent
  · Migrated from LangChain Agent to LangGraph StateGraph
  · Built 4 specialized tools:
      RAG Search / BIF Generation / Command Validation / Device Comparison
  · Exposed tools through an MCP Server
  · Integrated LangSmith for end-to-end agent tracing
    ↓
Project 4: AMD Multi-Document RAG System
  · Built cross-document retrieval across 3 AMD technical documents
  · Used Query Translation to address Chinese-English retrieval mismatch
  · Added RAGAS evaluation for Faithfulness and Context Precision
  · Built a FastAPI REST API with Redis response caching
  · Reduced repeated-query latency from ~13s to ~5ms on cache hits
  · Containerized with Docker and deployed to Hugging Face Spaces
```

---

## Technical Stack

| Category | Technologies |
|---|---|
| RAG | LangChain, FAISS, BM25, Hybrid Retrieval |
| Agents | LangGraph, LangChain Agent, Tool Calling |
| Protocol | MCP (Model Context Protocol) |
| LLMs | DeepSeek, OpenAI |
| Evaluation | RAGAS, Keyword-based Evaluation |
| Backend | FastAPI, REST API |
| Caching | Redis |
| Observability | LangSmith |
| Deployment | Docker, Hugging Face Spaces |

---

## Project 1–2: RAG Knowledge Bot

**Directory:** `rag-knowledge-bot/`

A foundational RAG implementation developed through two iterations, starting
with a general-purpose document Q&A pipeline and evolving into a
domain-specific RAG system for AMD technical documentation.

### Key Features

- PDF and TXT document ingestion
- Text chunking with configurable chunk size and overlap
- Vector embeddings and FAISS similarity search
- LLM-based question answering
- PDF noise cleaning for technical documentation
- Keyword-based evaluation with a 15-question test set
- Streamlit-based user interface

### Engineering Focus

The project was used to investigate how document preprocessing, chunking
strategies, and retrieval quality affect RAG performance on technical
documentation.

See [`rag-knowledge-bot/README.md`](rag-knowledge-bot/README.md) for details.

---

## Project 3: Bootgen Intelligent Assistant Agent

**Directory:** `bootgen-agent/`

A domain-specific AI Agent for AMD Boot/PDI engineering workflows, built with
LangGraph and designed to combine document retrieval with deterministic
engineering tools.

### Architecture

The Agent integrates four specialized tools:

1. **RAG Search** — retrieves relevant AMD technical documentation
2. **BIF Generator** — generates Boot Image Format (BIF) files
3. **Command Validator** — validates Bootgen command syntax
4. **Device Comparison** — compares device configurations and capabilities

The Agent uses LangGraph to explicitly model the workflow as a state graph,
allowing the LLM to determine when to retrieve information or invoke a
specific tool.

### Key Features

- LangGraph StateGraph-based Agent workflow
- Tool calling and conditional routing
- RAG integration
- Four domain-specific engineering tools
- MCP Server for standardized tool access
- Claude Desktop / MCP-compatible client integration
- LangSmith tracing and observability
- Streamlit-based user interface

### Engineering Focus

The project explores the difference between **open-ended knowledge retrieval**
and **structured engineering tasks**. Instead of relying on RAG for every task,
deterministic tools are used when the task has well-defined inputs and outputs.

See [`bootgen-agent/README.md`](bootgen-agent/README.md) for details.

---

## Project 4: AMD Technical Document Multi-Document Q&A System

**Directory:** `amd-doc-agent/`

A production-oriented multi-document RAG system for AMD FPGA/SoC technical
documentation, developed to address the retrieval limitations identified in
the earlier projects.

### Architecture

The system supports cross-document retrieval across:

- **UG1283** — Chinese technical documentation
- **UG1085** — English technical documentation
- **UG1137** — English technical documentation

The retrieval pipeline combines Query Translation with hybrid retrieval:

**User Query → Query Translation → Bilingual Queries → BM25 + Vector Search → Context Assembly → LLM Generation → Answer + Source Citations**

### Key Features

- Multi-document RAG
- Cross-document retrieval
- BM25 + vector hybrid retrieval
- LLM-based Query Translation
- Multilingual retrieval
- RAGAS evaluation
- Faithfulness and Context Precision metrics
- FastAPI REST API
- Redis response caching
- Docker containerization
- Hugging Face Spaces deployment
- Streamlit web interface

### Evaluation

RAGAS was used to quantitatively evaluate retrieval and generation quality.

Compared with the baseline vector-search implementation:

- **Faithfulness improved by 105%**
- **Context Precision improved by 171%**

These experiments demonstrated the benefits of combining hybrid retrieval
with Query Translation for the multilingual technical-document use case.

### Performance

Redis caching was added to avoid repeating the full retrieval and generation
pipeline for identical queries.

For repeated queries:

| Configuration | Response Time |
|---|---:|
| Full RAG pipeline | ~13 seconds |
| Redis cache hit | ~5 milliseconds |

This represents approximately a **2,600× reduction in response latency on
cache hits**.

🚀 **[Try the Live Demo](https://huggingface.co/spaces/chongyuanz/amd-doc-agent)**

See [`amd-doc-agent/README.md`](amd-doc-agent/README.md) for implementation
details.

---

## Key Engineering Findings

### 1. RAG vs. Deterministic Tools

For structured tasks with well-defined inputs and outputs, such as BIF
generation, command validation, and device comparison, deterministic tools
provide more reliable results than RAG alone.

**RAG is better suited for open-ended technical knowledge retrieval, while
deterministic tools are better suited for structured engineering tasks.**

This led to the Agent architecture used in Project 3, where RAG and
deterministic tools are selected based on task requirements.

---

### 2. Multilingual Retrieval

The AMD knowledge base contains both Chinese and English technical
documentation.

Initial experiments with direct embedding-based retrieval showed a systematic
bias against English document chunks when queries were written in Chinese.

To address this, the final system uses **Query Translation** to generate
English queries alongside the original Chinese query and performs parallel
retrieval across both languages.

This improved cross-language retrieval for the mixed-language knowledge base.

---

### 3. Hybrid Retrieval

Vector search provides strong semantic matching but can be less effective for
technical terminology, identifiers, command names, and exact phrases.

BM25 complements vector search by providing lexical matching.

Combining the two approaches improved retrieval robustness for technical
documentation containing both natural language and domain-specific terms.

---

### 4. RAG Evaluation

Rather than evaluating the system only through manual inspection, RAGAS was
integrated to quantitatively measure:

- **Faithfulness** — whether generated answers are supported by retrieved
  context
- **Context Precision** — whether retrieved context is relevant to the query

This enabled quantitative comparison between retrieval strategies and
provided a basis for iterative optimization.

---

### 5. Caching and Latency

LLM-based RAG pipelines can introduce significant latency because a single
request may involve:

1. Query processing
2. Embedding generation
3. Vector search
4. BM25 search
5. Context assembly
6. LLM inference

Redis caching eliminates these steps for repeated queries, reducing latency
from approximately **13 seconds to 5 milliseconds on cache hits**.

---

## Quick Start

Each project contains its own `README.md` and `requirements.txt`.
See the corresponding directory for detailed setup instructions.

### Projects 1–2

```bash
cd rag-knowledge-bot
pip install -r requirements.txt
streamlit run app.py
```

### Projects 3

```bash
cd bootgen-agent
pip install -r requirements.txt
streamlit run app.py
mcp dev mcp_server.py
```

### Projects 4

```bash
cd amd-doc-agent
pip install -r requirements.txt
streamlit run app.py
uvicorn main:app --reload
```

## Future Improvements
Potential areas for further development include:
- Reranking models for improved retrieval precision
- More comprehensive automated evaluation datasets
- Streaming responses for improved perceived latency
- Persistent conversation memory
- Authentication and access control
- Production-grade monitoring and logging
- More advanced Agent planning and error recovery
