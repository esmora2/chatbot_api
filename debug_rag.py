#!/usr/bin/env python3
"""
Debug del sistema RAG
"""
import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

from chatbot.firebase_embeddings import firebase_embeddings

def debug_rag():
    """Debug detallado del sistema RAG"""
    
    print("🔍 Debug del sistema RAG...\n")
    
    # 1. Verificar carga del índice
    print("1️⃣ Verificando índice vectorial...")
    success = firebase_embeddings.cargar_indice_vectorial()
    print(f"   Índice cargado: {success}")
    
    if hasattr(firebase_embeddings, 'index') and firebase_embeddings.index:
        print(f"   Documentos en índice: {len(firebase_embeddings.documents) if firebase_embeddings.documents else 0}")
        print(f"   Dimensión del índice: {firebase_embeddings.index.d}")
        print(f"   Total vectores: {firebase_embeddings.index.ntotal}")
    
    # 2. Verificar documentos
    print("\n2️⃣ Verificando documentos...")
    if firebase_embeddings.documents:
        print(f"   Primeros 3 documentos:")
        for i, doc in enumerate(firebase_embeddings.documents[:3]):
            print(f"   [{i+1}] {doc['pregunta'][:60]}...")
    
    # 3. Test de embedding
    print("\n3️⃣ Test de embedding...")
    test_text = "psicólogo"
    embedding = firebase_embeddings.generar_embedding(test_text)
    print(f"   Texto: '{test_text}'")
    print(f"   Embedding generado: {len(embedding)} dimensiones")
    print(f"   Primeros 5 valores: {embedding[:5]}")
    
    # 4. Test de búsqueda semántica con debug
    print("\n4️⃣ Test de búsqueda semántica...")
    try:
        resultado = firebase_embeddings.buscar_semantica("psicólogo", top_k=3, umbral=0.1)  # Umbral muy bajo
        print(f"   Resultados encontrados: {len(resultado) if resultado else 0}")
        
        if resultado:
            for i, res in enumerate(resultado):
                print(f"   [{i+1}] Score: {res.get('score', 0):.3f} - {res['pregunta'][:60]}...")
    except Exception as e:
        print(f"   Error en búsqueda semántica: {e}")
    
    # 5. Test de búsqueda textual
    print("\n5️⃣ Test de búsqueda textual...")
    try:
        resultado = firebase_embeddings._buscar_textual_simple("psicólogo", top_k=3)
        print(f"   Resultados encontrados: {len(resultado) if resultado else 0}")
        
        if resultado:
            for i, res in enumerate(resultado):
                print(f"   [{i+1}] Score: {res.get('score', 0):.3f} - {res['pregunta'][:60]}...")
    except Exception as e:
        print(f"   Error en búsqueda textual: {e}")
    
    # 6. Test completo híbrido
    print("\n6️⃣ Test de búsqueda híbrida...")
    try:
        resultado = firebase_embeddings.buscar_hibrida("psicólogo")
        print(f"   Resultado: {resultado}")
    except Exception as e:
        print(f"   Error en búsqueda híbrida: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_rag()
