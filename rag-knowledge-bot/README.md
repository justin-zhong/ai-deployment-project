# 📚 个人知识库问答机器人

基于 RAG（检索增强生成）的本地知识库问答系统。将 PDF/TXT 文档向量化存入本地数据库，支持用自然语言提问并获得有据可查的回答。

## Demo

> 问：最常用的文本切分器是什么？
>
> 答：最常用的文本切分器是 RecursiveCharacterTextSplitter。它按照段落、句子、字符的优先级递归切分，并支持通过 chunk_overlap 保证相邻片段之间的语义连贯性。

## 技术栈

- **LangChain** — RAG 框架（文档加载、切分、检索链）
- **OpenAI** — text-embedding-ada-002 向量化 + GPT-4o-mini 生成
- **FAISS** — 本地向量数据库，支持持久化
- **Streamlit** — Web UI

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key
cp .env.example .env
# 编辑 .env，填入你的 OPENAI_API_KEY

# 3. 放入文档（支持 PDF、TXT）
cp your_docs.pdf data/

# 4. 启动
streamlit run app.py
```

启动后在左侧点击「加载并索引文档」，完成后即可在右侧提问。

## 项目结构

```
├── data/               # 放你的文档（PDF、TXT）
├── src/
│   ├── loader.py       # 文档加载与 chunk 切分
│   ├── embedder.py     # 向量化与 FAISS 存储
│   ├── retriever.py    # 相似度检索
│   └── chain.py        # RAG 链组装（Prompt + LLM）
├── app.py              # Streamlit 入口
├── vectorstore/        # 向量库持久化（自动生成）
└── requirements.txt
```

## RAG 工作流程

```
【离线索引】
文档（PDF/TXT）→ 切分 chunk → Embedding 向量化 → 存入 FAISS

【在线查询】
用户提问 → Embedding 向量化 → FAISS 相似度检索 → top-k chunk
                                                        ↓
                                           拼入 Prompt → LLM → 回答
```

## 参数调优记录

在开发过程中，通过实验发现 chunk 切分参数对检索质量影响显著。以下是针对同一问题（"调试技巧有哪些？"）在不同参数下的表现：

| chunk_size | chunk_overlap | 结果 |
|-----------|--------------|------|
| 500 | 50 | ❌ 回答"没有找到相关信息" |
| 500 | 150 | ✅ 能回答，但内容不完整（2/3条） |
| 800 | 100 | ✅ 回答完整，并能主动关联相关内容 |

**结论：** chunk_size 影响语义完整性，chunk_overlap 是补救边界截断的手段。优先保证单个 chunk 能装下一个完整的语义单元，overlap 只用于减少边界损失。本项目最终采用 `chunk_size=800, chunk_overlap=100`。

**调试方法：** 通过 `retriever.py` 中的 `search()` 函数直接打印检索结果，可以快速判断问题出在检索层还是生成层，避免盲目调整 Prompt。

## 已知局限

- 仅支持文本内容，PDF 中的图表、表格暂不处理
- 向量化使用 OpenAI API，需要联网和费用
- 适合中小规模文档（数十份），大规模场景建议替换为 Pinecone 等云端向量库
