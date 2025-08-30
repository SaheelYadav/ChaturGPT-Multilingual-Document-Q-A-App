import streamlit as st
import os
import pandas as pd
import pdfplumber
import docx
import re
import chromadb
from chromadb.utils import embedding_functions
from transformers import pipeline, MarianMTModel, MarianTokenizer
import diskcache as dc
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import logging

# Suppress noisy Streamlit thread warnings
logging.getLogger("streamlit.runtime").setLevel(logging.ERROR)

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

@st.cache_resource
def get_summarizer():
    return pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")

@st.cache_resource
def get_translator(lang_code):
    model_name = f"Helsinki-NLP/opus-mt-{lang_code}-en"
    tokenizer = MarianTokenizer.from_pretrained(model_name)
    model = MarianMTModel.from_pretrained(model_name)
    return tokenizer, model

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

def summarize_text(text, lang_code):
    summarizer = get_summarizer()
    if lang_code != "en":
        tokenizer, model = get_translator(lang_code)
        tokens = tokenizer(text[:1024], return_tensors="pt", padding=True)
        translated = model.generate(**tokens)
        text = tokenizer.decode(translated[0], skip_special_tokens=True)
    return summarizer(text[:1024])[0]["summary_text"]

def translate_query(query, lang_code):
    if lang_code == "en":
        return query
    tokenizer, model = get_translator(lang_code)
    tokens = tokenizer(query, return_tensors="pt", padding=True)
    translated = model.generate(**tokens)
    return tokenizer.decode(translated[0], skip_special_tokens=True)

# ===== Initialize Chroma =====
with st.spinner("🔧 Initializing document assistant..."):
    chroma_client = chromadb.PersistentClient(path="chaturgpt_db")
    collection = chroma_client.get_or_create_collection(name="chaturgpt_docs")
    embedder = get_embedder()
    llm = get_llm()

# ===== Top UI =====
st.title("🗂️ Chatur GPT – Understand Any Document, Instantly.")
st.markdown("---")

# ===== Language Selection =====
language = st.selectbox("🌐 Choose your query language", ["English", "Hindi", "Telugu", "Tamil"])
lang_map = {"Hindi": "hi", "Telugu": "te", "Tamil": "ta", "English": "en"}
lang_code = lang_map[language]

# ===== Upload & Process =====
uploaded_files = st.file_uploader(
    "📎 Upload documents (PDF, DOCX, TXT, CSV)",
    type=["pdf", "docx", "txt", "csv"],
    accept_multiple_files=True
)

file_type_icons = {
    ".pdf": "📕", ".docx": "📄", ".csv": "📊", ".txt": "📜"
}

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

            with ThreadPoolExecutor() as executor:
                embeddings = list(executor.map(embedder, chunks))

            ids = [f"{file.name}_chunk_{i}" for i in range(len(chunks))]
            metas = [{"source": file.name, **identifiers} for _ in chunks]

            collection.add(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metas)
            icon = file_type_icons.get(file_path.suffix.lower(), "📁")
            st.success(f"{icon} {file.name} added to database")
            if any(identifiers.values()):
                st.info(f"📌 Identifiers: {identifiers}")

            summary = summarize_text(text, lang_code)
            st.info(f"📝 Summary of {file.name}:\n\n{summary}")

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
    translated_query = translate_query(query, lang_code)
    special = search_identifiers_first(translated_query)

    if special:
        st.subheader("📌 Answer")
        st.write(f"💡 {special}")
    else:
        results = collection.query(query_texts=[translated_query], n_results=10)
        filtered = [doc for doc in results["documents"][0] if translated_query.lower() in doc.lower()]
        context = "\n\n".join(filtered[:3]) if filtered else "\n\n".join(results["documents"][0][:3])

        prompt = f"Answer the following question using ONLY this document context:\n\n{context}\n\nQuestion: {translated_query}"
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

# ===== Feedback Form =====
with st.form("feedback_form"):
    st.subheader("💬 Share your feedback")
    name = st.text_input("Your name (optional)")
    comments = st.text_area("What did you like or want improved?")
    submitted = st.form_submit_button("Submit")
    if submitted:
        st.success("🙏 Thanks for your feedback!")

# ===== Reset Button =====
if st.button("Clear Knowledge Base"):
    if os.path.exists("chaturgpt_db"):
        for f in os.listdir("chaturgpt_db"):
            os.remove(os.path.join("chaturgpt_db", f))
    st.success("🗑 Knowledge base cleared.")