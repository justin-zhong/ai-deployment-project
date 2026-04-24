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

from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import os


# TODO: 写一个好的 Prompt Template
# 思考：
# 1. 如何告诉 LLM 只用提供的 context 回答，不要乱编？
# 2. 如果 context 里没有答案，应该怎么说？
# 3. 回答应该是什么风格？
PROMPT_TEMPLATE = """
你是一个知识库问答助手。请根据以下上下文回答用户的问题。

上下文：
{context}

问题：{question}

// TODO: 补充你的指令
// 提示：考虑加上"如果上下文中没有相关信息，请说明..."
如果上下文中没有相关信息，请说明“没有找到相关信息”并打印，不要自己创造答案。
"""


def format_docs(docs) -> str:
    """把检索到的文档列表拼接成字符串"""
    # TODO: 把 docs 里每个 doc.page_content 拼接起来
    # 提示："\n\n".join([doc.page_content for doc in docs])
    return "\n\n".join([doc.page_content for doc in docs])  # 替换这一行


def build_rag_chain(retriever):
    """
    组装 RAG 链

    Args:
        retriever: get_retriever() 返回的检索器

    Returns:
        chain: 可以直接调用的 RAG 链
    """
    # TODO: 初始化 LLM
    # 提示：llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    # 思考：temperature=0 意味着什么？什么场景下应该调高？
    llm = ChatDeepSeek(model= "deepseek-reasoner", api_key = os.getenv('DEEPSEEK_API_KEY'), temperature=0)# 替换这一行

    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

    # TODO: 用 LCEL 组装链
    # 标准 RAG 链结构：
    # chain = (
    #     {"context": retriever | format_docs, "question": RunnablePassthrough()}
    #     | prompt
    #     | llm
    #     | StrOutputParser()
    # )
    chain = (
     {"context": retriever | format_docs,
      "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )# 替换这一行

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
    # TODO: 调用 chain.invoke(question)
    answer = chain.invoke(question)  # 替换这一行

    return answer
