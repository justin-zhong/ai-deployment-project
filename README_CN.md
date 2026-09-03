[English](README.md) | **中文**

# AI/LLM 应用工程实践项目

围绕 AMD FPGA/SoC 技术领域开展的 LLM 应用工程实践，涵盖 **RAG、LLM Agent、MCP、检索优化、系统评估、API 开发、缓存与云端部署**。

项目从基础 RAG 流程逐步演进至领域专属 Agent 和多文档 RAG 系统，覆盖从原型开发、检索优化、效果评估到服务部署的完整工程流程。

🚀 **Live Demo（项目4）**：[https://huggingface.co/spaces/chongyuanz/amd-doc-agent](https://huggingface.co/spaces/chongyuanz/amd-doc-agent)

## 项目概览

| 项目 | 目录 | 核心技术 | 亮点 |
|------|------|---------|------|
| 项目1+2 | `rag-knowledge-bot/` | RAG、FAISS、LangChain | chunk调优、PDF噪音清洗、15题评估模块 |
| 项目3 | `bootgen-agent/` | LangGraph、MCP、LangSmith | 4工具Agent、MCP Server、链路追踪 |
| 项目4 | `amd-doc-agent/` | 多文档RAG、FastAPI、Redis | Query Translation、RAGAS评估、Hugging Face部署 |

---

## 工程能力
本项目主要体现以下 AI 应用工程能力:

- 构建与评估 RAG 系统
- 设计支持工具调用的 LLM Agent
- 使用混合检索与 Query Translation 优化检索效果
- 通过 REST API 对外提供 AI 服务
- 使用缓存降低应用延迟
- 使用 Docker 完成 AI 应用容器化与部署

## 项目演进

```
项目1: 基础 RAG
  · 单文档（PDF/TXT）问答，验证完整 RAG 流程
  · chunk_size/overlap 参数调优实验
    ↓
项目2: 垂直领域 RAG（AMD UG1283）
  · PDF 噪音清洗（页眉/页脚/页码正则过滤）
  · 15道测试题 + 关键词匹配评估模块
  · 系统分析技术文档 RAG 的检索局限性
    ↓
项目3: Bootgen 智能助手 Agent
  · LangChain Agent → LangGraph StateGraph 重构，将 Agent 工作流显式建模为状态图
  · 4个专属工具：RAG检索 / BIF生成 / 命令校验 / 器件对比
  · MCP Server 封装，支持 Claude Desktop 等客户端调用
  · LangSmith 集成，Agent 链路完整可观测
    ↓
项目4: AMD 多文档问答系统（已部署）
  · Extended the domain RAG system to 3 AMD technical documents with hybrid retrieval and multilingual query translation
  · Query Translation 解决中英文检索偏差
  · RAGAS 评估框架（Faithfulness / Context Precision）
  · FastAPI RESTful API + Redis 缓存（响应从13s降至0.005s）
  · Docker 容器化，部署至 Hugging Face Spaces
```

---

## 技术栈

| 类别 | 技术 |
|---|---|
| RAG | LangChain、FAISS、BM25、Hybrid Retrieval |
| Agent | LangGraph、LangChain Agent、Tool Calling |
| 工具协议 | MCP（Model Context Protocol） |
| LLM | DeepSeek、OpenAI |
| 评估 | RAGAS、关键词匹配评估 |
| 后端 | FastAPI、REST API |
| 缓存 | Redis |
| 可观测性 | LangSmith |
| 部署 | Docker、Hugging Face Spaces |

---

## 项目1–2：RAG 知识库

**目录：** `rag-knowledge-bot/`

从通用文档问答逐步演进至 AMD 技术文档领域的 RAG 系统，重点探索文档清洗、Chunk 策略及技术文档场景下的检索问题。

详见 [`rag-knowledge-bot/README.md`](rag-knowledge-bot/README.md)。

---

## 项目3：Bootgen 智能助手 Agent

**目录：** `bootgen-agent/`

基于 LangGraph 构建的领域专属 Agent，将技术文档检索与 BIF 生成、命令校验、器件对比等确定性工程工具结合，实现多工具协同调用。

详见 [`bootgen-agent/README.md`](bootgen-agent/README.md)。

---

## 项目4：AMD 技术文档多文档问答系统

**目录：** `amd-doc-agent/`

面向 AMD FPGA/SoC 技术文档构建的多文档 RAG 系统，在前序项目发现的检索问题基础上，引入混合检索、多语言 Query Translation、RAGAS 评估、FastAPI、Redis 缓存及 Docker 部署。

详见 [`amd-doc-agent/README.md`](amd-doc-agent/README.md)。

---

## 关键工程发现

### 1. RAG 与确定性工具

对于 BIF 生成、命令校验、器件对比等具有明确输入输出的结构化任务，确定性工具比纯 RAG 检索具有更高的可靠性。

**RAG 更适合开放性的技术知识检索，而确定性工具更适合输入输出明确的结构化工程任务。**

这一发现直接推动了项目3的 Agent 架构设计：由 Agent 根据任务类型选择 RAG 检索或确定性工具。

---

### 2. 中英文混合知识库的检索偏差

知识库同时包含中文和英文技术文档。

初始实验发现，当用户使用中文提问时，直接基于 Embedding 的检索会更容易召回中文 Chunk，而英文文档可能被系统性忽略。

因此，项目4引入 **Query Translation**：在保留原始 Query 的同时生成英文 Query，对两个 Query 并行检索并合并结果，从而提升混合语言知识库的跨语言检索效果。

---

### 3. 混合检索

纯向量检索擅长语义匹配，但对于技术术语、寄存器名称、命令参数和精确短语等内容，检索效果可能不稳定。

BM25 提供基于关键词的词法匹配能力，与向量检索形成互补。

将两种方法结合后，可以提高技术文档场景下的检索鲁棒性。

---

### 4. RAG 系统评估

除了人工查看回答结果外，项目4引入 **RAGAS** 对系统进行量化评估，包括：

- **Faithfulness**：生成回答是否得到检索上下文的支持
- **Context Precision**：检索到的上下文是否与用户问题相关

通过量化指标对不同检索策略进行比较，为后续优化提供依据。

---

### 5. 缓存与延迟

一次完整的 RAG 请求通常包括：

1. Query 处理
2. Embedding
3. 向量检索
4. BM25 检索
5. Context 构建
6. LLM 推理

对于重复请求，Redis 缓存可以直接跳过上述流程。

在测试中，相同问题的响应时间从约 **13 秒降低至约 5 毫秒**。

