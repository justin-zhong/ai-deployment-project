import streamlit as st
import os
from src.loader import load_documents, split_documents
from src.embedder import build_vectorstore, load_vectorstore
from src.retriever import get_retriever
from src.chain import build_rag_chain, ask
from src.evaluator import evaluate, print_report

st.set_page_config(page_title="📚 知识库问答", layout="centered")
st.title("📚 个人知识库问答机器人")
st.caption("把你的文档放进 data/ 目录，然后开始提问")

with st.sidebar:
    st.header("⚙️ 初始化")

    if st.button("🔄 加载并索引文档", use_container_width=True):
        if not os.listdir("data"):
            st.error("data/ 目录是空的，请先放入 PDF 或 TXT 文件")
        else:
            with st.spinner("正在处理文档..."):
                docs = load_documents("data")
                chunks = split_documents(docs)
                st.session_state.chunks = chunks
                vectorstore = build_vectorstore(chunks)
                st.session_state.vectorstore = vectorstore
            st.success(f"✅ 已索引 {len(chunks)} 个片段")
    if "vectorstore" not in st.session_state:
        vs = load_vectorstore()
        if vs:
            st.session_state.vectorstore = vs
            st.info("已加载本地向量库")
    if st.button("运行评估", use_container_width=True):
        with st.spinner(""):
            retriever = get_retriever(st.session_state.vectorstore, st.session_state.chunks)
            chain = build_rag_chain(retriever, st.session_state.vectorstore, st.session_state.chunks)
            test_report = evaluate(chain)
            print_report(test_report)
        st.success(f"✅ 已运行评估")
    st.divider()
    st.markdown("**使用步骤**")
    st.markdown("1. 把文档放入 `data/` 目录")
    st.markdown("2. 点击「加载并索引文档」")
    st.markdown("3. 在右侧输入问题")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if question := st.chat_input("请输入你的问题..."):
    if "vectorstore" not in st.session_state:
        st.error("请先在左侧初始化文档")
    else:

        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                retriever = get_retriever(st.session_state.vectorstore, st.session_state.chunks)
                chain = build_rag_chain(retriever, st.session_state.vectorstore, st.session_state.chunks)
                answer = ask(chain, question)
            st.write(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
