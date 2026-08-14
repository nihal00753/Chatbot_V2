import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage, AIMessage
import uuid

# **************************************** utility functions *************************

def generate_thread_id():
    return uuid.uuid4()

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    st.session_state['chat_threads'][thread_id] = "New Chat"
    st.session_state['message_history'] = []

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])

def get_chat_summary(messages):
    """Generate a name from first user message"""
    for msg in messages:
        if isinstance(msg, HumanMessage):
            summary = msg.content[:30].strip()
            return summary + "..." if len(msg.content) > 30 else summary
    return "New Chat"


# **************************************** Session Setup ******************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = {}

if st.session_state['thread_id'] not in st.session_state['chat_threads']:
    st.session_state['chat_threads'][st.session_state['thread_id']] = "New Chat"


# **************************************** Page Config & Styling **************************

st.set_page_config(page_title="LangGraph Chatbot", page_icon="💬", layout="wide")

st.markdown("""
<style>
    .stChatMessage { padding: 12px 0 !important; }
    .stChatMessage[data-testid="chat-message-user"] { 
        background: rgba(0, 102, 204, 0.05) !important;
        border-left: 3px solid #0066cc;
        padding-left: 16px !important;
    }
    .stChatMessage[data-testid="chat-message-assistant"] { 
        background: rgba(255, 165, 0, 0.04) !important;
        border-left: 3px solid #ff9500;
        padding-left: 16px !important;
    }
    .stText { font-size: 15px; line-height: 1.6; }
    .empty-state { text-align: center; padding: 60px 20px; color: #666; }
</style>
""", unsafe_allow_html=True)


# **************************************** Sidebar UI *********************************

with st.sidebar:
    st.markdown("### 💬 Chat")
    
    if st.button("➕ New Chat", use_container_width=True):
        reset_chat()
        st.rerun()
    
    st.divider()
    st.markdown("**Conversations**")
    
    for thread_id, name in sorted(st.session_state['chat_threads'].items(), key=lambda x: list(st.session_state['chat_threads'].keys()).index(x[0]), reverse=True):
        if st.button(name, use_container_width=True, key=f"thread_{thread_id}"):
            st.session_state['thread_id'] = thread_id
            messages = load_conversation(thread_id)
            
            temp_messages = []
            for msg in messages:
                role = 'user' if isinstance(msg, HumanMessage) else 'assistant'
                temp_messages.append({'role': role, 'content': msg.content})
            
            st.session_state['message_history'] = temp_messages
            st.rerun()


# **************************************** Main UI ************************************

st.markdown("### Chat")

if not st.session_state['message_history']:
    st.markdown("""
    <div class="empty-state">
        <div style="font-size: 48px; margin-bottom: 16px;">💭</div>
        <p><strong>Start a conversation</strong></p>
    </div>
    """, unsafe_allow_html=True)
else:
    for message in st.session_state['message_history']:
        with st.chat_message(message['role'], avatar="👤" if message['role'] == "user" else "🤖"):
            st.text(message['content'])

user_input = st.chat_input("Type a message...")

if user_input:
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    
    # Update chat name from first message
    if st.session_state['chat_threads'][st.session_state['thread_id']] == "New Chat":
        st.session_state['chat_threads'][st.session_state['thread_id']] = get_chat_summary([HumanMessage(content=user_input)])
    
    with st.chat_message("user", avatar="👤"):
        st.text(user_input)
    
    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}
    
    with st.chat_message("assistant", avatar="🤖"):
        def ai_only_stream():
            for message_chunk, metadata in chatbot.stream(
                {"messages": [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode="messages"
            ):
                if isinstance(message_chunk, AIMessage):
                    yield message_chunk.content
        
        ai_message = st.write_stream(ai_only_stream())
    
    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})
    st.rerun()