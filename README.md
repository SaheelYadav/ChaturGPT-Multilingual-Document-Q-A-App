# 🧠 ChaturGPT – AI Assistant for Your Own Data

**ChaturGPT** is an open-source, customizable AI assistant that lets you chat with your own documents, datasets, and knowledge base — in a secure, offline-friendly environment. Built with LlamaIndex, LangChain, and GPT4All, it aims to empower users with private, intelligent search over local data using natural language queries.

---

## 🚀 Project Goal

To build an AI assistant that:
- Understands and answers questions based on user-uploaded documents
- Runs on local or open-source LLMs without relying on commercial APIs
- Supports multilingual Indian languages (future scope)
- Is lightweight, community-driven, and privacy-respecting

---

## 🧩 Tech Stack

| Component         | Technology                     |
|------------------|--------------------------------|
| LLM Interface     | LlamaIndex + LangChain         |
| Language Model    | GPT4All (local inference)      |
| Frontend          | Streamlit                      |
| Backend           | Python                         |
| Data Storage      | File-based vector index (FAISS)|
| Deployment        | HuggingFace / Local Server     |

---

## 📦 Features

- 🔍 Natural language querying over PDFs, text, and web links
- 💾 Works offline with open-source LLMs (GPT4All)
- 🧠 RAG architecture using LangChain & LlamaIndex
- 🧑‍💻 Streamlit-based web UI
- 📚 Document ingestion, parsing & chunking
- 🌐 Ready for multilingual support (future scope)

---

## 📁 Folder Structure

```bash
chaturgpt/
├── data/                # Uploaded documents
├── app/                 # Core backend logic
│   ├── loader.py
│   ├── vector_store.py
│   └── chat_engine.py
├── streamlit_app.py     # UI entry point
├── requirements.txt
├── README.md
└── docs/
    └── user_acquisition.md

🔧 SET UP INSTRUCTUIONS

git clone https://code.swecha.org/SaheelYadav06/chaturgpt.git
cd chaturgpt
pip install -r requirements.txt
streamlit run streamlit_app.py

