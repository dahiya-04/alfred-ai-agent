


# 🎩 Alfred AI – A Tool-Using Local AI Assistant

Alfred AI is a **LangGraph-based conversational agent** powered by a **local LLM (Ollama)** that can retrieve structured data, search the web for unknown information, fetch recent news, and maintain conversation memory.

Inspired by **Batman’s trusted assistant Alfred**, the system helps users prepare conversations with guests by retrieving background information, suggesting discussion topics, and providing the latest updates.

This project demonstrates how to build **modern AI agents using tools, retrieval-augmented generation (RAG), and conversation memory**.

---

# 🚀 Features

- 🧠 **Conversation Memory**  
  Maintains multi-turn conversation using LangGraph checkpointing.

- 🔎 **Hybrid Retrieval (RAG)**  
  Retrieves guest information from a dataset using a retriever.

- 🌐 **Web Search Tool**  
  Looks up information for guests not present in the local dataset.

- 📰 **Latest News Tool**  
  Fetches recent news about a person or topic.

- 🧰 **Tool-Using Agent**  
  The LLM decides when to call tools instead of hallucinating answers.

- ⚡ **Local LLM**  
  Runs model inference locally using **Ollama**. Web tools contact external services.

---

# 🏗 System Architecture
User ↓ LangGraph Agent ↓ Memory ↓ Assistant ↓ Tools ↓ LLM

alfred-ai-agent
── app.py # Main chatbot application 

── tool.py # Tool implementations (web search, news and other tools)

── search_provider.py # DuckDuckGo and Parallel Search MCP backends

── retriever.py # Dataset loading and retrieval logic

# 🛠 Tech Stack

- Python
- LangGraph
- LangChain
- Ollama
- HuggingFace Datasets
- BM25 Retriever
- DuckDuckGo Search
- Sentence Transformers (optional upgrade)

## Run Alfred

Use Python 3.11 or newer and an [Ollama](https://ollama.com/) server:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
ollama pull qwen2.5:1.5b
python app.py
```

The first run downloads the guest dataset from Hugging Face. Ollama must be
listening at `http://127.0.0.1:11434`.

### Choose a web-search provider

DuckDuckGo remains the default, with no API key needed. To use free
[Parallel Search MCP](https://docs.parallel.ai/integrations/mcp/search-mcp)
instead, set the provider before starting Alfred:

```bash
ALFRED_SEARCH_PROVIDER=parallel python app.py
```

Parallel's anonymous endpoint uses Fast mode for search and requires no account or
API key. Alfred sends the search query to `https://search.parallel.ai/mcp` over
Streamable HTTP and returns the source excerpts and URLs to the agent's existing
`web_search_tool`. The standalone `latest_news_tool` uses the same backend.
Queries leave your machine; anonymous service limits apply.

Set `ALFRED_SEARCH_PROVIDER=duckduckgo` to select DuckDuckGo explicitly, or
`ALFRED_SEARCH_PROVIDER=disabled` to prevent web-search requests. Invalid provider
names fail at startup. Parallel requests have a 30-second deadline; errors are
returned to the agent without switching providers. Async callers can use
`web_search_tool.ainvoke(...)`, which propagates cancellation to the MCP client.

### Search integration tests

The offline suite needs neither Ollama nor the guest dataset. In a fresh virtual
environment, install the smaller search dependency set and run:

```bash
python -m pip install -r requirements-search.txt
python -m unittest discover -s tests -v
```

These tests exercise the real graph and MCP transport with scripted model
decisions and HTTP responses, including provider selection, result consumption,
errors, timeouts and cancellation.

---
**💬 Example Interaction**


🎩 Alfred: Hello, I am Alfred. How can I assist you today?
Type 'exit' or 'quit' to stop.

You: I wish to know about jacob betal recent performance World Cup , tell me about his recent form . Some point to start a conversations?

🎩 Alfred:
Jacob Bethell's recent form in the World Cup Semi-Final 2026 has been quite impressive.
Despite England's eventual defeat, Jacob Bethell scored 105 runs off 48 balls.

Highlights:
• Century achieved in just 45 balls
• 7 sixes and 8 fours
• One of England’s standout performances

Conversation starters:
• Ask about his aggressive batting approach in T20 cricket
• Discuss England’s emerging young cricket talent
• Talk about the pressure of playing in a World Cup semifinal

----------------------------------------

You: He scored these runs against which team?

🎩 Alfred:
Jacob Bethell scored his 105 runs against the India national cricket team
in the ICC Men's T20 World Cup 2026 Semi-Final.

----------------------------------------

You: who was the captain for England?

🎩 Alfred:
The captain of the England national cricket team was Eoin Morgan during the
2023 ICC Men's T20 World Cup.

----------------------------------------

You: exit
Alfred: Goodbye.


**🎯 Learning Goals**

This project demonstrates key AI engineering concepts:

Tool-using agents

Retrieval-Augmented Generation (RAG)

Conversation memory

Local LLM deployment

Graph-based agent orchestration
