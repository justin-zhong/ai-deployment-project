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


def get_retriever(vectorstore, k: int = 4):
    """
    从向量库创建检索器

    Args:
        vectorstore: FAISS 向量库实例
        k: 返回的相关文档数量

    Returns:
        retriever
    """
    # TODO: 用 vectorstore.as_retriever() 创建检索器
    # 提示：search_kwargs={"k": k} 控制返回数量
    retriever = vectorstore.as_retriever(
        search_kwargs = {"k": k}
    )  # 替换这一行

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
    # TODO: 用 vectorstore.similarity_search(query, k=k)
    results = vectorstore.similarity_search(query, k=k)  # 替换这一行

    # 打印结果（调试用）
    for i, doc in enumerate(results):
        print(f"\n--- 第 {i+1} 个相关片段 ---")
        print(doc.page_content[:200])  # 只打印前200字

    return results

if __name__ == "__main__":
    from embedder import build_vectorstore, load_vectorstore
    vectorstore = load_vectorstore()
    results = search(vectorstore, "什么是 Bootgen 工具？", k=4)
    results = search(vectorstore, "如何在 BIF 文件中定义分区？", k=4)
    results = search(vectorstore, "如何在 BIF 文件中指定启动设备？", k=4)