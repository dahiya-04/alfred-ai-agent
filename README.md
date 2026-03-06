# alfred-ai-agent
Alfred AI is a LangGraph-based conversational agent powered by a local LLM (Ollama) that can retrieve structured data, search the web for unknown information, fetch recent news, and maintain conversation memory.

Inspired by Batman’s trusted assistant Alfred, the system acts as a smart conversational aide capable of helping users prepare conversations with guests by retrieving background information, suggesting discussion topics, and providing the latest updates.

The project demonstrates how to build modern AI agents using tools, retrieval-augmented generation (RAG), and conversation memory.

🚀 Features

🧠 Conversation Memory
Maintains multi-turn conversation using LangGraph checkpointing.

🔎 Hybrid Retrieval (RAG)
Retrieves guest information from a dataset using a retriever.

🌐 Web Search Tool
Looks up information for guests not present in the local dataset.

📰 Latest News Tool
Fetches recent news about a person or topic.

🧰 Tool-Using Agent
The LLM decides when to call tools instead of hallucinating answers.

⚡ Local LLM
Runs entirely locally using Ollama, without relying on cloud APIs.


User
 ↓
LangGraph Agent
 ↓
Conversation Memory (Checkpointer)
 ↓
Assistant Node (LLM)
 ↓
Tool Router
 ├── Guest Retriever Tool (RAG)
 ├── Web Search Tool
 └── News Tool
 ↓
Local LLM (Ollama)


alfred-ai-agent/
│
├── app.py            # Main chatbot application
├── tools.py          # Tool implementations (retriever, web search, news)
├── retriever.py      # Dataset loading and retrieval logic
│
└── README.md
