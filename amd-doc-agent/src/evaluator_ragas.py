# evaluator_ragas.py
import os
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_openai import ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings

from retriever import get_retriever, search
from chain import build_rag_chain, ask
from embedder import load_vectorstore

TEST_CASES = [
    {
        "question": "什么是 PDI？",
        "ground_truth": "PDI 是可编程器件映像，用于描述 Versal 引导分区与加载顺序。"
    },
    {
        "question": "什么是 Bootgen 工具？",
        "ground_truth": "Bootgen 是用于生成引导镜像（boot image）的工具，支持 AMD 的 Zynq、Zynq UltraScale+ 和 Versal 设备。"
    },
    {
        "question": "Bootgen 生成的输出文件是什么？",
        "ground_truth": "Bootgen 生成的输出文件是引导镜像，例如 BOOT.BIN 或 Versal 设备使用的 PDI 文件。"
    },
    {
        "question": "BIF 文件的主要作用是什么？",
        "ground_truth": "BIF 文件用于描述引导镜像的内容和结构，包括分区及其顺序，是 Bootgen 的输入文件之一。"
    },
    {
        "question": "Bootgen 支持哪些输入文件类型？",
        "ground_truth": "Bootgen 支持多种输入文件类型，包括 ELF 文件、bitstream 文件、二进制文件以及其他数据文件。"
    },
    {
        "question": "如何在 BIF 文件中定义分区？",
        "ground_truth": "在 BIF 文件中通过添加分区条目（partition entries）按顺序列出各个文件来定义分区。"
    },
    {
        "question": "Bootgen 如何处理加密和认证？",
        "ground_truth": "Bootgen 支持对引导镜像进行加密和认证，通过在 BIF 文件中指定相关属性并使用密钥实现安全启动。"
    },
    {
        "question": "Bootgen 命令行的基本用法是什么？",
        "ground_truth": "Bootgen 通常通过命令行使用，例如指定 -image 输入 BIF 文件、-arch 指定架构以及 -o 指定输出文件。"
    },
    {
        "question": "如何在 BIF 文件中指定启动设备？",
        "ground_truth": "可以在 BIF 文件中通过相关配置项指定启动设备，以控制引导镜像的加载方式。"
    },
    {
        "question": "Bootgen 支持哪些架构？",
        "ground_truth": "Bootgen 支持 Zynq、Zynq UltraScale+ 和 Versal 等架构。"
    },
    {
        "question": "BIF 文件中 attributes 的作用是什么？",
        "ground_truth": "attributes 用于指定分区属性，例如加载地址、执行方式以及安全相关设置。"
    },
]

def run_ragas_evaluation():
    # 1. 初始化
    vs = load_vectorstore()
    retriever = get_retriever(vs)
    chain = build_rag_chain(retriever, vs)
    
    questions, answers, contexts, ground_truths = [], [], [], []
    
    for case in TEST_CASES:
        q = case["question"]
        
        # 方案B：分两步
        # TODO: 第一步，用 search() 拿到 chunks
        chunks = search(vs, q, 4)
        # TODO: 第二步，用 ask() 拿到回答
        answer = ask(chain, q)
        # TODO: 把 chunk 的 page_content 提取成字符串列表
        chunk_texts = [chunk_text.page_content for chunk_text in chunks]
        
        questions.append(q)
        answers.append(answer)
        contexts.append(chunk_texts)
        ground_truths.append(case["ground_truth"])
    
    # 2. 构建 dataset
    dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    })
    
    # 3. 配置 RAGAS
    # TODO: 初始化 llm 和 embeddings
    llm = LangchainLLMWrapper(ChatOpenAI(
        model="deepseek-chat",
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",
        n=1
    ))
    embeddings = LangchainEmbeddingsWrapper(HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cuda'},  # Use 'cuda' if you have GPU
        encode_kwargs={'normalize_embeddings': True},
    ))
    
    # 4. 运行评估
    result = evaluate(
        dataset,
        metrics=[faithfulness, context_precision],
        llm=llm,
        embeddings=embeddings
    )
    
    print(result)
    return result

if __name__ == "__main__":
    run_ragas_evaluation()