"""
chain.py - 组装 RAG 链

你的任务：
1. 写一个好的 Prompt Template
2. 把检索器 + LLM 组装成完整的 RAG 链
3. 处理"找不到相关内容"的情况

关键概念：
- Prompt Template：告诉 LLM 它的角色、它能用什么信息、怎么回答
- RetrievalQA / LCEL：LangChain 提供的两种组装方式，这里用更现代的 LCEL
- context：检索到的相关 chunk，会被填入 prompt
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from retriever import retrieve_multilingual
import os

PROMPT_TEMPLATE = """
你是一个知识库问答助手。请根据以下上下文回答用户的问题。

上下文：
{context}

问题：{question}

回答时请注明信息来自哪份文档（如"根据UG1283..."）。如果上下文中没有相关信息，请说明“没有找到相关信息”并打印，不要自己创造答案。
"""


def format_docs(docs) -> str:
    """把检索到的文档列表拼接成字符串"""
    return "\n\n".join([f"{doc.metadata['source']}\n{doc.page_content}" for doc in docs])


def build_rag_chain(retriever, vs):
    """
    组装 RAG 链

    Args:
        retriever: get_retriever() 返回的检索器

    Returns:
        chain: 可以直接调用的 RAG 链
    """
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
        temperature=0
    )

    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

    multilingual_retriever = RunnableLambda(lambda q: retrieve_multilingual(vs, q, k=4))
    
    chain = (
     {"context": multilingual_retriever | format_docs,
      "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


def ask(chain, question: str) -> str:
    """
    向 RAG 链提问

    Args:
        chain: build_rag_chain() 返回的链
        question: 用户问题

    Returns:
        answer: 字符串答案
    """
    answer = chain.invoke(question)

    return answer

if __name__ == "__main__":
    from embedder import build_vectorstore, load_vectorstore
    from retriever import get_retriever
    from loader import load_documents, split_documents
    if os.path.exists("vectorstore"):
        vs = load_vectorstore()
    else:    
        docs = load_documents("data")
        chunks = split_documents(docs)
        vs = build_vectorstore(chunks)
    retriever = get_retriever(vs)
    chain = build_rag_chain(retriever)
    
    questions = [
        "Zynq UltraScale+ 的启动流程是什么？",
        "AES 加密在硬件和软件层面分别如何配置？",
        "FSBL 的作用是什么？",
    ]
    
    for q in questions:
        print(f"\n问：{q}")
        print(f"答：{ask(chain, q)}")
        print("="*50)
