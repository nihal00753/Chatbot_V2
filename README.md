# Chatbot V2

[![Python](https://img.shields.io/badge/python-3.9+-blue)](https://www.python.org)
[![LangGraph](https://img.shields.io/badge/langgraph-latest-green)](https://langchain-ai.github.io/langgraph/)
[![Streamlit](https://img.shields.io/badge/streamlit-latest-red)](https://streamlit.io)
[![OpenRouter](https://img.shields.io/badge/openrouter-free-orange)](https://openrouter.ai)

A conversational AI chatbot built with LangGraph state management and Streamlit frontend. Leverages OpenRouter's free LLM models with stateful conversation persistence.

## Overview

This project demonstrates production-ready LLM application architecture using LangGraph's StateGraph for managing conversational state and message history. The system integrates with OpenRouter's free model tier, enabling cost-effective inference without API key restrictions.

Key architecture decisions:
- LangGraph StateGraph for deterministic conversation routing
- In-memory checkpointing for thread-based session management
- Streamlit for rapid UI iteration with minimal boilerplate
- OpenRouter free tier for inference (auto-selects available models)

## Features

- **Stateful Conversations**: Message history managed through LangGraph's `add_messages` reducer
- **Thread-Based Sessions**: Each conversation maintains its own checkpoint thread
- **Free LLM Access**: OpenRouter auto-selects available free models
- **Responsive UI**: Streamlit frontend with custom styling
- **Simple Deployment**: Ready for Streamlit Community Cloud

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

Streamlit UI with:
- Custom CSS chat bubbles (user: gradient blue, assistant: gray)
- Session state management for message history
- `st.chat_input()` for native Streamlit chat interface
- Loading indicator during LLM inference
- Responsive layout

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

1. Push to GitHub
2. Visit https://share.streamlit.io
3. Create new app from repository
4. Set `OPENROUTER_API_KEY` in Advanced settings

Free tier: 3 public apps, 1GB memory each

### Local / Docker

Docker deployment:
```bash
docker build -t chatbot_v2 .
docker run -p 8501:8501 -e OPENROUTER_API_KEY=your_key chatbot_v2
```

## Project Structure

```
Chatbot_V2/
├── backend.py           # LangGraph chatbot logic
├── frontend.py          # Streamlit UI
├── requirements.txt     # Dependencies
├── .env.example        # Environment template
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

## Development

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
result = chatbot.invoke({'messages': [HumanMessage(content='Hi')]})
print(result['messages'][-1].content)
"
```

## Dependencies

- `langchain-core` (0.1+): LLM abstractions and message types
- `langgraph` (0.0.20+): Graph-based workflow orchestration
- `langchain-openai` (0.1+): OpenAI/OpenRouter API integration
- `streamlit` (1.28+): Web UI framework
- `python-dotenv` (1.0+): Environment variable management

## Performance

- LLM inference: Depends on OpenRouter model (typical: 1-3s per response)
- UI responsiveness: Immediate (Streamlit native)
- Memory footprint: ~200MB (Streamlit + LangGraph base)

## Limitations

- Free tier rate limits: Varies by model (check OpenRouter dashboard)
- In-memory storage: Conversations lost on app restart
- Single thread ID: Configure for multi-user by generating unique thread IDs per session

## Roadmap

- Add system prompts for domain-specific behavior
- Implement persistent storage (PostgreSQL + pgvector)
- Add streaming responses for real-time output
- Multi-turn agent with ReAct framework
- Vector database for conversation retrieval (RAG)

## Troubleshooting

**API key not found**
- Verify `.env` file in project root
- Check `OPENROUTER_API_KEY` is set
- Restart Streamlit after updating `.env`

**Rate limit exceeded**
- Free tier has usage quotas
- Check OpenRouter dashboard for current limits
- Upgrade to paid tier or wait 24 hours

**Messages not persisting**
- Expected with in-memory storage
- Implement database backend for production

## References

- LangGraph: https://langchain-ai.github.io/langgraph/
- Streamlit: https://docs.streamlit.io
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
- User authentication
