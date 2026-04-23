#!/usr/bin/env python
# coding: utf-8

# ## RAG 核心原理
# 
# RAG = Retrieval-Augmented Generation
# 
# 流程：
# 1. 文档分块：把长文档切成小块
# 2. 向量化：把每个小块转换成向量（embedding）
# 3. 存储：把向量存起来
# 4. 检索：用户问问题 → 转成向量 → 找最相似的 k 个块
# 5. 生成：把检索到的块 + 用户问题 → 发给 LLM → 生成回答
# 
# 今天的目标：不用 LangChain，自己实现 1-4 步。

# In[138]:


# Cell 1: 文档分块
from pathlib import Path
from typing import List
import re

def chunk_document(text: str, chunk_size: int = 200, overlap: int = 20) -> List[str]:
    """
    将文档切成小块

    Args:
        text: 原始文本
        chunk_size: 每块最大字符数
        overlap: 块之间的重叠字符数

    Returns:
        文本块列表
    """
    result = []  # ← 初始化结果列表

    # 按句子分割（保留标点符号）
    sentences = re.split(r'([。！？])', text)

    # 合并标点和前面的句子
    merged = []
    for i in range(0, len(sentences) - 1, 2):
        if i + 1 < len(sentences):
            merged.append(sentences[i] + sentences[i+1])

    # 按 chunk_size 分块
    current_chunk = ""
    for sentence in merged:
        if len(current_chunk) + len(sentence) <= chunk_size:
            current_chunk += sentence
        else:
            if current_chunk:
                result.append(current_chunk.strip())
            current_chunk = sentence

    # 最后一块
    if current_chunk:
        result.append(current_chunk.strip())

    return result  # ← 确保返回 result

# 测试
test_text = """
PyTorch是一个深度学习框架。它由Facebook AI Research开发。
ONNX是一种模型交换格式，可以在不同框架之间转换模型。
TensorRT是NVIDIA的推理加速SDK，可以显著提升推理速度。
LangChain是一个用于开发LLM应用的框架，支持RAG、Agent等。
"""

chunks = chunk_document(test_text, chunk_size=50)
for i, chunk in enumerate(chunks):
    print(f"块 {i+1}: {chunk}")


# In[139]:


# Cell 2: 向量化
from sentence_transformers import SentenceTransformer
import numpy as np

class LocalEmbedder:
    """本地 embedding 模型"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        初始化 embedding 模型

        Args:
            model_name: HuggingFace 模型名称
        """
        # TODO: 加载模型
        self.model = SentenceTransformer(model_name)

    def embed(self, texts: List[str]) -> np.ndarray:
        """
        将文本列表转换成向量

        Args:
            texts: 文本列表

        Returns:
            shape (len(texts), embedding_dim) 的向量矩阵
        """
        # TODO: 自己实现向量化
        embeddings = self.model.encode(texts)
        return embeddings

# 测试
embedder = LocalEmbedder()
test_texts = ["你好世界", "Hello World"]
embeddings = embedder.embed(chunks)
print(f"向量形状: {embeddings.shape}")


# In[150]:


from sklearn.metrics.pairwise import cosine_similarity
# Cell 3: 余弦相似度检索
class VectorStore:
    """简单的向量存储和检索"""

    def __init__(self):
        self.chunks = []      # 存储文本块
        self.embeddings = []  # 存储对应的向量

    def add(self, chunks: List[str], embeddings: np.ndarray):
        """
        添加文档块和对应的向量

        Args:
            chunks: 文本块列表
            embeddings: 向量矩阵 (n_chunks, dim)
        """
        # TODO: 存储 chunks 和 embeddings
        self.chunks.extend(chunks)
        #print(embeddings.shape)
        self.embeddings.extend(embeddings)
        #print(np.array(self.embeddings).shape)

    def search(self, query: str, embedder: LocalEmbedder, k: int = 3) -> List[tuple]:
        """
        检索最相似的 k 个文档块

        Args:
            query: 查询文本
            embedder: embedding 模型
            k: 返回数量

        Returns:
            [(chunk, score), ...] 按相似度降序排列
        """
        # TODO: 自己实现余弦相似度计算
        # 提示：
        # 1. 把 query 转成向量
        embeddings = embedder.embed([query])[0]
        # 2. 计算 query 向量和所有存储向量的余弦相似度
        #print(len(embeddings))
        cos_sim = cosine_similarity(np.array(embeddings).reshape(1, -1), np.array(self.embeddings))[0]
        # 3. 返回 top-k
        #print(cos_sim.shape)
        top_indices = np.argsort(cos_sim)[::-1][:k]
        #print(cos_sim)
        #print(cos_sim[idx])
        #print(self.chunks)
        results = []
        for idx in top_indices:
            results.append((self.chunks[idx], cos_sim[idx]))
        return results


