"""
embedder.py - 向量化与存储

你的任务：
1. 把 chunk 转成向量
2. 存入 FAISS 向量数据库
3. 支持持久化保存（下次启动不用重新计算）

关键概念：
- Embedding：把文字变成一串数字，语义相近的文字，数字也相近
- FAISS：Meta 开源的向量数据库，本地运行，适合入门
- 持久化：向量计算很慢，保存到磁盘下次直接加载
"""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os

VECTORSTORE_PATH = "vectorstore"


def build_vectorstore(chunks: list):
    """
    把 chunks 向量化并存入 FAISS

    Args:
        chunks: split_documents() 返回的 chunk 列表

    Returns:
        vectorstore: FAISS 实例
    """
    print("正在向量化，请稍候...")

    # TODO: 初始化 OpenAIEmbeddings
    # 提示：embeddings = OpenAIEmbeddings()
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cuda'},  # Use 'cuda' if you have GPU
        encode_kwargs={'normalize_embeddings': True},
    )

    # TODO: 用 FAISS.from_documents(chunks, embeddings) 创建向量库
    vectorstore = FAISS.from_documents(chunks, embeddings)  # 替换这一行

    # TODO: 把向量库保存到本地（VECTORSTORE_PATH）
    # 提示：vectorstore.save_local(VECTORSTORE_PATH)
    vectorstore.save_local(VECTORSTORE_PATH)
    print(f"向量库已保存到 {VECTORSTORE_PATH}/")
    return vectorstore


def load_vectorstore():
    """
    从本地加载已有的向量库（如果存在）

    Returns:
        vectorstore 或 None
    """
    if not os.path.exists(VECTORSTORE_PATH):
        return None

    # TODO: 用 FAISS.load_local() 加载
    # 注意：需要传入 embeddings 和 allow_dangerous_deserialization=True
    # 提示：FAISS.load_local(VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cuda'},  # Use 'cuda' if you have GPU
        encode_kwargs={'normalize_embeddings': True},
    )
    vectorstore = FAISS.load_local(VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)
    print("已从本地加载向量库")
    return vectorstore  # 替换这一行
