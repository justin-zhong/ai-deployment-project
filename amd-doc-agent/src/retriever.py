from langchain_classic.retrievers.ensemble import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.prompts import ChatPromptTemplate

from src.llm_client import build_deepseek_llm

TRANSLATE_PROMPT = """
你是一个知识库问答助手。如果下面的问题是中文，请将问题翻译为英文并返回。

问题：{question}
"""

def get_retriever(vectorstore, chunks: list | None = None, k: int = 4):
    if chunks is None:
        chunks = []

    vectorRetriever = vectorstore.as_retriever(
        search_kwargs = {"k": k}
    )

    if not chunks:
        return vectorRetriever
        
    bm25Retriever = BM25Retriever.from_documents(chunks, k=k)

    retriever = EnsembleRetriever(
        retrievers=[vectorRetriever, bm25Retriever], 
        weights=[0.6, 0.4],
        c=0
    )

    return retriever


def search(vectorstore, query: str, k: int = 4) -> list:
    results = vectorstore.similarity_search(query, k=k)
    return results


def retrieve_multilingual(vectorstore, chunks: list, query: str, k: int = 4) -> list:
    llm = build_deepseek_llm()
    prompt = ChatPromptTemplate.from_template(TRANSLATE_PROMPT)
    chain = prompt | llm
    response = chain.invoke({"question": query})
    eng_query = response.content

    retriever = get_retriever(vectorstore, chunks, k=k)
    results = retriever.invoke(query)
    eng_results = retriever.invoke(eng_query)
    
    all_results = [item for pair in zip(results, eng_results) for item in pair]
    seen = set()
    unique_results = []
    for doc in all_results:
        if doc.page_content not in seen:
            seen.add(doc.page_content)
            unique_results.append(doc)
    return unique_results[:k]