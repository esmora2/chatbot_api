from huggingface_hub import login
login("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")  # Usa el mismo token que en views.py

from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from .document_loader import cargar_documentos

# Inicializar modelo de embeddings
embedding_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

# Cargar documentos
all_documents = cargar_documentos()

# Generar embeddings
texts = [doc.page_content for doc in all_documents]
embeddings = embedding_model.encode(texts)

# Crear FAISS index
embedding_matrix = np.array(embeddings).astype("float32")
index = faiss.IndexFlatL2(embedding_matrix.shape[1])
index.add(embedding_matrix)

# Búsqueda semántica
def buscar_documentos(query, top_k=3):
    query_embedding = embedding_model.encode([query]).astype("float32")
    distances, indices = index.search(query_embedding, top_k)
    resultados = [all_documents[i] for i in indices[0]]
    return resultados
