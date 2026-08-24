from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import re


def load_documents(data_dir: str) -> list:
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
        if filename == "UG1283.pdf":
            documents += docs[6:]
        else:
            documents += docs

    return documents


def split_documents(documents: list) -> list:
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