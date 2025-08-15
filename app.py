import streamlit as st
import os
import pandas as pd
import pdfplumber
import docx
import re
import chromadb
from chromadb.utils import embedding_functions
from transformers import pipeline
import diskcache as dc
from pathlib import Path

# ===== Config =====
st.set_page_config(
    page_title="🗂️ Chatur GPT – Understand Any Document",
    page_icon="🗂️",
    layout="wide"
)
UPLOAD_DIR = "data"
os.makedirs(UPLOAD_DIR, exist_ok=True)
CACHE_DIR = "chat_cache"

# ===== Session =====
cache = dc.Cache(CACHE_DIR)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = cache.get("history", [])

# ===== Cached Resources =====
@st.cache_resource
def get_embedder():
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name="paraphrase-multilingual-MiniLM-L12-v2"
    )

@st.cache_resource
def get_llm():
    return pipeline("text-generation", model="gpt2", max_length=1024)

# ===== Utilities =====
def extract_text(file_path: Path):
    ext = file_path.suffix.lower()
    text = ""
    if ext == ".pdf":
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                text += page.extract_text() or ""
    elif ext == ".docx":
        docf = docx.Document(file_path)
        text = "\n".join([p.text for p in docf.paragraphs])
    elif ext == ".csv":
        df = pd.read_csv(file_path)
        text = df.to_string(index=False)
    elif ext == ".txt":
        text = file_path.read_text(encoding="utf-8", errors="ignore")
    return text.strip()

def chunk_text(text, chunk_size=800, overlap=200):
    chunks, start = [], 0
    while start < len(text):
        end = min(len(text), start + chunk_size)
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def extract_identifiers(text):
    email = re.search(r'\b[\w\.-]+@[\w\.-]+\.\w+\b', text)
    phone = re.search(r'(\+?\d[\d\-\s]{7,}\d)', text)
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    name = next((l for l in lines if not re.search(r'\d', l) and '@' not in l and len(l.split()) <= 5), "")
    return {
        "name": name,
        "email": email.group(0) if email else "",
        "phone": phone.group(0) if phone else ""
    }

# ===== Initialize Chroma =====
with st.spinner("🔧 Initializing document assistant..."):
    chroma_client = chromadb.PersistentClient(path="chaturgpt_db")
    collection = chroma_client.get_or_create_collection(name="chaturgpt_docs")
    embedder = get_embedder()
    llm = get_llm()

# ===== Top UI =====
st.title("🗂️ Chatur GPT- Understand Any Document, Instantly.")
#st.markdown("*Understand Any Document, Instantly.*")
st.markdown("---")

# ===== Language Selection =====
language = st.selectbox("🌐 Choose your query language", ["English", "Hindi", "Telugu", "Tamil"])

# ===== Upload & Process =====
uploaded_files = st.file_uploader(
    "📎 Upload documents (PDF, DOCX, TXT, CSV)",
    type=["pdf", "docx", "txt", "csv"],
    accept_multiple_files=True
)

if uploaded_files:
    with st.spinner("📄 Processing files..."):
        for file in uploaded_files:
            file_path = Path(UPLOAD_DIR) / file.name
            with open(file_path, "wb") as f:
                f.write(file.getbuffer())

            text = extract_text(file_path)
            if not text:
                st.warning(f"⚠️ No readable text in {file.name}")
                continue

            identifiers = extract_identifiers(text)
            chunks = chunk_text(text)
            embeddings = [embedder(c) for c in chunks]
            ids = [f"{file.name}_chunk_{i}" for i in range(len(chunks))]
            metas = [{"source": file.name, **identifiers} for _ in chunks]

            collection.add(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metas)
            st.success(f"✅ {file.name} added to database")
            if any(identifiers.values()):
                st.info(f"📌 Identifiers: {identifiers}")

# ===== Query Section =====
query = st.text_input("🔍 Ask something about your documents")

def search_identifiers_first(query):
    if "resume" in query.lower() or "whose" in query.lower():
        all_meta = collection.get(include=["metadatas"])["metadatas"]
        for m in all_meta:
            if m and m.get("name"):
                return f"This résumé belongs to {m['name']}"
    return None

if query:
    special = search_identifiers_first(query)
    if special:
        st.subheader("📌 Answer")
        st.write(f"💡 {special}")
    else:
        results = collection.query(query_texts=[query], n_results=3)
        if not results.get("documents") or not results["documents"][0]:
            st.error("📂 No documents in the database. Please upload files first.")
        else:
            context = "\n\n".join(results["documents"][0])
            prompt = f"Answer the following question using ONLY this document context:\n\n{context}\n\nQuestion: {query}"
            answer = llm(prompt)[0]["generated_text"]

            st.session_state.chat_history.append({"user": query, "bot": answer})
            cache["history"] = st.session_state.chat_history

            st.subheader("📌 Answer")
            st.write(f"💡 {answer}")

# ===== Chat History =====
with st.expander("🕘 Chat History"):
    for turn in st.session_state.chat_history:
        st.markdown(f"**You:** {turn['user']}")
        st.markdown(f"**Assistant:** {turn['bot']}")

# ===== Reset Button =====
if st.button("Clear Knowledge Base"):
    if os.path.exists("chaturgpt_db"):
        for f in os.listdir("chaturgpt_db"):
            os.remove(os.path.join("chaturgpt_db", f))
    st.success("🗑 Knowledge base cleared.")