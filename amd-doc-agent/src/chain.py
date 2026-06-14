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
    #把检索到的文档列表拼接成字符串
    return "\n\n".join([f"{doc.metadata['source']}\n{doc.page_content}" for doc in docs])


def build_rag_chain(retriever, vs, chunks):
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
        temperature=0
    )

    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)

    multilingual_retriever = RunnableLambda(lambda q: retrieve_multilingual(vs, chunks, q, k=4))
    
    chain = (
     {"context": multilingual_retriever | format_docs,
      "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain


def ask(chain, question: str) -> str:
    answer = chain.invoke(question)
    return answer