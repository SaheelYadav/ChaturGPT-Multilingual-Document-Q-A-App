import streamlit as st
import chromadb
from sentence_transformers import SentenceTransformer
from deep_translator import GoogleTranslator
from langchain.text_splitter import RecursiveCharacterTextSplitter
import pandas as pd
import tempfile
from PyPDF2 import PdfReader
from docx import Document
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

# ------------------ CONFIG ------------------
st.set_page_config(
    page_title="ChaturGPT – Multilingual Document Q&A",
    page_icon="🗂️",
    layout="wide",
)

# ------------------ SESSION STATE ------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "collection" not in st.session_state:
    st.session_state.collection = None

# ------------------ EMBEDDING MODEL & DB ------------------
embedder = SentenceTransformer("all-MiniLM-L6-v2")
chroma_client = chromadb.PersistentClient(path="chaturgpt_db")

# ------------------ LANGUAGE DROPDOWN ------------------
st.title("🗂️ ChaturGPT – Understand Any Document")
st.subheader("📂 Upload PDF, DOCX, TXT, or CSV and ask questions in any language")

language_map = {
    "English": "en",
    "Hindi": "hi",
    "Telugu": "te",
    "Tamil": "ta",
    "Bengali": "bn",
    "Gujarati": "gu",
    "Kannada": "kn",
    "Malayalam": "ml",
}

selected_lang_name = st.selectbox("🌍 Select Response Language", list(language_map.keys()), index=0)
selected_lang = language_map[selected_lang_name]

# ------------------ HELPER FUNCTIONS ------------------
def translate(text, target_lang="en"):
    """Translate text to target language using Google Translator."""
    try:
        if not text or target_lang == "en":
            return text
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception:
        return text


def extract_text(file):
    """Extract text from PDF, DOCX, TXT, or CSV files."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(file.read())
        tmp_path = tmp.name

    if file.name.endswith(".pdf"):
        reader = PdfReader(tmp_path)
        return "\n".join([page.extract_text() or "" for page in reader.pages])
    elif file.name.endswith(".docx"):
        doc = Document(tmp_path)
        return "\n".join([p.text for p in doc.paragraphs])
    elif file.name.endswith(".csv"):
        df = pd.read_csv(tmp_path)
        return df.to_string()
    else:
        with open(tmp_path, "r", encoding="utf-8") as f:
            return f.read()


# ------------------ FILE UPLOAD ------------------
uploaded_files = st.file_uploader(
    "Upload your documents", type=["pdf", "docx", "txt", "csv"], accept_multiple_files=True
)

text_chunks = []
if uploaded_files:
    for file in uploaded_files:
        text = extract_text(file)
        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        chunks = splitter.split_text(text)
        text_chunks.extend(chunks)

    if text_chunks:
        # Reset collection to avoid conflict
        try:
            chroma_client.delete_collection("chaturgpt_docs")
        except:
            pass

        st.session_state.collection = chroma_client.create_collection("chaturgpt_docs")
        embeddings = embedder.encode(text_chunks).tolist()

        for i, chunk in enumerate(text_chunks):
            st.session_state.collection.add(
                ids=[str(i)], documents=[chunk], embeddings=[embeddings[i]]
            )

        st.success(f"✅ Processed {len(uploaded_files)} file(s) ({len(text_chunks)} chunks)")

        # Basic summary & keywords
        summary = "\n".join(text_chunks[:3])[:1000]
        keywords = ", ".join(
            list(set([w for chunk in text_chunks for w in chunk.split()[:3]]))[:10]
        )

        st.markdown("### 📄 Document Summary")
        st.info(translate(summary, selected_lang))

        st.markdown("### 🔑 Keywords")
        st.success(translate(keywords, selected_lang))

# ------------------ Q&A SECTION ------------------
st.markdown("### 💬 Ask a Question About Your Documents")
user_input = st.text_input("Type your question here...")

if user_input:
    translated_q = translate(user_input, "en")

    if st.session_state.collection:
        results = st.session_state.collection.query(
            query_embeddings=[embedder.encode(translated_q).tolist()], n_results=2
        )
        retrieved_docs = results["documents"][0] if results else []
        answer = "\n".join(retrieved_docs) if retrieved_docs else "No relevant answer found."
    else:
        answer = "No documents uploaded yet."

    st.session_state.chat_history.append(
        {"q": user_input, "a": translate(answer, selected_lang)}
    )

# ------------------ CHAT HISTORY ------------------
with st.expander("📜 View Chat History", expanded=False):
    if st.session_state.chat_history:
        for chat in st.session_state.chat_history:
            st.markdown(f"**Q:** {chat['q']}")
            st.markdown(f"**A:** {chat['a']}")
    else:
        st.write("No chat history yet.")

# ------------------ FEEDBACK ------------------
st.markdown("### 📝 Feedback")
feedback = st.text_area("Let us know how we did!")
if st.button("Submit Feedback"):
    st.success("✅ Feedback submitted. Thank you!")
