"""
retriever.py - 检索逻辑

你的任务：
1. 根据用户问题，从向量库里找最相关的 chunk
2. 返回 top-k 个结果

关键概念：
- similarity_search：用向量相似度找最近的 chunk
- k：返回几个相关片段（建议 3–5，太多会干扰 LLM，太少会漏信息）

进阶思考（做完基础版再考虑）：
- MMR (Maximal Marginal Relevance)：在相关性基础上增加多样性，避免返回重复内容
"""
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os

TRANSLATE_PROMPT = """
你是一个知识库问答助手。如果下面的问题是中文，请将问题翻译为英文并返回。

问题：{question}
"""

def get_retriever(vectorstore, k: int = 4):
    """
    从向量库创建检索器

    Args:
        vectorstore: FAISS 向量库实例
        k: 返回的相关文档数量

    Returns:
        retriever
    """
    retriever = vectorstore.as_retriever(
        search_kwargs = {"k": k}
    )

    return retriever


def search(vectorstore, query: str, k: int = 4) -> list:
    """
    直接搜索（调试用，可以看到具体返回了哪些 chunk）

    Args:
        vectorstore: FAISS 向量库实例
        query: 用户问题
        k: 返回数量

    Returns:
        List[Document]
    """
    results = vectorstore.similarity_search(query, k=k)
    return results


def retrieve_multilingual(vectorstore, query: str, k: int = 4) -> list:
    llm = ChatOpenAI(
        model= "deepseek-chat", 
        api_key = os.getenv('DEEPSEEK_API_KEY'),
        base_url="https://api.deepseek.com",
        temperature=0)
    prompt = ChatPromptTemplate.from_template(TRANSLATE_PROMPT)
    chain = prompt | llm
    response = chain.invoke({"question": query})
    eng_query = response.content
    results = search(vectorstore, query, k=4)
    eng_results = search(vectorstore, eng_query, k=4)
    all_results = [item for pair in zip(results, eng_results) for item in pair]
    seen = set()
    unique_results = []
    for doc in all_results:
        if doc.page_content not in seen:
            seen.add(doc.page_content)
            unique_results.append(doc)
    return unique_results

if __name__ == "__main__":
    from embedder import build_vectorstore, load_vectorstore
    vectorstore = load_vectorstore()
    results = search(vectorstore, "什么是 Bootgen 工具？", k=4)
    results = search(vectorstore, "如何在 BIF 文件中定义分区？", k=4)
    results = search(vectorstore, "如何在 BIF 文件中指定启动设备？", k=4)