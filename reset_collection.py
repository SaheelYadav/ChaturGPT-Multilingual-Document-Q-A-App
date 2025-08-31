import chromadb

# Connect to your persistent DB
chroma_client = chromadb.PersistentClient(path="chaturgpt_db")

# Delete the old collection if it exists
try:
    chroma_client.delete_collection(name="chaturgpt_docs")
    print("✅ Old collection deleted.")
except Exception as e:
    print(f"ℹ️ No existing collection to delete or already removed: {e}")

# Create a fresh collection — will now lock to your current embedder's dimension
collection = chroma_client.create_collection(name="chaturgpt_docs")
print("📦 New collection created with correct embedding dimension.")