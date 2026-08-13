import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage

st.set_page_config(page_title="Chat", page_icon="💬", layout="centered")

st.markdown("""
<style>
    .user-msg { text-align: right; padding: 0.5rem 0; }
    .user-msg > div { background: #667eea; color: white; padding: 0.75rem 1rem; border-radius: 18px; width: fit-content; margin-left: auto; }
    .ai-msg { padding: 0.5rem 0; }
    .ai-msg > div { background: #f0f2f5; color: #222; padding: 0.75rem 1rem; border-radius: 18px; width: fit-content; }
</style>
""", unsafe_allow_html=True)

st.title("ChatBot")

CONFIG = {'configurable': {'thread_id': 'thread-1'}}

if 'messages' not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    if msg['role'] == 'user':
        st.markdown(f'<div class="user-msg"><div>{msg["content"]}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="ai-msg"><div>{msg["content"]}</div></div>', unsafe_allow_html=True)

# Chat input
user_input = st.chat_input("Type message...")

if user_input:
    # Add user message
    st.session_state.messages.append({'role': 'user', 'content': user_input})
    st.markdown(f'<div class="user-msg"><div>{user_input}</div></div>', unsafe_allow_html=True)
    
    # Get AI response
    with st.spinner("Thinking..."):
        response = chatbot.invoke({'messages': [HumanMessage(content=user_input)]}, config=CONFIG)
        ai_msg = response['messages'][-1].content
        st.session_state.messages.append({'role': 'assistant', 'content': ai_msg})
        st.markdown(f'<div class="ai-msg"><div>{ai_msg}</div></div>', unsafe_allow_html=True)
    
    st.rerun()