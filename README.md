**English** | [中文](README_CN.md)

# AI / LLM Application Engineering Portfolio

Hands-on AI application engineering projects built around AMD FPGA/SoC
technical domains, covering **RAG, Agents, MCP, retrieval optimization, evaluation, API development, caching, and deployment**.

The portfolio demonstrates an end-to-end progression from foundational RAG
pipelines to a domain-specific Agent and a deployed multi-document RAG
system.

🚀 **[Live Demo — AMD Technical Document RAG System](https://huggingface.co/spaces/chongyuanz/amd-doc-agent)**

---

## Projects

| Project | Directory | Core Technologies | Highlights |
|---|---|---|---|
| Projects 1–2 | `rag-knowledge-bot/` | RAG, FAISS, LangChain | Chunking experiments, PDF noise cleaning, evaluation |
| Project 3 | `bootgen-agent/` | LangGraph, MCP, LangSmith | 4-tool Agent, MCP Server, end-to-end tracing |
| Project 4 | `amd-doc-agent/` | Multi-document RAG, FastAPI, Redis | Query Translation, RAGAS evaluation, Hugging Face deployment |

---

## Engineering Focus
This portfolio demonstrates practical experience in:

- Building and evaluating RAG systems
- Designing tool-using LLM Agents
- Optimizing retrieval quality with hybrid search and Query Translation
- Exposing AI systems through REST APIs
- Improving application latency with caching
- Containerizing and deploying AI applications

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
  · Migrated from a LangChain Agent to a LangGraph StateGraph, making the agent workflow explicit and state-driven
  · Built 4 specialized tools:
      RAG Search / BIF Generation / Command Validation / Device Comparison
  · Exposed tools through an MCP Server
  · Integrated LangSmith for end-to-end agent tracing
    ↓
Project 4: AMD Multi-Document RAG System
  · Extended the domain RAG system to 3 AMD technical documents
  · Added Query Translation to address Chinese-English retrieval mismatch
  · Added BM25 hybrid retrieval to improve technical-term matching
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

See [`rag-knowledge-bot/README.md`](rag-knowledge-bot/README.md) for details.

---

## Project 3: Bootgen Intelligent Assistant Agent

**Directory:** `bootgen-agent/`

A domain-specific AI Agent for AMD Boot/PDI engineering workflows, built with
LangGraph and designed to combine document retrieval with deterministic
engineering tools.

See [`bootgen-agent/README.md`](bootgen-agent/README.md) for details.

---

## Project 4: AMD Technical Document Multi-Document Q&A System

**Directory:** `amd-doc-agent/`

An end-to-end multi-document RAG system for AMD FPGA/SoC technical documentation,
developed to address retrieval limitations identified through the earlier RAG projects, with hybrid retrieval, multilingual query translation, and quantitative evaluation.

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

Initial experiments with direct embedding-based retrieval showed a retrieval
bias against English document chunks when queries were written in Chinese.

To address this, the final system uses **Query Translation** to generate
English queries alongside the original Chinese query and performs parallel
retrieval across both languages.

This improved cross-language retrieval for the mixed-language knowledge base.

---

### 3. Hybrid Retrieval

Vector search provides strong semantic matching but can be less effective for
technical terminology, identifiers, command names, and exact phrases.

BM25 complements vector search by providing lexical matching for technical
terminology, identifiers, command names, and exact phrases.

In the evaluation set, adding BM25 on top of Query Translation substantially
improved Faithfulness and Context Precision.

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
