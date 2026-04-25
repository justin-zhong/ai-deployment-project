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
        #print(filename, filepath)

        if filename.endswith(".pdf"):
            # TODO: 用 PyPDFLoader 加载 PDF
            # 提示：loader = PyPDFLoader(filepath)
            #       docs = loader.load()
            loader = PyPDFLoader(filepath)
            docs = loader.load()
            #print(f"pdf: {docs[0]}")

        elif filename.endswith(".txt"):
            # TODO: 用 TextLoader 加载 TXT
            # 提示：loader = TextLoader(filepath, encoding="utf-8")
            loader = TextLoader(filepath, encoding = 'utf-8')
            docs = loader.load()
            #print(f"txt: {docs[0]}")
        else:
            continue
        documents += docs[6:]
        #print(len(documents))

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
        #print(f"清洗前：{repr(doc.page_content)}")
        doc.page_content = re.sub(r"^Send Feedback.*", "", doc.page_content, flags=re.MULTILINE)
        doc.page_content = re.sub(r"^.*UG1283 \(v.*$", "", doc.page_content, flags=re.MULTILINE)
        doc.page_content = re.sub(r"^\s*Bootgen 用户指南\s+\d+\s*$", "", doc.page_content, flags=re.MULTILINE)
        #print(f"清洗后：{repr(doc.page_content)}")
    
    # TODO: 初始化 RecursiveCharacterTextSplitter
    # 思考：chunk_size 和 chunk_overlap 设多少合适？太大会导致什么？太小呢？
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)  # 替换这一行

    # TODO: 调用 text_splitter.split_documents(documents)
    #print(type(documents[0]))
    chunks = text_splitter.split_documents(documents)  # 替换这一行
    #print(chunks)
    print(f"切分后共 {len(chunks)} 个 chunk")
    return chunks

if __name__ == "__main__":
    docs = load_documents("data")
    print(f"加载了 {len(docs)} 个文档")
    #print(type(docs))
    chunks = split_documents(docs)
    print(f"切成了 {len(chunks)} 个 chunk")
    for i, chunk in enumerate(chunks):
        if "安装" in chunk.page_content and "Bootgen" in chunk.page_content:
            print(f"chunk {i}:")
            print(chunk.page_content[:300])
            print("---")
    import random
    """for i, chunk in enumerate(random.sample(chunks, 5)):
        print(f"\n第{i}个 chunk 内容：")
        print(chunk.page_content)
        print(f"\nchunk 长度：{len(chunk.page_content)} 字符")
    """