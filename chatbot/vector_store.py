from huggingface_hub import login
login("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")

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from .document_loader import cargar_documentos

all_documents = cargar_documentos()
embedding_model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")

texts = [doc.page_content for doc in all_documents]
embeddings = embedding_model.encode(texts, convert_to_numpy=True)
embedding_matrix = np.array(embeddings).astype("float32")

index = faiss.IndexFlatL2(embedding_matrix.shape[1])
index.add(embedding_matrix)


# Búsqueda semántica
def buscar_documentos(query, top_k=3):
    query_embedding = embedding_model.encode([query]).astype("float32")
    distances, indices = index.search(query_embedding, 1) #top_k=1
    resultados = [all_documents[i] for i in indices[0]]

def buscar_documentos(query, top_k=3, min_similarity=0.6):
    query_embedding = embedding_model.encode([query], convert_to_numpy=True).astype("float32")
    distances, indices = index.search(query_embedding, top_k)

    resultados = []
    for i, dist in zip(indices[0], distances[0]):
        similarity = 1 / (1 + dist)
        if similarity >= min_similarity:
            resultados.append(all_documents[i])

    return resultados
