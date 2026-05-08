"""
chain.py - 组装 RAG 链

- 写一个好的 Prompt Template
- 把检索器 + LLM 组装成完整的 RAG 链
- 处理"找不到相关内容"的情况
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os

PROMPT_TEMPLATE = """
你是一个知识库问答助手。请根据以下上下文回答用户的问题。

上下文：
{context}

问题：{question}

如果上下文中没有相关信息，请说明“没有找到相关信息”并打印，不要自己创造答案。
"""


def format_docs(docs) -> str:
    # 把检索到的文档列表拼接成字符串
    return "\n\n".join([doc.page_content for doc in docs])


def build_rag_chain(retriever):
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
    chain = (
     {"context": retriever | format_docs,
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
