[English](README.md) | [中文](README_CN.md)

# LLM Application Engineering Projects

AMD FPGA/SoC 技术背景下的 AI 应用工程实践，涵盖 RAG、LangGraph Agent、MCP、FastAPI、Redis 缓存和云端部署。四个项目递进式构建，从基础 RAG 到生产级多文档问答系统。

## 项目概览

| 项目 | 目录 | 核心技术 | 亮点 |
|------|------|---------|------|
| 项目1+2 | `rag-knowledge-bot/` | RAG、FAISS、LangChain | chunk调优、PDF噪音清洗、15题评估模块 |
| 项目3 | `bootgen-agent/` | LangGraph、MCP、LangSmith | 4工具Agent、MCP Server、链路追踪 |
| 项目4 | `amd-doc-agent/` | 多文档RAG、FastAPI、Redis | Query Translation、RAGAS评估、Hugging Face部署 |

🚀 **Live Demo（项目4）**：[https://huggingface.co/spaces/chongyuanz/amd-doc-agent](https://huggingface.co/spaces/chongyuanz/amd-doc-agent)

---

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
  · LangChain Agent → LangGraph 重构（黑盒→状态图）
  · 4个专属工具：RAG检索 / BIF生成 / 命令校验 / 器件对比
  · MCP Server 封装，支持 Claude Desktop 等客户端调用
  · LangSmith 集成，Agent 链路完整可观测
    ↓
项目4: AMD 多文档问答系统（已部署）
  · 3份文档（UG1283中文 + UG1085/UG1137英文）跨文档检索
  · Query Translation 解决中英文检索偏差
  · RAGAS 评估框架（Faithfulness / Context Precision）
  · FastAPI RESTful API + Redis 缓存（响应从13s降至0.005s）
  · Docker 容器化，部署至 Hugging Face Spaces
```

---

## 技术栈总览

| 类别 | 技术 |
|------|------|
| RAG 框架 | LangChain、FAISS |
| Agent 框架 | LangGraph、LangChain Agent |
| 工具协议 | MCP（Model Context Protocol） |
| LLM | DeepSeek、OpenAI |
| 评估 | RAGAS、关键词匹配 |
| 后端 | FastAPI |
| 缓存 | Redis |
| 可观测性 | LangSmith |
| 部署 | Docker、Hugging Face Spaces |

---

## 快速开始

每个子项目有独立的 `README.md` 和 `requirements.txt`，进入对应目录查看详细说明：

```bash
# 项目1+2
cd rag-knowledge-bot && pip install -r requirements.txt
streamlit run app.py

# 项目3
cd bootgen-agent && pip install -r requirements.txt
streamlit run app.py          # Streamlit UI
mcp dev mcp_server.py         # MCP Server

# 项目4
cd amd-doc-agent && pip install -r requirements.txt
streamlit run app.py          # Streamlit UI
uvicorn main:app --reload     # FastAPI
```

所有项目需要配置 `.env` 文件，参考各目录下的 `.env.example`。

---

## 关键技术发现

**RAG vs Agent**
对于有明确输入输出的结构化任务（BIF生成、命令校验、器件对比），确定性工具的效果远好于 RAG 检索。RAG 适合开放性文档查询，工具适合结构化任务。

**中英文混合知识库**
OpenAI embedding 对中文问题和英文 chunk 的向量距离天然偏大，导致英文文档被系统性忽略。通过 Query Translation 双语并行检索有效解决。

**Redis 缓存效果**
相同问题的响应时间从 13 秒（RAG 全流程）降至 0.005 秒（缓存命中），提升约 2600 倍。
