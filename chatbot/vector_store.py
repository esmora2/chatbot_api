from huggingface_hub import login
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from django.conf import settings
from .document_loader import cargar_documentos

# Global variables that will be initialized lazily
all_documents = None
embedding_model = None
index = None
embedding_matrix = None

def inicializar_vector_store():
    """
    Inicializa el vector store de manera lazy.
    Solo se ejecuta cuando se necesita buscar documentos.
    """
    global all_documents, embedding_model, index, embedding_matrix
    
    if all_documents is None:
        try:
            # Use token from environment variable if available
            if settings.HUGGINGFACE_TOKEN:
                login(settings.HUGGINGFACE_TOKEN)
            all_documents = cargar_documentos()
            embedding_model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")
            
            texts = [doc.page_content for doc in all_documents]
            embeddings = embedding_model.encode(texts, convert_to_numpy=True)
            embedding_matrix = np.array(embeddings).astype("float32")
            
            index = faiss.IndexFlatL2(embedding_matrix.shape[1])
            index.add(embedding_matrix)
            
            print(f"Vector store inicializado con {len(all_documents)} documentos")
        except Exception as e:
            print(f"Error al inicializar vector store: {e}")
            # Crear estructuras vacías para evitar errores
            all_documents = []
            embedding_model = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")
            embedding_matrix = np.array([[0.0] * 384]).astype("float32")  # Dimensión por defecto del modelo
            index = faiss.IndexFlatL2(384)


# Búsqueda semántica
def buscar_documentos(query, top_k=3):
    # Inicializar el vector store si no está inicializado
    inicializar_vector_store()
    
    if not all_documents:
        return []
    
    query_embedding = embedding_model.encode([query]).astype("float32")
    _, indices = index.search(query_embedding, top_k)
    resultados = [all_documents[i] for i in indices[0]]
    return resultados
