"""
embedder.py - 向量化与存储

- 把 chunk 转成向量
- 存入 FAISS 向量数据库
- 支持持久化保存（下次启动不用重新计算）
"""

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
import torch

# 存储文件夹在 "/rag-knowledge-bot/vectorstore"
VECTORSTORE_PATH = "vectorstore"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def build_vectorstore(chunks: list):
    """
    把 chunks 向量化并存入 FAISS

    Args:
        chunks: split_documents() 返回的 chunk 列表

    Returns:
        vectorstore: FAISS 实例
    """
    # 这个项目中使用HuggingFaceEmbeddings更节省时间和成本
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': device},
        encode_kwargs={'normalize_embeddings': True},
    )
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(VECTORSTORE_PATH)
    return vectorstore


def load_vectorstore():
    """
    从本地加载已有的向量库（如果存在）

    Returns:
        vectorstore 或 None
    """
    # 检查 1."/rag-knowledge-bot/vectorstore"是否存在，2.“index.faiss”和“index.pkl”是否存在
    if not os.path.exists(VECTORSTORE_PATH) or \
    not os.path.exists(os.path.join(VECTORSTORE_PATH, "index.faiss")) or \
    not os.path.exists(os.path.join(VECTORSTORE_PATH, "index.pkl")):
        return None

    # 这个项目中使用HuggingFaceEmbeddings更节省时间和成本
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': device}, 
        encode_kwargs={'normalize_embeddings': True},
    )
    vectorstore = FAISS.load_local(VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)
    return vectorstore