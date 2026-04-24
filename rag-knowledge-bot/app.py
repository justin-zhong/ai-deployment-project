"""
app.py - 主入口（UI 已写好，专注实现 src/ 里的逻辑）

运行方式：
    streamlit run app.py
"""

import streamlit as st
import os
from src.loader import load_documents, split_documents
from src.embedder import build_vectorstore, load_vectorstore
from src.retriever import get_retriever
from src.chain import build_rag_chain, ask

# ---- 页面配置 ----
st.set_page_config(page_title="📚 知识库问答", layout="centered")
st.title("📚 个人知识库问答机器人")
st.caption("把你的文档放进 data/ 目录，然后开始提问")

# ---- 侧边栏：初始化 ----
with st.sidebar:
    st.header("⚙️ 初始化")

    if st.button("🔄 加载并索引文档", use_container_width=True):
        if not os.listdir("data"):
            st.error("data/ 目录是空的，请先放入 PDF 或 TXT 文件")
        else:
            with st.spinner("正在处理文档..."):
                docs = load_documents("data")
                chunks = split_documents(docs)
                vectorstore = build_vectorstore(chunks)
                st.session_state.vectorstore = vectorstore
            st.success(f"✅ 已索引 {len(chunks)} 个片段")

    # 尝试加载已有向量库
    if "vectorstore" not in st.session_state:
        vs = load_vectorstore()
        if vs:
            st.session_state.vectorstore = vs
            st.info("已加载本地向量库")

    st.divider()
    st.markdown("**使用步骤**")
    st.markdown("1. 把文档放入 `data/` 目录")
    st.markdown("2. 点击「加载并索引文档」")
    st.markdown("3. 在右侧输入问题")

# ---- 主界面：问答 ----
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# 用户输入
if question := st.chat_input("请输入你的问题..."):
    if "vectorstore" not in st.session_state:
        st.error("请先在左侧初始化文档")
    else:
        # 显示用户消息
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        # 生成回答
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                retriever = get_retriever(st.session_state.vectorstore)
                chain = build_rag_chain(retriever)
                answer = ask(chain, question)
            st.write(answer)

        st.session_state.messages.append({"role": "assistant", "content": answer})
