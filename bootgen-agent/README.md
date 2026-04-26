# 🤖 Bootgen 智能助手 Agent

基于 LangChain Agent 的 AMD Bootgen 专属助手，是[RAG 知识库问答项目](../rag-knowledge-bot)的进阶版本。相比纯 RAG 方案，Agent 能主动决策调用哪个工具、按需链式执行多步操作，对结构化任务（BIF 生成、命令校验、器件对比）的回答质量显著优于检索方式。

## Demo

> 用户：帮我为 zynqmp 生成一个包含 fsbl 和 application 的 BIF 文件，然后检查这个命令是否正确：`bootgen -arch zynqmp -image test.bif -o boot.bin`
>
> Agent：① 调用 `generate_bif` 生成 BIF 模板 → ② 调用 `check_command_syntax` 验证命令 → ③ 整合输出完整回答

## 工具列表

| 工具 | 触发场景 | 实现方式 |
|------|---------|---------|
| `rag_search` | 查询 UG1283 文档内容（启动流程、属性说明等） | 复用项目2的 FAISS 向量检索 |
| `generate_bif` | 根据器件和组件生成 BIF 文件模板 | 规则模板，支持 zynqmp / versal |
| `check_command_syntax` | 验证 bootgen 命令行语法 | 规则校验（必填参数 + 合法值检查） |
| `compare_devices` | 对比两个器件的配置差异 | 结构化查表 |

## 典型使用场景

**场景1：生成并验证启动镜像命令**
```
帮我为 zynqmp 生成包含 fsbl、pmu 和 application 的 BIF，
并检查命令 bootgen -arch zynqmp -image test.bif -o boot.bin 是否正确
```

**场景2：器件选型对比**
```
zynqmp 和 versal 在启动流程和组件上有什么区别？
```

**场景3：文档查询**
```
UG1283 中 authentication 在引导流程中的作用是什么？
```

## 技术栈

- **LangChain** — Agent 框架（`create_tool_calling_agent` + `AgentExecutor`）
- **DeepSeek** — LLM（tool calling 支持良好，成本低于 OpenAI）
- **FAISS** — 向量检索（复用项目2的向量库）
- **Streamlit** — Web UI

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API Key
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY 和 OPENAI_API_KEY（用于 embedding）

# 3. 确保项目2的向量库已生成
# vectorstore/ 目录需存在，否则先运行 rag-knowledge-bot 完成索引

# 4. 启动
streamlit run app.py
```

## 项目结构

```
├── tools/
│   ├── rag_tool.py           # RAG 检索工具（复用项目2）
│   ├── bif_generator.py      # BIF 文件生成
│   ├── command_validator.py  # bootgen 命令语法校验
│   └── device_comparator.py  # 器件对比查表
├── agent.py                  # Agent 组装与 AgentExecutor
├── app.py                    # Streamlit 入口
└── README.md
```

## 关键设计决策

**为什么 Agent 效果比纯 RAG 好？**

RAG 的瓶颈在检索层——向量相似度不稳定，技术文档的页眉页脚噪音会干扰检索质量。而 `generate_bif`、`check_command_syntax`、`compare_devices` 这三个工具的输出是确定性的，完全不依赖检索，自然没有"找不到相关信息"的问题。

> 核心原则：**能用规则/工具解决的问题，不要交给 RAG。RAG 适合开放性文档查询，工具适合有明确输入输出的结构化任务。**

## 已知局限与后续方向

- 当前仅支持 zynqmp 和 versal 两种器件，可扩展至 zynq、spartanup 等
- BIF 生成仅覆盖 non-secure 镜像，安全镜像（加密/认证）为后续扩展方向
- 计划用 **LangGraph** 重构 Agent，将每个工具调用显式建模为节点，获得更精细的流程控制和更好的可观测性
