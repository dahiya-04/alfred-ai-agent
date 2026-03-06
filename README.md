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
  Runs entirely locally using **Ollama**, without relying on cloud APIs.

---

# 🏗 System Architecture
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
  Runs entirely locally using **Ollama**, without relying on cloud APIs.

---

# 🏗 System Architecture
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


# 🛠 Tech Stack

- Python
- LangGraph
- LangChain
- Ollama
- HuggingFace Datasets
- BM25 Retriever
- DuckDuckGo Search
- Sentence Transformers (optional upgrade)

---
💬 Example Interaction


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
