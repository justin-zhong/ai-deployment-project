"""
retriever.py - 检索逻辑

- 根据用户问题，从向量库里找最相关的 chunk
- 返回 top-k 个结果
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
        k: 返回chunk数量

    Returns:
        List[Document]
    """
    results = vectorstore.similarity_search(query, k=k)
    return results