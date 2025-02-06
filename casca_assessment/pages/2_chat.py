import streamlit as st
from streamlit_chat import message
from langchain_ollama import OllamaLLM


st.title("💬 Chat with Bank Statement AI")

if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

for idx, chat_message in enumerate(st.session_state.chat_messages):
    message(chat_message['content'], 
            is_user=(chat_message['role'] == 'user'), 
            key=f"chat_{idx}")

user_input = st.chat_input("Ask a question about your bank statement...")

if user_input:
    st.session_state.chat_messages.append({
        "role": "user",
        "content": user_input
    })
    
    llm = OllamaLLM(model="gemma2:9b", num_ctx=8192)
    
    

    response = llm.invoke(f'{user_input}\n\n{st.session_state["chat_file"]}')
    print(st.session_state["chat_file"])
    st.session_state.chat_messages.append({
        "role": "bot",
        "content": response
    })
    
    st.rerun()