# 测试
vector_store = VectorStore()
vector_store.add(chunks, embeddings)  # 使用任务4的 embeddings

query = "什么是TensorRT？"
results = vector_store.search(query, embedder, k=2)
#print(results)
for chunk, score in results:
    #print(chunk, score)
    print(f"相似度: {score:.4f} | {chunk}")


# In[151]:


# Cell 4: 完整的 RAG 系统
import requests
import os
from openai import OpenAI

class SimpleRAG:
    """自己实现的 RAG 系统"""

    def __init__(self, embedder: LocalEmbedder, vector_store: VectorStore):
        self.embedder = embedder
        self.vector_store = vector_store
        self.api_key = os.environ.get('DEEPSEEK_API_KEY')

    def build_knowledge_base(self, documents: List[str]):
        """
        从文档构建知识库

        Args:
            documents: 文档文本列表
        """
        # TODO: 
        # 1. 对每个文档分块
        chunks = []
        for text in documents:
            chunks.extend(chunk_document(text, chunk_size=50))

        # 2. 向量化所有块
        embeddings = self.embedder.embed(chunks)
        # 3. 存入 vector_store
        self.vector_store.add(chunks, embeddings)

    def ask(self, question: str, k: int = 3) -> str:
        """
        问问题

        Args:
            question: 用户问题
            k: 检索数量

        Returns:
            生成的回答
        """
        # TODO:
        # 1. 检索相关的文档块
        results = vector_store.search(question, self.embedder, k)
        #print(results)
        chunks, _ = zip(*results)
        # 2. 构造 prompt
        prompt = """

        你是一个有用的文档检索助手。请用并且只用下面的信息来回答问题。

        相关文档资料：{chunks}
        """
        final_prompt = prompt.format(
            chunks = chunks
        )
        #print(final_prompt)
        # 3. 调用 LLM API
        client = OpenAI(
        api_key=self.api_key, 
        base_url="https://api.deepseek.com"
        )
        response = client.chat.completions.create(
        model="deepseek-chat",  # Use 'deepseek-chat' for V3 or 'deepseek-reasoner' for R1
        messages=[
        {"role": "system", "content": final_prompt},
        {"role": "user", "content": question},
        ],
        stream=False
        )
        #print(response)
        # 4. 返回回答
        return response.choices[0].message.content

# 测试
documents = [
    "PyTorch是一个深度学习框架，由Facebook开发。",
    "ONNX是一种模型交换格式，可以在PyTorch和TensorFlow之间转换模型。",
    "TensorRT是NVIDIA的推理加速SDK，可以提升GPU上的推理速度。",
    "RAG（检索增强生成）结合了信息检索和文本生成。"
]

rag = SimpleRAG(embedder, vector_store)
rag.build_knowledge_base(documents)

answer = rag.ask("什么是TensorRT？")
print(f"回答: {answer}")


# In[152]:


# Cell 5: 完整测试
test_questions = [
    "PyTorch是什么？",
    "ONNX有什么用？",
    "TensorRT能做什么？",
    "RAG是什么？"
]

for q in test_questions:
    print(f"\n问题: {q}")
    answer = rag.ask(q, k=2)
    print(f"回答: {answer}")

