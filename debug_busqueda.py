#!/usr/bin/env python3
import os
import sys
import django

# Agregar el directorio del proyecto al path
sys.path.append('/home/erickxse/visual/asegcbot/chatbot_api')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

from chatbot.vector_store import buscar_documentos, inicializar_vector_store
from chatbot.views import es_pregunta_fuera_contexto, validar_relevancia_respuesta

def test_busqueda():
    pregunta = "quien es el director de carrera de software en la ESPE"
    
    print(f"=== TESTING BÚSQUEDA ===")
    print(f"Pregunta: {pregunta}")
    print()
    
    # 1. Verificar filtro de contexto
    fuera_contexto = es_pregunta_fuera_contexto(pregunta)
    print(f"¿Está fuera de contexto?: {fuera_contexto}")
    print()
    
    # 2. Buscar documentos
    print("Inicializando vector store...")
    try:
        inicializar_vector_store()
        print("Vector store inicializado correctamente")
    except Exception as e:
        print(f"Error al inicializar: {e}")
        return
    
    print("Buscando documentos...")
    documentos = buscar_documentos(pregunta, top_k=5)
    print(f"Documentos encontrados: {len(documentos)}")
    print()
    
    # 3. Mostrar documentos encontrados
    for i, doc in enumerate(documentos):
        print(f"--- Documento {i+1} ---")
        print(f"Fuente: {doc.metadata.get('source', 'desconocida')}")
        print(f"Título: {doc.metadata.get('titulo', 'N/A')}")
        if doc.metadata.get('source') == 'faq':
            print(f"Pregunta original: {doc.metadata.get('pregunta_original', 'N/A')}")
            print(f"Respuesta original: {doc.metadata.get('respuesta_original', 'N/A')}")
        print(f"Contenido (primeros 200 chars): {doc.page_content[:200]}...")
        print()
    
    # 4. Verificar validación de relevancia
    relevante = validar_relevancia_respuesta(pregunta, "", documentos)
    print(f"¿Es relevante?: {relevante}")
    
    # 5. Calcular similitudes individuales
    print("\n=== SIMILITUDES ===")
    from difflib import SequenceMatcher
    
    def similitud_texto(a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    for i, doc in enumerate(documentos):
        if doc.metadata.get("source") == "faq":
            pregunta_original = doc.metadata.get("pregunta_original", "")
            sim_pregunta = similitud_texto(pregunta, pregunta_original)
            print(f"Documento {i+1} (FAQ) - Similitud con pregunta original: {sim_pregunta:.3f}")
        else:
            sim_contenido = similitud_texto(pregunta, doc.page_content[:200])
            print(f"Documento {i+1} ({doc.metadata.get('source', 'N/A')}) - Similitud con contenido: {sim_contenido:.3f}")

if __name__ == "__main__":
    test_busqueda()
