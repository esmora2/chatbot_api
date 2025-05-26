import pandas as pd
import os
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Ruta base de documentos
BASE_DIR = os.path.join("media", "docs")

def cargar_documentos():
    all_docs = []

    # 1. Cargar CSV
    csv_path = os.path.join(BASE_DIR, "basecsvf.csv")
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        df = df.dropna(subset=["Pregunta", "Respuesta"])

        for _, row in df.iterrows():
            doc = Document(
                page_content=row["Respuesta"],
                metadata={"source": "faq", "pregunta": row["Pregunta"]}
            )
            all_docs.append(doc)

    # 2. Cargar PDFs
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
