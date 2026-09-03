---
title: AMD Doc Agent
emoji: 🤖
colorFrom: red
colorTo: blue
sdk: docker
pinned: false
---

[English](README.md) | **中文**

# 🔍 项目4：AMD 技术文档多文档问答系统

面向 AMD FPGA/SoC 技术文档的多文档 RAG（检索增强生成）问答系统。在前序项目基础上，进一步引入 **BM25 + 向量混合检索、多语言 Query Translation、RAGAS 评估、FastAPI 后端、Redis 缓存以及 Docker 云端部署**，重点解决多文档场景下的跨语言检索偏差、检索质量和系统性能问题

🚀 **Live Demo:** [AMD Doc Agent](https://huggingface.co/spaces/chongyuanz/amd-doc-agent)

![Screenshot of demo](images/demo.png)

## 工程亮点

- **Hybrid Retrieval:** 结合 FAISS 语义检索与 BM25 关键词检索，提升技术术语、标识符和精确短语的检索效果
- **Multilingual Retrieval:** 通过基于 LLM 的 Query Translation 改善中英文技术文档之间的跨语言检索效果
- **Evaluation:** 使用 RAGAS 对不同检索策略进行对比，并量化评估 Faithfulness 和 Context Precision
- **Performance:** 引入 Redis 缓存，将重复查询的响应延迟从约 13 秒降低至约 0.005 秒
- **Productionization:** 通过 FastAPI 暴露 RAG Pipeline，并使用 Docker Compose 完成应用容器化部署
- **Source Attribution:** 在检索和生成过程中保留文档 metadata，使生成答案能够追溯至对应来源文档

## 架构与部署
                    ┌─────────────────┐
                    │   Streamlit UI  │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     FastAPI     │
                    │      /ask       │
                    └────────┬────────┘
                             │
                       ┌─────▼─────┐
                       │   Redis   │
                       │   Cache   │
                       └─────┬─────┘
                             │ miss
                             ▼
                    ┌─────────────────┐
                    │ Query Processing│
                    │   Translation   │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
          ┌───────────┐             ┌───────────┐
          │   FAISS   │             │   BM25    │
          │ Semantic  │             │  Keyword  │
          └─────┬─────┘             └─────┬─────┘
                └────────────┬────────────┘
                             ▼
                  ┌─────────────────────┐
                  │  LLM Generation     │
                  │+ Source Attribution │
                  └─────────────────────┘

Docker Compose
```
├── Streamlit :8501
├── FastAPI   :8000
└── Redis     :6379
```

## 知识库文档

| 文档 | 内容 | 语言 |
|------|------|------|
| UG1283 | Bootgen 用户指南 | 中文 |
| UG1085 | Zynq UltraScale+ 技术参考手册 | 英文 |
| UG1137 | Zynq UltraScale+ MPSoC 软件开发指南 | 英文 |

三份文档覆盖 **硬件架构** → **软件开发** → **Bootgen 镜像生成** 等相关技术内容，构成中英文混合的多文档知识库，支持跨文档综合查询。

## Demo

> **问**：FSBL 的作用是什么？
>
> **答**：根据 UG1085，FSBL 执行开始后 CSU ROM 进入后配置阶段，负责系统篡改响应。根据 UG1137，FSBL 直接从 FLASH 设备复制比特流块并执行身份验证。根据 UG1283，FSBL 在启动流程中涉及加密、签名等多个安全阶段。
>
> *（信息来自 UG1085、UG1137、UG1283）*

## 核心特性

**多文档检索**
三份技术文档统一进行向量化并存入 FAISS。每个 chunk 保留 `source`、`filename` 等文档 metadata，使检索器能够在多个文档之间进行统一检索，同时保留文档来源信息

**多语言检索（Query Translation）**
中英文混合知识库存在跨语言检索偏差：中文问题更容易与中文 chunk 产生较高的 embedding 相似度，使英文文档存在被低估的风险

为缓解这一问题，系统在检索前使用 LLM 将用户问题转换为英文 Query，并使用原始 Query 和英文 Query 分别进行检索，再对结果进行合并、去重并选取最终 Top-k chunks，从而改善中文问题对英文技术文档的召回效果

**来源标注（Source Attribution）**
每个 chunk 保留 `metadata["source"]` 等来源信息。检索后的 metadata 会沿 RAG Pipeline 传递至生成阶段，并用于关联回答所依据的源文档，使生成结果具备可追溯性

**FastAPI 后端**
除 Streamlit UI 外，系统还通过 FastAPI 提供 RESTful API，便于与其他应用集成。`/ask` 接口返回 `answer`、`question` 和 `sources`，并通过中间件记录请求响应时间

**Redis 缓存**
对于重复查询，系统可直接从 Redis 返回缓存结果，避免再次执行完整的 RAG Pipeline。测试中，缓存命中时响应延迟从**约 13 秒降低至约 0.005 秒（5 毫秒）**

缓存 key 会对 Query 进行标准化处理，包括转为小写和移除空白字符，从而减少因大小写或空白差异导致的不必要缓存未命中

**RAGAS 评估框架**
使用 RAGAS 对系统质量进行量化评估。相比项目 2 的关键词匹配评估，RAGAS 能够从语义层面对生成结果和检索上下文进行评价

| 检索策略 | Faithfulness | Answer Relevancy | Context Precision |
|---|---:|---:|---:|
| Vector + Query Translation | 0.39 | 0.54 | 0.06 |
| Vector + BM25 + Query Translation | 0.80 | 0.50 | 0.16 |

在评估集上，引入 BM25 混合检索后，**Faithfulness 提升 105%，Context Precision 提升 171%**。这表明 BM25 与向量检索具有互补性，能够改善技术文档场景下的检索质量

当前评估中的低分主要来自检索层：PDF 预处理后仍存在部分格式噪声，同时中文 Query 与英文技术文档之间仍存在一定语义匹配偏差。这些问题也是后续优化的重点

> **注：** Answer Relevancy 当前受到 DeepSeek 配置与 RAGAS 评估器/API 兼容性的限制，因此该指标不作为本次检索策略比较的主要依据

**云端部署**
应用通过 Docker Compose 完成容器化，包含 Streamlit、FastAPI 和 Redis 三个服务，并部署至 Hugging Face Spaces（CPU Free tier），提供公网访问

## 技术栈

- **LangChain** — RAG 框架（文档加载、切分、检索链）
- **Hugging Face / Sentence Transformers** — `all-MiniLM-L6-v2` 向量化
- **DeepSeek** — LLM 生成
- **FAISS** — 向量检索
- **BM25** — 关键词检索
- **RAGAS** — RAG 系统评估框架
- **FastAPI** — RESTful API 后端
- **Redis** — 响应缓存
- **Streamlit** — Web UI
- **Docker** — 容器化部署
- **Hugging Face Spaces** — 云端托管

## 快速开始

### API 示例

```bash
curl -X POST "http://localhost:8000/ask" \
  -H "Content-Type: application/json" \
  -d '{"question":"What is Bootgen?"}'
```

示例响应：
```json
{
  "answer": "...",
  "question": "What is Bootgen?",
  "sources": ["UG1085", "UG1137"]
}  
```

### Docker Compose 运行完整应用
```bash
docker compose up --build
```
Streamlit: http://localhost:8501
FastAPI:   http://localhost:8000/docs

### 本地开发
Streamlit 和 FastAPI 应用也可以分别运行。FastAPI 的 Redis 缓存功能需要本地 Redis 服务正常运行
```bash
docker run -d -p 6379:6379 redis
```

### 本地运行 Streamlit

```bash
pip install -r requirements.txt
cp .env.example .env
```
在 .env 中设置 `DEEPSEEK_API_KEY`。请勿将 .env 提交至 Git 仓库

```bash
streamlit run app.py
```

### 本地运行 FastAPI
```bash
uvicorn main:app --reload
```
访问 http://localhost:8000/docs 查看交互式 API 文档

## 项目结构

```
├── data/                  # 三份 AMD 技术文档 PDF
├── images/
├── src/
│   ├── loader.py          # 多文档加载、噪音清洗、来源标注
│   ├── embedder.py        # 向量化与 FAISS 存储
│   ├── retriever.py       # 相似度检索 + 多语言检索（Query Translation）
│   ├── chain.py           # RAG 链组装（含来源标注 Prompt）
│   ├── evaluator.py       # 关键词匹配评估（基础版）
│   └── evaluator_ragas.py # RAGAS 评估框架（进阶版）
├── main.py                # FastAPI 入口（RESTful API + Redis 缓存）
├── cache.py               # Redis 缓存逻辑
├── app.py                 # Streamlit 入口
├── Dockerfile
├── Dockerfile.api
├── docker-compose.yml
├── requirements.txt
├── requirements-eval.txt
├── README_CN.md
├── .env.example
├── .dockerignore
└── README.md
```

## 项目演进

项目 1 → Basic RAG
      ↓
项目 2 → AMD Bootgen RAG
      ↓
项目 3 → Bootgen Agent / LangGraph / MCP
      ↓
项目 4 → Multi-document RAG / Hybrid Retrieval /
            Evaluation / API / Deployment

> **项目系列**：[项目1+2: RAG知识库](../rag-knowledge-bot) → [项目3: Bootgen Agent](../bootgen-agent) → **项目4: 多文档RAG + 部署（当前）**

## 已知局限

- 表格和多栏布局的文档解析质量仍然有限
- Query Translation 增加了一次额外的 LLM 调用和响应延迟
- Answer Relevancy 的评估受到当前 DeepSeek 配置的兼容性限制

## 后续改进

- 扩展知识库，加入更多 AMD 技术文档
- 引入 Re-ranking 阶段，进一步提升检索精度
- 随着文档规模增长，评估使用托管式向量数据库
