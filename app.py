import streamlit as st
from agent.react_agent import ReactAgent

st.title("智能客服")
st.divider()

if "agent" not in st.session_state:
    st.session_state["agent"] = ReactAgent()

if "message" not in st.session_state:
    st.session_state["message"] = []

for message in st.session_state["message"]:
    st.chat_message(message["role"]).write(message["content"])

# 用户输入
question = st.chat_input()
if question:
    st.chat_message("user").write(question)
    st.session_state["message"].append({"role": "user", "content": question})

    response_messages = []
    with st.spinner("思考中..."):
        res_stream = st.session_state["agent"].execute_stream(question)

        def capture(generator, cache_list): # 迭代器处理一遍之后就会失效
            for chunk in generator:
                cache_list.append(chunk)
                yield chunk

        st.chat_message("assistant").write_stream(capture(res_stream, response_messages))
        st.session_state["message"].append({"role": "assistant", "content": response_messages[-1]})
        st.rerun()