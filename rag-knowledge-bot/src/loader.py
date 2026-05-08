"""
loader.py - 文档加载与切分

- 支持加载 PDF 和 TXT 文件
- 把长文档切成合适大小的 chunk
- 返回 Document 对象列表
"""

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import re


def load_documents(data_dir: str) -> list:
    """
    从 data_dir 目录加载所有文档

    Args:
        data_dir: 文档目录路径

    Returns:
        documents: List[Document]
    """
    print(os.listdir(data_dir))
    documents = []

    for filename in os.listdir(data_dir):
        filepath = os.path.join(data_dir, filename)

        if filename.endswith(".pdf"):
            loader = PyPDFLoader(filepath)
            docs = loader.load()

        elif filename.endswith(".txt"):
            loader = TextLoader(filepath, encoding = 'utf-8')
            docs = loader.load()
        else:
            continue
        # 去掉UG1283的前6页（前6页为封面和目录）
        documents += docs[6:]

    return documents


def split_documents(documents: list) -> list:
    """
    把文档切分成 chunk

    Args:
        documents: load_documents() 返回的文档列表

    Returns:
        chunks: List[Document]
    """
    for doc in documents:
        # 清除页脚格式：“SendFeedback”
        doc.page_content = re.sub(r"^Send Feedback.*", "", doc.page_content, flags=re.MULTILINE)
        # 清除页脚格式：“UG1283(v2025.2) 2025年11月20日”
        doc.page_content = re.sub(r"^.*UG1283 \(v.*$", "", doc.page_content, flags=re.MULTILINE)
        # 清除页脚格式：“Bootgen 用户指南”
        doc.page_content = re.sub(r"^\s*Bootgen 用户指南\s+\d+\s*$", "", doc.page_content, flags=re.MULTILINE)

    # chunk_size=800和chunk_overlap=100是实验后的最优值，详见 README 调优记录
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents) 
    return chunks