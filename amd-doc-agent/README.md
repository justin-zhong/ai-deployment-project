# 🔍 项目4：AMD 技术文档多文档问答系统

> **项目系列**：[项目1: 基础RAG](../rag-knowledge-bot) → [项目2: 垂直领域RAG](../rag-knowledge-bot) → [项目3: Bootgen Agent](../bootgen-agent) → **项目4: 多文档RAG + 部署（当前）**

基于 RAG（检索增强生成）的多文档知识库问答系统，专为 AMD FPGA/SoC 技术文档设计。在前序项目基础上新增多文档支持、多语言检索、RAGAS 评估框架和云端部署。

🚀 **Live Demo**: [https://huggingface.co/spaces/chongyuanz/amd-doc-agent](https://huggingface.co/spaces/chongyuanz/amd-doc-agent)

## 知识库文档

| 文档 | 内容 | 语言 |
|------|------|------|
| UG1283 | Bootgen 用户指南 | 中文 |
| UG1085 | Zynq UltraScale+ 技术参考手册 | 英文 |
| UG1137 | Zynq UltraScale+ MPSoC 软件开发指南 | 英文 |

三份文档覆盖"硬件架构 → 软件开发 → 镜像生成工具"完整链路，支持跨文档综合查询。

## Demo

> 问：FSBL 的作用是什么？
>
> 答：根据 UG1085，FSBL 执行开始后 CSU ROM 进入后配置阶段，负责系统篡改响应。根据 UG1137，FSBL 直接从 FLASH 设备复制比特流块并执行身份验证。根据 UG1283，FSBL 在启动流程中涉及加密、签名等多个安全阶段。
>
> （信息来自 UG1085、UG1137、UG1283）

## 核心特性

**多文档检索**
三份文档统一向量化存入 FAISS，每个 chunk 打上来源标签（`source`、`filename`），检索时跨文档召回。

**多语言检索（Query Translation）**
中英文混合知识库存在语义匹配偏差——中文问题和中文 chunk 向量天然更近，导致英文文档系统性被忽略。解决方案：检索前用 LLM 将用户问题翻译成英文，同时用中英文两个 query 检索，合并去重后取 top-k，显著提升英文文档的召回率。

**来源标注**
每个 chunk 携带 `metadata["source"]`，Prompt 中要求 LLM 回答时注明来源文档，回答可追溯。

**RAGAS 评估框架**
使用 RAGAS 对系统质量进行量化评估，相比项目2的关键词匹配更能捕捉语义层面的质量问题。

| 指标 | 分数 | 含义 |
|------|------|------|
| Faithfulness | 0.23 | 回答与检索内容的一致性 |
| Context Precision | 0.10 | 检索 chunk 与问题的相关性 |

分数偏低的根本原因在于检索层质量——PDF 噪音清洗后仍有残留，且中文问题与英文文档存在语义匹配偏差。这是后续优化的主要方向。

**云端部署**
Docker 容器化，部署于 Hugging Face Spaces（CPU Free tier），公网可访问。

## 技术栈

- **LangChain** — RAG 框架（文档加载、切分、检索链）
- **OpenAI** — text-embedding-ada-002 向量化
- **DeepSeek** — LLM 生成（成本低，效果好）
- **FAISS** — 本地向量数据库
- **RAGAS** — RAG 系统评估框架
- **Streamlit** — Web UI
- **Docker** — 容器化部署
- **Hugging Face Spaces** — 云端托管

## 快速开始

```bash
# 本地运行
pip install -r requirements.txt
cp .env.example .env
# 填入 OPENAI_API_KEY 和 DEEPSEEK_API_KEY
streamlit run app.py

# Docker 运行
docker build -t amd-doc-agent .
docker run -p 8501:8501 \
  -e OPENAI_API_KEY=your_key \
  -e DEEPSEEK_API_KEY=your_key \
  amd-doc-agent
```

## 项目结构

```
├── data/                  # 三份 AMD 技术文档 PDF
├── src/
│   ├── loader.py          # 多文档加载、噪音清洗、来源标注
│   ├── embedder.py        # 向量化与 FAISS 存储
│   ├── retriever.py       # 相似度检索 + 多语言检索（Query Translation）
│   ├── chain.py           # RAG 链组装（含来源标注 Prompt）
│   ├── evaluator.py       # 关键词匹配评估（基础版）
│   └── evaluator_ragas.py # RAGAS 评估框架（进阶版）
├── app.py                 # Streamlit 入口
├── Dockerfile
├── requirements.txt
└── README.md
```

## 项目演进关系

```
项目1: 基础 RAG
  · 单文档（PDF/TXT）
  · 本地运行
  · 关键词匹配评估
    ↓ 加入垂直领域 + PDF噪音清洗
项目2: AMD Bootgen 专属问答
  · UG1283 单文档
  · PDF噪音清洗（正则）
  · 15题评估模块
    ↓ 加入 Agent + 工具调用
项目3: Bootgen Agent
  · LangChain Agent → LangGraph 重构
  · 4个专属工具（RAG/BIF生成/命令校验/器件对比）
  · MCP Server 封装
    ↓ 加入多文档 + 多语言检索 + RAGAS + 部署
项目4: AMD 多文档问答系统（当前）
  · 3份文档（中英文混合）
  · Query Translation
  · RAGAS 评估
  · Docker + Hugging Face Spaces 部署
```

## 技术挑战与发现

**中英文混合知识库的检索偏差**
使用 OpenAI embedding 时，中文问题和中文 chunk 的向量相似度天然高于英文 chunk，导致英文文档被系统性忽略。通过 Query Translation 在检索前将问题翻译为英文，实现双语并行检索，有效解决了这一问题。

**PDF 噪音对检索质量的影响**
技术文档的页眉、页脚、页码会污染向量空间，使不相关 chunk 的向量距离被人为拉近。通过正则清洗 + 跳过封面目录页，将 chunk 数量从原始的 ~2000 降至 1792，检索区分度明显提升。

**评估框架的演进**
项目2使用关键词匹配评估，简单但无法捕捉语义层面的质量问题。项目4引入 RAGAS，通过 Faithfulness 和 Context Precision 等指标量化评估，发现检索层是主要瓶颈，为后续优化指明方向。

## 已知局限与后续方向

- 英文文档的表格、多栏布局解析质量有限
- Query Translation 增加了一次额外的 LLM 调用，响应时间略有增加
- RAGAS 的 Answer Relevancy 指标与 DeepSeek API 存在兼容性问题（`n>1` 不支持）
- 可扩展至更多 AMD 文档（AM011、UG1304 等），建议届时替换为 Pinecone 等云端向量库
- 可引入 Re-ranking 模型对检索结果重排序，进一步提升准确率