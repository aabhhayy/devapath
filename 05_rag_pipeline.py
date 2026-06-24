"""
RAG Pipeline — Temple Data ko AI ke liye ready karo
"""

import json
import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# ---- Data load karo ----
with open("data/processed/temples_master.json", "r", encoding="utf-8") as f:
    temples = json.load(f)

print(f"✅ {len(temples)} temples loaded")

# ---- Har temple ka text banao ----
documents = []
metadatas = []

for temple in temples:
    text = f"""
    Temple: {temple['name']}
    City: {temple['city']}, {temple['state']}
    Deity: {temple['deity']}
    Opening Time: {temple['opening_time']}
    Closing Time: {temple['closing_time']}
    Best Visit Time: {temple['best_visit_time']}
    Entry Fee: {temple['entry_fee']}
    Dress Code: {temple['dress_code']}
    History: {temple['history']}
    """

    documents.append(text.strip())
    metadatas.append({
        "name":  temple['name'],
        "city":  temple['city'],
        "state": temple['state'],
        "lat":   str(temple.get('lat', '')),
        "lon":   str(temple.get('lon', ''))
    })

# ---- Text chunks me todo ----
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.create_documents(documents, metadatas=metadatas)
print(f"✅ {len(chunks)} chunks created")

# ---- Embeddings banao aur ChromaDB me save karo ----
print("⏳ Embeddings ban rahi hain (1-2 min)...")

embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2"
)

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="data/chroma_db"
)

print("✅ ChromaDB ready!")
print("📁 Saved: data/chroma_db")