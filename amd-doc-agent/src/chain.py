from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from src.util import get_deepseek_api_key

PROMPT_TEMPLATE = """
你是一个知识库问答助手。请根据以下上下文回答用户的问题。

上下文：
{context}

问题：{question}

回答时请注明信息来自哪份文档（如"根据UG1283..."）。
如果上下文中没有相关信息，请说明“没有找到相关信息”并打印，不要自己创造答案。
"""

def format_docs(docs) -> str:
    return "\n\n".join([f"{doc.metadata['source']}\n{doc.page_content}" for doc in docs])

def _build_deepseek_llm():
    return ChatOpenAI(
        model="deepseek-chat",
        api_key=get_deepseek_api_key(),
        base_url="https://api.deepseek.com",
        temperature=0
    )

def build_answer_chain():
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    
    return prompt | _build_deepseek_llm() | StrOutputParser()

def ask_with_context(chain, question: str, docs) -> str:
    return chain.invoke({
        "context": format_docs(docs),
        "question": question
    })

def build_rag_chain(retriever):
    return (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | build_answer_chain()
    )

def ask(chain, question: str) -> str:
    return chain.invoke(question)