[English](README.md) | **中文**

# 🤖 项目3：Bootgen 智能助手 Agent

> **项目系列**：[项目1+2: RAG知识库](../rag-knowledge-bot) → **项目3: Bootgen Agent（当前）** → [项目4: 多文档RAG + 部署](../amd-doc-agent)

基于 LangGraph 的 AMD Bootgen 专属助手。相比纯 RAG 方案，Agent 能主动决策调用哪个工具、按需链式执行多步操作，对结构化任务（BIF 生成、命令校验、器件对比）的回答质量显著优于检索方式。

## Demo

> 用户：帮我为 zynqmp 生成一个包含 fsbl 和 application 的 BIF 文件，然后检查这个命令是否正确：`bootgen -arch zynqmp -image test.bif -o boot.bin`
>
> Agent：① 调用 `generate_bif` 生成 BIF 模板 → ② 调用 `check_command_syntax` 验证命令 → ③ 整合输出完整回答

## 工具列表

| 工具 | 触发场景 | 实现方式 |
|------|---------|---------|
| `rag_search` | 查询 UG1283 文档内容（启动流程、属性说明等） | FAISS 向量检索 |
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

**场景3：跨工具推理**
```
如果把命令中的 zynqmp 改成 zynq，还正确吗？
```
Agent 会同时调用 `rag_search` 查文档 + `compare_devices` 对比器件差异，综合推理给出答案，而不是简单查表。

## 技术栈

- **LangGraph** — Agent 框架（`StateGraph` + `MessagesState` + `ToolNode`）
- **LangChain** — 工具定义（`@tool` 装饰器）、LLM 调用
- **DeepSeek** — LLM（tool calling 支持良好，成本低于 OpenAI）
- **FAISS** — 向量检索
- **MCP** — 工具封装为 MCP Server，支持标准化协议调用
- **LangSmith** — Agent 链路追踪与可观测性
- **Streamlit** — Web UI

## 快速开始

# 1. 安装依赖
```bash
pip install -r requirements.txt
```

# 2. 配置 API Key
```bash
cp .env.example .env
```
# 编辑 .env，填入以下环境变量：
```bash
DEEPSEEK_API_KEY=your_key
OPENAI_API_KEY=your_key（用于 embedding）
LANGCHAIN_API_KEY=your_key（用于 LangSmith，可选）
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=bootgen-agent
```

# 3. 确保向量库已生成
`vectorstore/` 目录需存在，否则先运行 `rag-knowledge-bot` 完成索引

# 4. 启动 Streamlit UI
```bash
streamlit run app.py
```

# 5. 启动 MCP Server（可选）
```bash
mcp dev mcp_server.py
```

## 项目结构

```
├── tools/
│   ├── rag_tool.py           # RAG 检索工具
│   ├── bif_generator.py      # BIF 文件生成
│   ├── command_validator.py  # bootgen 命令语法校验
│   └── device_comparator.py  # 器件对比查表
├── agent.py                  # LangChain Agent 版本（初始实现）
├── agent_lg.py               # LangGraph 版本（重构版，当前使用）
├── mcp_server.py             # MCP Server（四个工具的标准化封装）
├── app.py                    # Streamlit 入口
└── README.md
```

## LangGraph 架构

```
[用户输入]
    ↓
[agent 节点] — LLM 决策，判断调用哪个工具
    ↓ (有 tool_calls)          ↓ (无 tool_calls)
[tools 节点]               [END 结束]
    ↓
回到 [agent 节点]
```

相比 LangChain Agent 的黑盒循环，LangGraph 的优势：
- **状态可见**：每个节点的输入输出都是显式的 `MessagesState`，方便调试
- **流程可控**：通过条件边精确控制路由逻辑，复杂场景下可以加入自定义节点
- **易于扩展**：后续加入"人工确认"节点、"错误重试"节点只需加节点和边

## 可观测性（LangSmith）

集成 LangSmith 对 Agent 链路进行追踪，可实时查看：
- 每次 LLM 决策的完整输入输出
- 工具调用的参数和返回值
- 整个链路的耗时分布和 token 消耗

示例追踪记录：https://smith.langchain.com/public/79a5705d-8365-4ce0-9e8f-da220bfb149c/r

## MCP Server

四个工具同时封装为 MCP Server，支持任意 MCP 兼容客户端（如 Claude Desktop）直接调用，无需通过 LangGraph Agent。

```bash
mcp dev mcp_server.py
```

## 关键设计决策

**为什么 Agent 效果比纯 RAG 好？**

RAG 的瓶颈在检索层——向量相似度不稳定，技术文档噪音会干扰检索质量。而 `generate_bif`、`check_command_syntax`、`compare_devices` 这三个工具的输出是确定性的，完全不依赖检索，自然没有"找不到相关信息"的问题。

> 核心原则：**能用规则/工具解决的问题，不要交给 RAG。RAG 适合开放性文档查询，工具适合有明确输入输出的结构化任务。**

**为什么从 LangChain Agent 迁移到 LangGraph？**

LangChain Agent 是黑盒——只能看到最终输出，看不到中间决策过程。LangGraph 把每一步显式建模为节点，结合 LangSmith 追踪，调试效率大幅提升。两个版本都保留在仓库里，可直接对比代码差异。

## 已知局限与后续方向

- 当前仅支持 zynqmp 和 versal 两种器件，可扩展至 zynq、spartanup 等
- BIF 生成仅覆盖 non-secure 镜像，安全镜像（加密/认证）为后续扩展方向
- 可加入"人工确认"节点：生成 BIF 后先展示给用户确认，再执行命令校验