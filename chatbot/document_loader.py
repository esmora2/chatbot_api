import pandas as pd
import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Ruta base de documentos
BASE_DIR = os.path.join("media", "docs")

def cargar_documentos():
    all_docs = []

    # 1. Cargar CSV con PREGUNTA + RESPUESTA combinadas
    csv_path = os.path.join(BASE_DIR, "basecsvf.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df = df.dropna(subset=["Pregunta", "Respuesta"])

        for _, row in df.iterrows():
            # SOLUCIÓN: Combinar pregunta y respuesta para mejorar la búsqueda
            contenido_combinado = f"Pregunta: {row['Pregunta']}\nRespuesta: {row['Respuesta']}"
            
            doc = Document(
                page_content=contenido_combinado,  # Ahora incluye la pregunta
                metadata={
                    "source": "faq", 
                    "pregunta_original": row["Pregunta"],
                    "respuesta_original": row["Respuesta"]
                }
            )
            all_docs.append(doc)

    # 2. Cargar PDFs (sin cambios)
    for filename in os.listdir(BASE_DIR):
        if filename.endswith(".pdf"):
            loader = PyMuPDFLoader(os.path.join(BASE_DIR, filename))
            raw_docs = loader.load()

            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            split_docs = splitter.split_documents(raw_docs)

            for doc in split_docs:
                doc.metadata["source"] = filename
                all_docs.append(doc)

    return all_docs

# ALTERNATIVA: Función para crear documentos duales
def cargar_documentos_duales():
    """
    Alternativa que crea DOS documentos por cada FAQ:
    1. Uno con la pregunta (para encontrar preguntas similares)
    2. Uno con pregunta+respuesta (para contexto completo)
    """
    all_docs = []

    csv_path = os.path.join(BASE_DIR, "basecsvf.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df = df.dropna(subset=["Pregunta", "Respuesta"])

        for _, row in df.iterrows():
            # Documento 1: Solo la pregunta (para matching)
            doc_pregunta = Document(
                page_content=row["Pregunta"],
                metadata={
                    "source": "faq_pregunta", 
                    "pregunta_original": row["Pregunta"],
                    "respuesta_original": row["Respuesta"],
                    "tipo": "pregunta"
                }
            )
            all_docs.append(doc_pregunta)
            
            # Documento 2: Pregunta + Respuesta (para contexto)
            contenido_completo = f"P: {row['Pregunta']}\nR: {row['Respuesta']}"
            doc_completo = Document(
                page_content=contenido_completo,
                metadata={
                    "source": "faq_completa", 
                    "pregunta_original": row["Pregunta"],
                    "respuesta_original": row["Respuesta"],
                    "tipo": "completa"
                }
            )
            all_docs.append(doc_completo)

    # Cargar PDFs
    for filename in os.listdir(BASE_DIR):
        if filename.endswith(".pdf"):
            loader = PyMuPDFLoader(os.path.join(BASE_DIR, filename))
            raw_docs = loader.load()

            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            split_docs = splitter.split_documents(raw_docs)

            for doc in split_docs:
                doc.metadata["source"] = filename
                doc.metadata["tipo"] = "pdf"
                all_docs.append(doc)

    return all_docs