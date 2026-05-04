"""
loader.py - 文档加载与切分

你的任务：
1. 支持加载 PDF 和 TXT 文件
2. 把长文档切成合适大小的 chunk
3. 返回 Document 对象列表

关键概念：
- chunk_size: 每个片段的字符数（建议 500–1000）
- chunk_overlap: 片段之间的重叠字符数（建议 50–100，避免语义断裂）
"""

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import re

def find_content_start_by_pattern(docs, patterns=["chapter", "introduction", "概述"]):
    """Find first page that doesn't look like table of contents"""
    for i, doc in enumerate(docs):
        content = doc.page_content.lower()
        
        # Skip if page has typical TOC indicators
        if any(pattern in content for pattern in patterns):
            return i
    return 0

def load_documents(data_dir: str) -> list:
    """
    从 data_dir 目录加载所有文档

    Args:
        data_dir: 文档目录路径

    Returns:
        documents: List[Document]
    """
    documents = []

    for filename in os.listdir(data_dir):
        filepath = os.path.join(data_dir, filename)
        

        if filename.endswith(".pdf"):
            # 提取文档名称
            source = filename.split('-')[0].upper()
            loader = PyPDFLoader(filepath)
            docs = loader.load()

        elif filename.endswith(".txt"):
            loader = TextLoader(filepath, encoding = 'utf-8')
            docs = loader.load()
        else:
            continue

        parsed_docs = docs[find_content_start_by_pattern(docs, ["chapter 1\n", "第 1 章\n"]):]
        print(f"起始页索引：{find_content_start_by_pattern(docs, ["chapter 1\n", "第 1 章\n"])}\n")
        print(f"起始页内容前150字：{parsed_docs[0].page_content[:150]}\n")
        for page in parsed_docs:
            page.metadata["source"] = source
            page.metadata["filename"] = filename
        documents += parsed_docs

    print(f"共加载 {len(documents)} 个文档片段（切分前）")
    return documents


def split_documents(documents: list) -> list:
    """
    把文档切分成 chunk

    Args:
        documents: load_documents() 返回的文档列表

    Returns:
        chunks: List[Document]
    """
    #添加pdf清洗功能
    for doc in documents:
        doc.page_content = re.sub(r"^Send Feedback.*", "", doc.page_content, flags=re.MULTILINE)
        doc.page_content = re.sub(r"^.*UG* \(v.*$", "", doc.page_content, flags=re.MULTILINE)
        doc.page_content = re.sub(r"^\s*Bootgen 用户指南\s+\d+\s*$", "", doc.page_content, flags=re.MULTILINE)
        doc.page_content = re.sub(r"^\s*Zynq UltraScale+ MPSoC Software Developer Guide\s+\d+\s*$", "", doc.page_content, flags=re.MULTILINE)
        doc.page_content = re.sub(r"^\s*Zynq UltraScale+ Device TRM\s+\d+\s*$", "", doc.page_content, flags=re.MULTILINE)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

    chunks = text_splitter.split_documents(documents)
    print(f"切分后共 {len(chunks)} 个 chunk")
    return chunks

if __name__ == "__main__":
    docs = load_documents("data")
    print(f"加载了 {len(docs)} 个文档")
    chunks = split_documents(docs)
    print(f"切成了 {len(chunks)} 个 chunk")

    import random
    for i, chunk in enumerate(random.sample(chunks, 5)):
        print(f"来源：{chunk.metadata['source']}")
        print(f"文件：{chunk.metadata['filename']}")
        print(f"\n第{i}个 chunk 内容：")
        print(chunk.page_content[:80])
        print(f"\nchunk 长度：{len(chunk.page_content)} 字符")
