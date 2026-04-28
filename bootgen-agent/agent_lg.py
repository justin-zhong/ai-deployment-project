from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_openai import ChatOpenAI

from tools.bif_generator import generate_bif
from tools.rag_tool import rag_search
from tools.device_comparator import compare_devices
from tools.command_validator import validate_command

import os

API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 1. 定义工具列表
tools = [rag_search, generate_bif, validate_command, compare_devices]
# 2. 定义 agent 节点函数
llm = ChatOpenAI(
    model='deepseek-chat',
    openai_api_key=API_KEY,
    openai_api_base='https://api.deepseek.com',
)

def agent_node(state: MessagesState):
    print(f"当前消息数：{len(state['messages'])}")  # 临时调试
    response = llm.bind_tools(tools).invoke(state["messages"])
    return {"messages": [response]}
    
tool_node = ToolNode(tools)
# 3. 构建图
graph = StateGraph(MessagesState)

graph.add_node("agent", agent_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", tools_condition)
graph.add_edge("tools", "agent")  # 工具执行完回到agent继续决策
# 4. 编译
app = graph.compile()

if __name__ == "__main__":
    result = app.invoke({
        "messages": [("user", "zynqmp和versal的区别是什么？")]
    })
    print(result["messages"][-1].content)