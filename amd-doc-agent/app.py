import streamlit as st
import os
import requests


API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(page_title="📚 知识库问答", layout="centered")
st.title("📚 个人知识库问答机器人")
st.caption("基于 AMD 技术文档的智能问答")

with st.sidebar:
    st.header("⚙️ 使用说明")
    st.markdown("**使用步骤**")
    st.markdown("1. 确认 FastAPI 后端已启动")
    st.markdown("2. 确认后端已成功加载向量库")
    st.markdown("3. 在下方输入问题")
    st.divider()
    st.caption("检索、模型调用和缓存由 FastAPI 后端负责。")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if question := st.chat_input("请输入你的问题..."):
        st.session_state.messages.append({"role": "user", "content": question})
        
        with st.chat_message("user"):
            st.write(question)

        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                try:
                    response = requests.post(
                        f"{API_URL}/ask",
                        json={"question": question},
                        timeout=60,
                    )
                    response.raise_for_status()
                    result = response.json()
                    
                    answer = result["answer"]
                    sources = result.get("sources", [])
                    
                    st.write(answer)
                    
                    if sources:
                        with st.expander("参考来源"):
                            for source in sources:
                                st.write(f"- {source}")

                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    
                except requests.HTTPError as exc:
                    status_code = exc.response.status_code
                    st.error(
                        f"后端请求失败（HTTP {status_code}）。"
                        "请检查 FastAPI 日志。"
                    )
                    
                except requests.RequestException:
                    st.error(
                        "无法连接到 FastAPI 后端。"
                        "请确认后端已启动，并检查 API_URL 配置。"
                    )
                
                except (ValueError, KeyError):
                    st.error("后端返回的数据格式不符合预期。")
