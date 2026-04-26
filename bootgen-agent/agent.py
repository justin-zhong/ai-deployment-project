from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import os
from tools.bif_generator import generate_bif
from tools.rag_tool import rag_search
from tools.device_comparator import compare_devices
from tools.command_validator import validate_command

API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 1. 把工具集合起来
tools = [rag_search, generate_bif, validate_command, compare_devices]

# 2. 定义 LLM
llm = ChatOpenAI(
    model='deepseek-chat',
    openai_api_key=API_KEY,
    openai_api_base='https://api.deepseek.com',
)
# 3. 定义 Prompt
# Agent 的 Prompt 和 RAG 的不一样，需要包含几个特殊占位符
prompt = """你是一个有用的ai助手。
你必须使用定义的工具来回答用户的问题。
当生成BIF时，请用generate_bif工具。
当检查bootgen指令语法时，请用check_command_syntax工具。
当对比器件时，请用compare_devices工具。
如果搜索文档中的内容时，请用rag_search工具。
如果没有找到合适的工具请回答你没有找到合适的工具。       
"""
# 4. 组装 Agent
agent = create_agent(llm, tools, system_prompt=prompt)
# 5. 创建 AgentExecutor
if __name__ == "__main__":
    result = agent.invoke({
    "messages": [
        #("user", "zynqmp和versal的区别是什么？"),
        ("user", """帮我为zynqmp生成一个包含fsbl和application的BIF文件，
         然后帮我检查这个命令是否正确：
         bootgen -arch zynqmp -image test.bif -o boot.bin"""),                ]
    })
    print(result['messages'][-1].content)