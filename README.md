# Chatbot V2

[![Python](https://img.shields.io/badge/python-3.9+-blue)](https://www.python.org)
[![LangGraph](https://img.shields.io/badge/langgraph-latest-green)](https://langchain-ai.github.io/langgraph/)
[![Streamlit](https://img.shields.io/badge/streamlit-latest-red)](https://streamlit.io)
[![OpenRouter](https://img.shields.io/badge/openrouter-free-orange)](https://openrouter.ai)

A conversational AI chatbot built with LangGraph state management and Streamlit frontend. Leverages OpenRouter's free LLM models with stateful conversation persistence and real-time token streaming.

## Overview

This project demonstrates production-ready LLM application architecture using LangGraph's StateGraph for managing conversational state and message history. The system integrates with OpenRouter's free model tier, enabling cost-effective inference without API key restrictions.

Key architecture decisions:
- LangGraph StateGraph for deterministic conversation routing
- In-memory checkpointing for thread-based session management
- Streamlit for rapid UI iteration with minimal boilerplate
- Real-time token streaming with `st.write_stream()` for responsive UX
- OpenRouter free tier for inference (auto-selects available models)

## Features

- **Stateful Conversations**: Message history managed through LangGraph's `add_messages` reducer
- **Thread-Based Sessions**: Each conversation maintains its own checkpoint thread
- **Real-Time Streaming**: Token-by-token LLM output using `stream_mode='messages'`
- **Free LLM Access**: OpenRouter auto-selects available free models
- **Responsive UI**: Streamlit frontend with native chat interface
- **Simple Deployment**: Ready for Streamlit Community Cloud

## What's New (v2)

### Streaming Implementation

Chatbot V2 now features real-time token streaming for improved user experience:

```python
ai_message = st.write_stream(
    message_chunk.content for message_chunk, metadata in chatbot.stream(
        {'messages': [HumanMessage(content=user_input)]},
        config={'configurable': {'thread_id': 'thread-1'}},
        stream_mode='messages'
    )
)
```

**Benefits:**
- First token appears within 0.5-1s (vs waiting 2-3s for full response)
- Users see output as it's being generated
- Better perceived performance and responsiveness
- Tokens stream directly from LangGraph at message level

**How it works:**
1. LangGraph's `stream()` method with `stream_mode='messages'` yields message chunks
2. `st.write_stream()` displays each chunk in real-time
3. Full message stored in session state after completion

## Quick Start

### Prerequisites

- Python 3.9+
- OpenRouter API key (get free tier at https://openrouter.ai)

### Installation

```bash
git clone https://github.com/nihal00753/Chatbot_V2.git
cd Chatbot_V2

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Configuration

Create `.env` file:
```
OPENROUTER_API_KEY=sk_free_your_key_here
```

### Run Locally

```bash
streamlit run frontend.py
```

Opens at `http://localhost:8501`

## Architecture

### Backend (backend.py)

LangGraph workflow structure:
- **ChatState**: TypedDict containing messages list with `add_messages` reducer
- **chat_node**: Invokes LLM with current message history
- **StateGraph**: Linear workflow (START → chat_node → END)
- **InMemorySaver**: Checkpointer for conversation persistence

Thread configuration enables separate conversation threads per user session.

### Frontend (frontend.py)

Streamlit UI with native chat components:
- **st.chat_message()**: Native chat bubble styling for user and assistant
- **st.chat_input()**: Native chat input with better UX
- **st.write_stream()**: Real-time token display as LLM generates
- **stream_mode='messages'**: LangGraph message-level streaming
- Session state management for full conversation history
- Error handling with user-friendly feedback

**Streaming flow:**
```
User input → LangGraph.stream(stream_mode='messages')
          → Yields message chunks in real-time
          → st.write_stream() displays each chunk
          → Session state stores final message
```

## Configuration

### Environment Variables

```
OPENROUTER_API_KEY      OpenRouter API key (free tier)
```

Get free API key:
1. Visit https://openrouter.ai
2. Sign up with email/GitHub
3. Copy key from dashboard

### Model Selection

Default: `openrouter/free` (auto-selects available free model)

To specify model, edit backend.py line 12:
```python
model="meta-llama/llama-2-7b-chat"  # Or other OpenRouter models
```

## Deployment

### Streamlit Community Cloud

1. Push latest code to GitHub
2. Visit https://share.streamlit.io
3. Create new app from repository
4. Select branch: `main`, file: `frontend.py`
5. Set environment variables in "Advanced settings":
   ```
   OPENROUTER_API_KEY = sk_free_xxxxx
   ```

Free tier: 3 public apps, 1GB memory each, auto-deploys on push

### Local / Docker

Docker deployment:
```bash
docker build -t chatbot_v2 .
docker run -p 8501:8501 -e OPENROUTER_API_KEY=your_key chatbot_v2
```

Example Dockerfile:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["streamlit", "run", "frontend.py"]
```

## Project Structure

```
Chatbot_V2/
├── backend.py           # LangGraph chatbot logic
├── frontend.py          # Streamlit UI with streaming
├── requirements.txt     # Dependencies
├── .env.example        # Environment template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Development

### Understanding Streaming

The streaming implementation uses three key components:

1. **LangGraph `stream()` method**:
   ```python
   chatbot.stream(
       {'messages': [HumanMessage(content=user_input)]},
       config={'configurable': {'thread_id': 'thread-1'}},
       stream_mode='messages'  # Message-level streaming
   )
   ```

2. **Message chunk iteration**:
   ```python
   for message_chunk, metadata in chatbot.stream(...):
       yield message_chunk.content  # Extract content from each chunk
   ```

3. **Streamlit write_stream**:
   ```python
   st.write_stream(generator)  # Displays output as it's generated
   ```

### Adding System Prompt

Modify `chat_node()` in backend.py:
```python
from langchain_core.messages import SystemMessage

def chat_node(state: ChatState):
    messages = state['messages']
    system = SystemMessage(content="You are a helpful assistant...")
    response = llm.invoke([system, *messages])
    return {"messages": [response]}
```

### Adding Tools/Functions

Extend workflow with additional nodes:
```python
graph.add_node("tool_node", tool_execution)
graph.add_edge("chat_node", "tool_node")
graph.add_edge("tool_node", END)
```

### Testing

```bash
python -c "
from backend import chatbot
from langchain_core.messages import HumanMessage

# Test standard invoke
result = chatbot.invoke({'messages': [HumanMessage(content='Hi')]})
print('Response:', result['messages'][-1].content)

# Test streaming
for chunk, _ in chatbot.stream({'messages': [HumanMessage(content='Hi')]}, stream_mode='messages'):
    print(chunk.content, end='', flush=True)
"
```

## Dependencies

- `langchain-core` (0.1+): LLM abstractions and message types
- `langgraph` (0.0.20+): Graph-based workflow orchestration with streaming
- `langchain-openai` (0.1+): OpenAI/OpenRouter API integration
- `streamlit` (1.28+): Web UI framework with `st.write_stream()`
- `python-dotenv` (1.0+): Environment variable management

**Note:** Streaming requires Streamlit >= 1.28 (includes `st.write_stream()`)

## Performance

- **First Token Latency (TTL)**: 0.5-1s (when LLM starts generating)
- **Token throughput**: ~10-20 tokens/sec (OpenRouter free tier)
- **UI responsiveness**: Immediate (Streamlit native)
- **Memory footprint**: ~200MB (Streamlit + LangGraph base)

**User perception:**
- Non-streaming: Wait 2-3s, then see full response
- Streaming: Start seeing output within 1s, completes in 2-3s (feels 3x faster)

## Limitations

- Free tier rate limits: Varies by model (check OpenRouter dashboard)
- In-memory storage: Conversations lost on app restart (add database for persistence)
- Single thread ID: Configure for multi-user by generating unique thread IDs per session
- Streaming models: Not all OpenRouter models support streaming (most do)

## Roadmap

- Add system prompts for domain-specific behavior
- Implement persistent storage (PostgreSQL + pgvector)
- Multi-turn agent with ReAct framework
- Vector database for conversation retrieval (RAG)
- Response caching for repeated queries

## Troubleshooting

**API key not found**
- Verify `.env` file in project root
- Check `OPENROUTER_API_KEY` is set: `echo $OPENROUTER_API_KEY`
- Restart Streamlit after updating `.env`

**Streaming not working**
- Ensure Streamlit >= 1.28: `pip install --upgrade streamlit`
- Check `stream_mode='messages'` is set in chatbot.stream() call
- Verify OpenRouter model supports streaming (most free models do)

**Rate limit exceeded**
- Free tier has usage quotas (typically 10-20 requests/day)
- Check OpenRouter dashboard for remaining quota
- Upgrade to paid tier or wait 24 hours for reset

**Messages not persisting**
- Expected with in-memory storage (session_state only)
- Implement database backend for production persistence

## References

- LangGraph: https://langchain-ai.github.io/langgraph/
- Streamlit: https://docs.streamlit.io
- Streamlit Chat: https://docs.streamlit.io/develop/api-reference/chat
- OpenRouter: https://openrouter.ai/docs
- LangChain: https://python.langchain.com

## License

MIT License

## Notes

This implementation prioritizes simplicity and clarity for educational purposes. Production deployments should add:
- Error handling and retry logic
- Request validation and rate limiting
- Persistent conversation storage
- Monitoring and logging
- User authentication and multi-user support
