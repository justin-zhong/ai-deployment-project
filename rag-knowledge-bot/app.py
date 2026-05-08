"""
app.py - 主入口

运行方式：
    streamlit run app.py
"""

import streamlit as st
import os
from src.loader import load_documents, split_documents
from src.embedder import build_vectorstore, load_vectorstore
from src.retriever import get_retriever
from src.chain import build_rag_chain, ask
from src.evaluator import evaluate, print_report

# ---- 页面配置 ----
st.set_page_config(page_title="📚 知识库问答", layout="centered")
st.title("📚 个人知识库问答机器人")
st.caption("把你的文档放进 data/ 目录，然后开始提问")

# ---- 侧边栏：初始化 ----
with st.sidebar:
    st.header("⚙️ 初始化")

    if st.button("🔄 加载并索引文档", use_container_width=True, type="primary"):
        if not os.listdir("data"):
            st.error("data/ 目录是空的，请先放入 PDF 或 TXT 文件")
        elif not os.listdir("data"):
            st.error("data/ 目录是空的，请先放入 PDF 或 TXT 文件")
        else:
            with st.spinner("正在处理文档..."):
                try:
                    docs = load_documents("data")
                    if not docs:
                        st.error("未找到任何可读文档，请检查文件格式")
                    else:
                        chunks = split_documents(docs)
                        if not chunks:
                            st.error("文档分割失败")
                        else:
                            vectorstore = build_vectorstore(chunks)
                            st.session_state.vectorstore = vectorstore
                            st.session_state.vectorstore_status = "loaded"
                            st.session_state.retriever = get_retriever(vectorstore)
                            st.session_state.chain = build_rag_chain(st.session_state.retriever)
                            st.success(f"✅ 已索引 {len(chunks)} 个片段")
                except Exception as e:
                    st.error(f"❌ 索引失败: {str(e)}")
                    st.session_state.vectorstore_status = "error"

    if "vectorstore" not in st.session_state and "load_attempted" not in st.session_state:
        st.session_state.load_attempted = True
        vs = load_vectorstore()
        if vs:
            st.session_state.vectorstore = vs
            st.session_state.vectorstore_status = "loaded"
            st.session_state.retriever = get_retriever(vs)
            st.session_state.chain = build_rag_chain(st.session_state.retriever)
            st.success("✅ 已加载本地向量库")
        else:
            st.session_state.vectorstore = None
            st.session_state.vectorstore_status = "not_found"
            st.info("💡 点击上方按钮创建向量库")
            
    status = st.session_state.get("vectorstore_status")
    if status == "loaded":
        st.success("✅ 向量库已就绪")
    elif status == "not_found":
        st.info("📚 点击上方按钮创建向量库")
    elif status == "error":
        st.error("❌ 向量库加载失败，请重试")
        
    if st.button("运行评估", use_container_width=True):
        if not st.session_state.get("vectorstore"):
            st.error("❌ 请先加载文档后再运行评估")
        else:
            with st.spinner("正在运行评估..."):
                try:
                    if "chain" not in st.session_state:
                        retriever = get_retriever(st.session_state.vectorstore)
                        st.session_state.chain = build_rag_chain(retriever)
                        
                    test_report = evaluate(st.session_state.chain)
                    print_report(test_report)
                    st.success(f"✅ 已运行评估")

                    with st.expander("查看评估结果详情"):
                        st.json(test_report)
                except Exception as e:
                    st.error(f"❌ 评估失败: {str(e)}")
        
    st.divider()
    st.markdown("**使用步骤**")
    st.markdown("1. 把文档放入 `data/` 目录")
    st.markdown("2. 点击「加载并索引文档」")
    st.markdown("3. 在右侧输入问题")

    st.markdown("**💡 支持格式**")
    st.markdown("- PDF (.pdf)")
    st.markdown("- 文本文件 (.txt)")
    
# ---- 主界面：问答 ----
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if question := st.chat_input("请输入你的问题..."):
    if not st.session_state.get("vectorstore"):
        st.error("❌ 请先在左侧初始化文档")
    else:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("🤔 思考中..."):
                try:
                    if "chain" not in st.session_state:
                        retriever = get_retriever(st.session_state.vectorstore)
                        st.session_state.chain = build_rag_chain(retriever)
                    answer = ask(st.session_state.chain, question)
                    st.write(answer)
                except Exception as e:
                    error_msg = f"❌ 生成回答失败: {str(e)}"
                    st.error(error_msg)
                    answer = error_msg

        st.session_state.messages.append({"role": "assistant", "content": answer})