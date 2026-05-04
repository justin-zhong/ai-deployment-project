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

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
import torch

VECTORSTORE_PATH = "vectorstore"

vectorstore = None

# This will automatically be 'cuda' when the GPU is available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def build_vectorstore(chunks: list):
    """
    把 chunks 向量化并存入 FAISS

    Args:
        chunks: split_documents() 返回的 chunk 列表

    Returns:
        vectorstore: FAISS 实例
    """
    print("正在向量化，请稍候...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': device}, 
        encode_kwargs={'normalize_embeddings': True},
    )

    vectorstore = FAISS.from_documents(chunks, embeddings)

    vectorstore.save_local(VECTORSTORE_PATH)
    print(f"向量库已保存到 {VECTORSTORE_PATH}/")
    return vectorstore


def load_vectorstore():
    """
    从本地加载已有的向量库（如果存在）

    Returns:
        vectorstore 或 None
    """
    # Check directory AND both files exist
    if not os.path.exists(VECTORSTORE_PATH) or \
    not os.path.exists(os.path.join(VECTORSTORE_PATH, "index.faiss")) or \
    not os.path.exists(os.path.join(VECTORSTORE_PATH, "index.pkl")):
        return None

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': device},
        encode_kwargs={'normalize_embeddings': True},
    )
    vectorstore = FAISS.load_local(VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)
    print("已从本地加载向量库")
    return vectorstore

if __name__ == "__main__":
    from loader import load_documents, split_documents
    docs = load_documents("data")
    chunks = split_documents(docs)
    build_vectorstore(chunks)
