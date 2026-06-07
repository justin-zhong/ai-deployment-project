from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import os
import torch
import pickle

VECTORSTORE_PATH = "vectorstore"

vectorstore = None

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def build_vectorstore(chunks: list):
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': device}, 
        encode_kwargs={'normalize_embeddings': True},
    )

    with open(f"{VECTORSTORE_PATH}/chunks.pkl", "wb") as f:
        pickle.dump(chunks, f)

    vectorstore = FAISS.from_documents(chunks, embeddings)

    vectorstore.save_local(VECTORSTORE_PATH)
    return vectorstore


def load_vectorstore():
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
    return vectorstore
