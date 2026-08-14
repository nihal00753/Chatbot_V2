import streamlit as st
from backend import chatbot, retrieve_all_threads
from langchain_core.messages import HumanMessage
import uuid

# **************************************** utility functions *************************

def generate_thread_id():
    thread_id = uuid.uuid4()
    return thread_id

def reset_chat():
    thread_id = generate_thread_id()
    st.session_state['thread_id'] = thread_id
    add_thread(thread_id)
    st.session_state['message_history'] = []

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)
    if thread_id not in st.session_state['chat_titles']:
        st.session_state['chat_titles'][thread_id] = "New Chat"

def load_conversation(thread_id):
    state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
    # Check if messages key exists in state values, return empty list if not
    return state.values.get('messages', [])

def make_title(text):
    """Turn a raw message into a short, single-line chat title."""
    title = " ".join(text.strip().split())
    if len(title) > 40:
        title = title[:40].rstrip() + "..."
    return title or "New Chat"

def get_thread_title(thread_id):
    """
    Human-friendly name for a thread instead of showing the raw UUID.
    Cached in session_state; derived from the first user message the
    first time a thread's title is needed.
    """
    cached = st.session_state['chat_titles'].get(thread_id)
    if cached and cached != "New Chat":
        return cached

    messages = load_conversation(thread_id)
    for msg in messages:
        if isinstance(msg, HumanMessage) and msg.content.strip():
            title = make_title(msg.content)
            st.session_state['chat_titles'][thread_id] = title
            return title

    st.session_state['chat_titles'][thread_id] = "New Chat"
    return "New Chat"


# **************************************** Page config *********************************

st.set_page_config(
    page_title="LangGraph Chatbot",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Purely visual polish below — no features added or removed.
st.markdown(
    """
    <style>
    /* ---- Sidebar: dark, ChatGPT-style conversation list ---- */
    section[data-testid="stSidebar"] {
        background-color: #171717;
    }
    section[data-testid="stSidebar"] * {
        color: #ececec !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #333333;
    }

    /* Make every sidebar button look like a list row, left-aligned */
    section[data-testid="stSidebar"] .stButton > button {
        width: 100%;
        text-align: left;
        justify-content: flex-start;
        background-color: transparent;
        border: 1px solid transparent;
        border-radius: 8px;
        padding: 0.5rem 0.75rem;
        margin-bottom: 4px;
        font-size: 0.9rem;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background-color: #2a2b2e;
        border-color: #3a3b3e;
    }

    /* New Chat button gets a bit more presence */
    section[data-testid="stSidebar"] .stButton:first-of-type > button {
        border: 1px solid #444444;
        font-weight: 600;
    }

    /* ---- Main chat area ---- */
    [data-testid="stChatMessage"] {
        border-radius: 14px;
        padding: 0.4rem 0.6rem;
        margin-bottom: 0.4rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# **************************************** Session Setup ******************************

if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = retrieve_all_threads()

if 'chat_titles' not in st.session_state:
    st.session_state['chat_titles'] = {}

add_thread(st.session_state['thread_id'])


# **************************************** Sidebar UI *********************************

with st.sidebar:
    st.markdown("### Chatbot")

    if st.button("  New Chat", use_container_width=True):
        reset_chat()
        st.rerun()

    st.markdown("---")
    st.caption("MY CONVERSATIONS")

    for thread_id in st.session_state['chat_threads'][::-1]:
        title = get_thread_title(thread_id)
        is_active = thread_id == st.session_state['thread_id']
        label = f" {title}" if is_active else f" {title}"

        if st.button(label, key=f"thread_{thread_id}", use_container_width=True):
            st.session_state['thread_id'] = thread_id
            messages = load_conversation(thread_id)

            temp_messages = []

            for msg in messages:
                if isinstance(msg, HumanMessage):
                    role = 'user'
                else:
                    role = 'assistant'
                temp_messages.append({'role': role, 'content': msg.content})

            st.session_state['message_history'] = temp_messages
            st.rerun()


# **************************************** Main UI ************************************

st.subheader(get_thread_title(st.session_state['thread_id']))


# loading the conversation history
for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])

user_input = st.chat_input('Type here')

if user_input:

    # first add the message to message_history
    st.session_state['message_history'].append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.text(user_input)

    # name the thread from its first message, same convention used for reloaded threads
    if st.session_state['chat_titles'].get(st.session_state['thread_id'], "New Chat") == "New Chat":
        st.session_state['chat_titles'][st.session_state['thread_id']] = make_title(user_input)

    CONFIG = {
        "configurable": {"thread_id": st.session_state["thread_id"]},
        "metadata": {
            "thread_id": st.session_state["thread_id"]
        },
        "run_name": "chat_turn",
    }

    # first add the message to message_history
    with st.chat_message('assistant'):

        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )

    st.session_state['message_history'].append({'role': 'assistant', 'content': ai_message})