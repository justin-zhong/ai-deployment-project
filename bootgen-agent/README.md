**English** | [中文](README_CN.md)

# 🤖 Project 3: Bootgen Intelligent Assistant Agent

> **Project Series:** [Projects 1–2: RAG Knowledge Base](../rag-knowledge-bot) → **Project 3: Bootgen Agent (Current)** → [Project 4: Multi-Document RAG + Deployment](../amd-doc-agent)

A domain-specific AI Agent for AMD Bootgen engineering workflows, built with
LangGraph. Unlike a pure RAG system, the Agent can autonomously decide which
tool to invoke and execute multiple tools in sequence as needed.

For structured tasks such as BIF generation, command validation, and device
comparison, the Agent provides more reliable results than relying on document
retrieval alone.

## Demo

> **User:** Generate a BIF file for `zynqmp` containing FSBL and an application,
> then check whether this command is valid:
> `bootgen -arch zynqmp -image test.bif -o boot.bin`
>
> **Agent:** ① Calls `generate_bif` to generate the BIF template → ② Calls
> `check_command_syntax` to validate the command → ③ Combines the results into
> a complete response

## Tools

| Tool | Trigger Scenario | Implementation |
|---|---|---|
| `rag_search` | Query UG1283 documentation, such as boot flows and attribute descriptions | FAISS vector search |
| `generate_bif` | Generate a BIF file template based on device and components | Rule-based templates supporting `zynqmp` / `versal` |
| `check_command_syntax` | Validate Bootgen command-line syntax | Rule-based validation of required parameters and valid values |
| `compare_devices` | Compare configuration differences between two devices | Structured lookup |

## Typical Use Cases

### Scenario 1: Generate and Validate a Boot Image Command

```
Generate a BIF containing FSBL, PMU, and an application for zynqmp,
and check whether the command
bootgen -arch zynqmp -image test.bif -o boot.bin
is valid.
```

### Scenario 2: Device Comparison
```
What are the differences between zynqmp and versal
in terms of boot flow and supported components?
```
The Agent uses compare_devices to retrieve structured device information and
can combine it with rag_search when additional documentation context is
required.

### Scenario 3: Cross-Tool Reasoning
```
If I change zynqmp to zynq in the command,
will the command still be valid?
```
The Agent can combine rag_search with compare_devices to reason about the
device-specific differences rather than simply performing a table lookup.

## Tech Stack

- **LangGraph** — Agent framework using StateGraph, MessagesState, and ToolNode
- **LangChain** — Tool definitions with the @tool decorator and LLM integration
- **DeepSeek** — LLM with tool-calling support
- **FAISS** — Vector retrieval
- **MCP** — Exposes the tools through a standardized MCP Server
- **LangSmith** — Agent tracing and observability
- **Streamlit** — Web UI

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure API keys
```bash
cp .env.example .env
Edit .env and configure the required environment variables:
DEEPSEEK_API_KEY=your_key
OPENAI_API_KEY=your_key
LANGCHAIN_API_KEY=your_key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=bootgen-agent
```
OPENAI_API_KEY is used for embeddings. LANGCHAIN_API_KEY is optional and
is only required if LangSmith tracing is enabled.

### 3. Ensure the Vector Store Exists
The `vectorstore/` directory must exist before starting the Agent.

If it does not exist, first run
`rag-knowledge-bot` to load and index the technical
documentation.

### 4. Start the Streamlit UI
```bash
streamlit run app.py
```

### 5. Start the MCP Server (Optional)
```bash
mcp dev mcp_server.py
```

## Project Structure

```
├── tools/
│   ├── rag_tool.py           # RAG retrieval tool
│   ├── bif_generator.py      # BIF file generation
│   ├── command_validator.py  # Bootgen command syntax validation
│   └── device_comparator.py  # Device comparison
├── agent.py                  # LangChain Agent version (initial implementation)
├── agent_lg.py               # LangGraph version (current implementation)
├── mcp_server.py             # MCP Server exposing all four tools
├── app.py                    # Streamlit entry point
└── README.md
```

## LangGraph Architecture

```
[User Input]
      ↓
[Agent Node] — LLM decides which tool to invoke
      ↓
  ┌───────────────┐
  │               │
Tool Calls      No Tool Calls
  ↓               ↓
[Tools Node]     [END]
  ↓
Back to [Agent Node]
```

Compared with the more opaque execution loop of a LangChain Agent,
LangGraph provides several advantages:

- **Explicit state:** Each node's inputs and outputs are represented through
MessagesState, making the workflow easier to inspect and debug.
- **Controlled execution:** Conditional edges provide precise control over
routing logic and allow custom nodes to be introduced for more complex
workflows.
- **Extensibility:** Additional nodes, such as human approval or error
recovery, can be added without redesigning the entire workflow.

## Observability with LangSmith

LangSmith is integrated to trace the Agent execution flow. It provides
visibility into:

- Complete inputs and outputs for each LLM decision
- Tool-call parameters and return values
- Latency distribution across the workflow
- Token usage

**Example LangSmith Trace:**[View trace](https://smith.langchain.com/public/79a5705d-8365-4ce0-9e8f-da220bfb149c/r)

## MCP Server

All four tools are also exposed through an MCP Server, allowing any
MCP-compatible client, such as Claude Desktop, to invoke them directly
without going through the LangGraph Agent.

Start the MCP development server with:

```bash
mcp dev mcp_server.py
```

This separates the tool implementation from the Agent orchestration
layer, allowing the same tools to be reused by different MCP-compatible
clients.

## Key Design Decisions

**Why Does the Agent Perform Better Than Pure RAG?**

A key limitation of RAG is that its performance depends on retrieval quality.
Vector similarity can be unstable, and noise in technical documentation can
further degrade retrieval results.

In contrast, the outputs of generate_bif, check_command_syntax, and
compare_devices are deterministic and do not depend on retrieval.

This eliminates failure modes such as "no relevant information found" for
structured tasks.

> Core principle: Use rules and deterministic tools whenever possible.
Use RAG for open-ended knowledge retrieval and tools for structured tasks
with well-defined inputs and outputs.

This principle became a key design decision for the Agent architecture.

**Why Migrate from LangChain Agent to LangGraph?**

The initial implementation used a LangChain Agent. However, the execution
process was relatively opaque: it was difficult to inspect the intermediate
decisions and tool-routing logic.

The LangGraph implementation explicitly models each step as a node in a state
graph. Combined with LangSmith tracing, this makes the Agent workflow easier
to debug and extend.

Both implementations are retained in the repository, allowing direct
comparison between the LangChain Agent and LangGraph approaches.

## Known Limitations and Future Directions

- Currently supports only zynqmp and versal; support could be extended to
additional devices such as zynq and spartanup.
- BIF generation currently covers non-secure boot images. Secure boot features
such as encryption and authentication are potential future extensions.
- A human-in-the-loop approval node could be added so that generated BIF
files are presented to the user for confirmation before command validation
or further execution.