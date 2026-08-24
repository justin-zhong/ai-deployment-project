from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
import torch

VECTORSTORE_PATH = "vectorstore"

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def build_vectorstore(chunks: list):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': device},
        encode_kwargs={'normalize_embeddings': True},
    )
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(VECTORSTORE_PATH)
    return vectorstore


def load_vectorstore():
    # 检查 1."/rag-knowledge-bot/vectorstore"是否存在，2.“index.faiss”和“index.pkl”是否存在
    if not os.path.exists(VECTORSTORE_PATH) or \
    not os.path.exists(os.path.join(VECTORSTORE_PATH, "index.faiss")) or \
    not os.path.exists(os.path.join(VECTORSTORE_PATH, "index.pkl")):
        return None

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': device}, 
        encode_kwargs={'normalize_embeddings': True},
    )
    # The vectorstore is generated locally by this project.
    # Only load vectorstores created from trusted project data.
    vectorstore = FAISS.load_local(VECTORSTORE_PATH, embeddings, allow_dangerous_deserialization=True)
    return vectorstore