from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
import re

def find_content_start_by_pattern(docs, patterns=["chapter", "introduction", "概述"]):
    for i, doc in enumerate(docs):
        content = doc.page_content.lower()
        
        # Skip if page has typical TOC indicators
        if any(pattern in content for pattern in patterns):
            return i
    return 0

def load_documents(data_dir: str) -> list:
    documents = []

    for filename in os.listdir(data_dir):
        filepath = os.path.join(data_dir, filename)

        if filename.endswith(".pdf"):
            source = filename.split('-')[0].upper()
            loader = PyPDFLoader(filepath)
            docs = loader.load()

        elif filename.endswith(".txt"):
            loader = TextLoader(filepath, encoding = 'utf-8')
            docs = loader.load()
        else:
            continue

        parsed_docs = docs[find_content_start_by_pattern(docs, ["chapter 1\n", "第 1 章\n"]):]
        for page in parsed_docs:
            page.metadata["source"] = source
            page.metadata["filename"] = filename
        documents += parsed_docs
    return documents


def split_documents(documents: list) -> list:
    #pdf清洗
    for doc in documents:
        doc.page_content = re.sub(r"^Send Feedback.*", "", doc.page_content, flags=re.MULTILINE)
        doc.page_content = re.sub(r"^.*UG* \(v.*$", "", doc.page_content, flags=re.MULTILINE)
        doc.page_content = re.sub(r"^\s*Bootgen 用户指南\s+\d+\s*$", "", doc.page_content, flags=re.MULTILINE)
        doc.page_content = re.sub(r"^\s*Zynq UltraScale+ MPSoC Software Developer Guide\s+\d+\s*$", "", doc.page_content, flags=re.MULTILINE)
        doc.page_content = re.sub(r"^\s*Zynq UltraScale+ Device TRM\s+\d+\s*$", "", doc.page_content, flags=re.MULTILINE)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)

    chunks = text_splitter.split_documents(documents)
    return chunks
