import pandas as pd
import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Ruta base de documentos
BASE_DIR = os.path.join("media", "docs")

def cargar_documentos():
    all_docs = []

    # 1. Cargar CSV de FAQ (PREGUNTA + RESPUESTA combinadas)
    faq_csv = os.path.join(BASE_DIR, "basecsvf.csv")
    if os.path.exists(faq_csv):
        df = pd.read_csv(faq_csv)
        df = df.dropna(subset=["Pregunta", "Respuesta"])

        for _, row in df.iterrows():
            contenido = f"Pregunta: {row['Pregunta']}\nRespuesta: {row['Respuesta']}"
            doc = Document(
                page_content=contenido,
                metadata={
                    "source": "faq",
                    "tipo": "faq",
                    "pregunta_original": row["Pregunta"],
                    "respuesta_original": row["Respuesta"]
                }
            )
            all_docs.append(doc)

    # 2. Cargar contenido web del DCCO (scrapeado)
    web_csv = os.path.join(BASE_DIR, "contenido_web_dcco.csv")
    if os.path.exists(web_csv):
        df = pd.read_csv(web_csv)
        df = df.dropna(subset=["Titulo", "Contenido"])

        for _, row in df.iterrows():
            doc = Document(
                page_content=row["Contenido"],
                metadata={
                    "source": "web",
                    "tipo": "web",
                    "titulo": row["Titulo"],
                    "url": row.get("URL", "")
                }
            )
            all_docs.append(doc)
            print(f"[WEB] {row['Titulo']} cargado desde {row.get('URL', '')}")

    # 3. Cargar PDFs como siempre
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
