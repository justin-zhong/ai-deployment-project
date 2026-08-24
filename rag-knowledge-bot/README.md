**English** | [中文](README_CN.md)

# 📚 Project 1 + Project 2: AMD Bootgen Technical Document Q&A Bot

> **Project Series:** **Projects 1–2: RAG Knowledge Base (Current)** → [Project 3: Bootgen Agent](../bootgen-agent) → [Project 4: Multi-Document RAG + Deployment](../amd-doc-agent)

A domain-specific RAG (Retrieval-Augmented Generation) knowledge base designed for AMD FPGA/SoC technical documentation. The current knowledge base is based on the UG1283 Bootgen User Guide (2025.2) and supports natural-language queries about boot image generation, BIF syntax, encryption, authentication, and other Bootgen-related topics.

- **Project 1:** Built a general-purpose RAG pipeline to validate the end-to-end retrieval and generation workflow and experiment with chunking parameters.
- **Project 2:** Applied the RAG pipeline to the real-world UG1283 technical documentation, adding PDF noise cleaning and an evaluation module to systematically analyze the limitations of RAG for technical documentation.

## Demo

> **Q:** What role does authentication play during the boot process?
>
> **A:** Authentication ensures the integrity and authenticity of partitions, including the header table, during the boot process. It is enabled by configuring authentication for partitions and specifying a PPK (Primary Public Key). Partitions are signed using an SSK, with the signature stored in the Authentication Certificate (AC), while the hash of the PPK is stored in eFUSE.

> **Q:** How do I use Bootgen from the command line?
>
> **A:** The basic Bootgen command-line syntax is `bootgen -arch <architecture> -image <bif_file> -o <output_file>`. For example: `bootgen -arch zynqmp -image test.bif -w -o boot.bin`.

## Tech Stack

- **Hugging Face / Sentence Transformers** — `all-MiniLM-L6-v2` local embeddings
- **DeepSeek** — LLM generation
- **FAISS** — Local vector store with persistence support
- **Streamlit** — Web UI

## Quick Start

### 1. Create a virtual environment

It is recommended to use Python `3.10`-`3.12` to create individual virtual environments:

```bash
python -m venv .venv
```
Windows
```bash
.venv\Scripts\activate
```
macOS / Linux
```bash
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```
The project runs on CPU by default. For NVIDIA GPUs, install a PyTorch build compatible with your CUDA/driver environment.

For example, this project has been verified in an NVIDIA GeForce GTX 1050 + CUDA 12.6 PyTorch build environment:
```bash
pip install torch==2.13.0 --index-url https://download.pytorch.org/whl/cu126
```

Verify GPU availability:
```bash
python -c "import torch; print(torch.__version__); print(torch.cuda.is_available())"
```

### 3. Configure API key
```bash
cp .env.example .env
```
Edit .env and add your OPENAI_API_KEY

### 4. Add documents (PDF or TXT)
```bash
cp your_docs.pdf data/
```
### 5. Start the application
```bash
streamlit run app.py
```

After starting the application, click "Load & Index Documents" in the
sidebar. Once indexing is complete, you can ask questions through the chat
interface.

## Project Structure

```
├── data/               # Knowledge base documents (currently UG1283 Bootgen User Guide)
├── src/
│   ├── loader.py       # Document loading, PDF noise cleaning, and chunking
│   ├── embedder.py     # Embedding generation and FAISS storage
│   ├── retriever.py    # Similarity search
│   ├── chain.py        # RAG chain assembly (Prompt + LLM)
│   └── evaluator.py    # Automated evaluation (10 test questions + keyword matching)
├── app.py              # Streamlit entry point with evaluation dashboard
├── vectorstore/        # Persisted vector store (automatically generated)
└── requirements.txt
```

## RAG Workflow

```
【Offline Indexing】
Document (PDF/TXT)
        ↓
Chunking
        ↓
Embedding Generation
        ↓
FAISS Vector Store

【Online Query】
User Query
    ↓
Query Embedding
    ↓
FAISS Similarity Search
    ↓
Top-k Chunks
    ↓
Prompt Construction
    ↓
LLM
    ↓
Answer
```

## Chunking Parameter Experiments

During development, experiments showed that chunking parameters have a
significant impact on retrieval quality. The following results were obtained
for the same question, "What are the debugging techniques?", using
different chunking configurations:

| chunk_size | chunk_overlap | Result |
|-----------|--------------|------|
| 500 | 50 | ❌ Failed to retrieve relevant information |
| 500 | 150 | ✅ Answered the question, but incompletely (2 of 3 items) |
| 800 | 100 | ✅ Complete answer with relevant related information |

**Conclusion:** chunk_size primarily affects semantic completeness, while
chunk_overlap helps reduce information loss at chunk boundaries. The
preferred approach is to ensure that each chunk contains a complete semantic
unit and use overlap to mitigate boundary truncation.

The final configuration for this project is:

```text
chunk_size = 800
chunk_overlap = 100
```

**Debugging approach:** The search() function in retriever.py can be used
to directly inspect retrieved chunks. This makes it possible to quickly
determine whether an issue originates from the retrieval or generation layer,
rather than blindly modifying the prompt.

## Challenges and Findings with Technical Document RAG

When adapting the general-purpose RAG system to specialized technical
documentation such as AMD UG1283, several issues were identified and
investigated:

| Issue | Root Cause | Solution | Result |
|------|---------|---------|------|
| Large amount of content could not be retrieved | PDF headers, footers, page numbers, document IDs, and "Send Feedback" text were included in chunks | Used regex-based cleaning for three types of PDF noise and skipped the first 6 cover/table-of-contents pages | Reduced chunks from 636 to 559 and significantly reduced noise |
| Some content was still difficult to retrieve | Chunks covered multiple topics, diluting their semantic meaning | Adjusted chunk_size and chunk_overlap | Partial improvement |
| Low evaluation accuracy | User questions did not match the terminology and writing style of the documentation | Shortened questions and aligned them more closely with document terminology | Some improvement, but gaps remained |
| Poor retrieval discrimination | Repeated residual footer text reduced the distinction between relevant and irrelevant chunks | — | Partially addressed in Project 4 with Query Translation |

**Key Finding:** For technical-document RAG, the primary bottleneck is often not the LLM, but
data quality and the retrieval layer.

PDF noise cleaning, chunking strategy, and query formulation had a much larger
impact on retrieval quality than simply switching to a more capable LLM.

**Further Development:** Project 4 introduced Query Translation to address the multilingual
retrieval problem. Before retrieval, an LLM translates the user's query into
English, allowing the system to perform parallel Chinese and English
retrieval and merge the results. See the [Project 4 README](../amd-doc-agent) for details.

## Known Limitations

- PDF charts and multi-column tables may not be parsed correctly, which can
result in partial loss of semantic information.
- LLM generation uses the DeepSeek API, requiring network access and incurring API costs. 
Embeddings are generated locally using Sentence Transformers.
- The current knowledge base contains only UG1283. For larger multi-document
deployments, a managed vector database such as Pinecone could be considered.
- Retrieval quality can still be affected by residual PDF footer text.
Loading documentation from web-based sources such as WebBaseLoader could
provide cleaner source text.
