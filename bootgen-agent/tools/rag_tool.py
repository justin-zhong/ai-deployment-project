from langchain.tools import tool
import sys
sys.path.append("../rag-knowledge-bot")  # 指向项目2的路径
from src.embedder import load_vectorstore
from src.retriever import get_retriever
from src.chain import build_rag_chain, ask

import os
os.chdir("../rag-knowledge-bot")
VECTORSTORE_PATH = "vectorstore"

vectorstore = load_vectorstore()
retriever = get_retriever(vectorstore)
chain = build_rag_chain(retriever)
os.chdir("../bootgen-agent")


@tool
def rag_search(query: str) -> str:
    """
    当询问关于UG1283的问题时，使用这个工具来回答问题。几个范例的技术领域： BIF 语法、启动流程、加密认证
    """
    
    answer = ask(chain, query)
    return answer