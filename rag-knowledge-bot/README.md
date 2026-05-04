# 📚 项目3：AMD Bootgen 技术文档问答机器人

基于 RAG（检索增强生成）的垂直领域知识库问答系统，专为 AMD FPGA/SoC 技术文档设计。当前知识库基于 UG1283 Bootgen 用户指南（2025.2），支持用自然语言查询启动镜像生成、BIF 语法、加密认证等技术问题。

## Demo

> 问：authentication 在引导中的角色是什么？
>
> 答：认证（authentication）在引导过程中用于确保分区（包括报头表）的完整性和来源可信性。具体通过为分区启用身份验证并指定 PPK（主公钥）实现，分区使用 SSK 来签名，签名填充到 AC 中，PPK 将散列化并存储在 eFUSE 中。

> 问：如何在命令行使用 bootgen？
>
> 答：在命令行中使用 Bootgen 的基本语法为 `bootgen -arch <架构> -image <bif文件> -o <输出文件>`，例如 `bootgen -arch zynqmp -image test.bif -w -o boot.bin`。

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
├── data/               # 知识库文档（当前：UG1283 Bootgen 用户指南）
├── src/
│   ├── loader.py       # 文档加载、PDF 噪音清洗与 chunk 切分
│   ├── embedder.py     # 向量化与 FAISS 存储
│   ├── retriever.py    # 相似度检索
│   ├── chain.py        # RAG 链组装（Prompt + LLM）
│   └── evaluator.py    # 自动评估模块（15道测试题 + 关键词匹配评分）
├── app.py              # Streamlit 入口（含评估面板）
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

## 技术文档 RAG 的挑战与发现

将通用 RAG 系统迁移到 AMD UG1283 等专业技术文档时，遇到了以下问题并逐一排查：

| 问题 | 根本原因 | 解决方案 | 结果 |
|------|---------|---------|------|
| 大量内容检索失败 | PDF 页眉页脚噪音（页码、文档编号、"Send Feedback"）混入 chunk | 正则清洗三类噪音模式 + 跳过前6页封面目录 | chunk 从 636 降至 559，噪音显著减少 |
| 部分内容仍检索不到 | chunk 跨越多个主题，语义被稀释 | 调整 chunk_size/overlap | 部分改善 |
| 评估准确率偏低 | 用户问题措辞与文档术语风格不匹配 | 缩短问题、贴近文档原文术语 | 有所改善，但仍有差距 |
| 检索区分度差 | 残留页脚（"附录A/B/C"、章节标题）反复出现，拉近了不相关 chunk 的向量距离 | — | 待解决 |

**核心发现：** 技术文档 RAG 的瓶颈不在 LLM，而在数据质量和检索层。噪音清洗、chunk 策略、问题改写（Query Rewriting）对最终效果的影响远大于更换更强的模型。

**下一步方向：** 考虑引入 Query Rewriting——在检索前用 LLM 将用户的自然语言问题改写为更贴近文档术语风格的检索 query，以提升召回率。

## 已知局限

- PDF 中的图表、多栏表格解析质量有限，部分内容可能丢失语义
- 向量化使用 OpenAI API，需要联网和费用
- 当前知识库仅含 UG1283，扩展多文档时建议替换为 Pinecone 等云端向量库
- 检索区分度受残留页脚影响，考虑改用网页版文档加载（WebBaseLoader）以获得更干净的文本
