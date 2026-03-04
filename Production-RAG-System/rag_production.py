import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import pipeline
from sklearn.metrics.pairwise import cosine_similarity

# Load models
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
generator = pipeline("text-generation", model="gpt2")

# Sample knowledge base with metadata
documents = [
    {"text": "Machine learning is a subset of Artificial Intelligence.", "category": "ML"},
    {"text": "Supervised learning requires labeled data.", "category": "ML"},
    {"text": "Deep learning uses neural networks.", "category": "ML"},
    {"text": "Artificial Intelligence is transforming industries.", "category": "AI"},
    {"text": "Legal documents must follow regulatory standards.", "category": "Legal"}
]

# Metadata filter
selected_category = "ML"
filtered_docs = [doc["text"] for doc in documents if doc["category"] == selected_category]

# Embeddings
doc_embeddings = embedding_model.encode(filtered_docs).astype("float32")

# FAISS index
dimension = doc_embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(doc_embeddings)

print("🚀 Production RAG System Ready!")

while True:
    query = input("Ask a question (type 'quit' to exit): ")

    if query.lower() == "quit":
        break

    query_vector = embedding_model.encode([query]).astype("float32")

    # Top-K retrieval
    k = 5
    distances, indices = index.search(query_vector, k)

    retrieved_docs = [filtered_docs[i] for i in indices[0]]

    # Re-ranking
    retrieved_embeddings = embedding_model.encode(retrieved_docs)
    similarities = cosine_similarity(query_vector, retrieved_embeddings)[0]

    ranked_docs = [doc for _, doc in sorted(zip(similarities, retrieved_docs), reverse=True)]

    # Select best 2
    final_context = "\n".join(ranked_docs[:2])

    prompt = f"""
Context:
{final_context}

Question:
{query}

Answer:
"""

    output = generator(prompt, max_length=150)
    print("\nAnswer:\n", output[0]["generated_text"])
    print("-" * 50)