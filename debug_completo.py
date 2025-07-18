#!/usr/bin/env python3
import os
import sys

# Agregar el directorio del proyecto al path
sys.path.append('/home/erickxse/visual/asegcbot/chatbot_api')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')

try:
    import django
    django.setup()
    print("Django configurado correctamente")
except Exception as e:
    print(f"Error configurando Django: {e}")
    sys.exit(1)

try:
    from chatbot.vector_store import buscar_documentos, inicializar_vector_store
    from chatbot.views import es_pregunta_fuera_contexto, validar_relevancia_respuesta
    from difflib import SequenceMatcher

    def similitud_texto(a, b):
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()

    pregunta = "quien es el director de carrera de software en la ESPE"
    
    print(f"=== ANÁLISIS DE BÚSQUEDA ===")
    print(f"Pregunta: {pregunta}")
    print()
    
    # 1. Verificar filtro de contexto
    fuera_contexto = es_pregunta_fuera_contexto(pregunta)
    print(f"¿Está fuera de contexto?: {fuera_contexto}")
    
    if fuera_contexto:
        print("ERROR: La pregunta está siendo marcada como fuera de contexto!")
        sys.exit(1)
    
    # 2. Buscar documentos
    print("Inicializando vector store...")
    try:
        inicializar_vector_store()
        print("Vector store inicializado correctamente")
    except Exception as e:
        print(f"Error al inicializar: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("Buscando documentos...")
    documentos = buscar_documentos(pregunta, top_k=5)
    print(f"Documentos encontrados: {len(documentos)}")
    print()
    
    if len(documentos) == 0:
        print("ERROR: No se encontraron documentos!")
        sys.exit(1)
    
    # 3. Mostrar documentos encontrados
    for i, doc in enumerate(documentos):
        print(f"--- Documento {i+1} ---")
        print(f"Fuente: {doc.metadata.get('source', 'desconocida')}")
        print(f"Título: {doc.metadata.get('titulo', 'N/A')}")
        if doc.metadata.get('source') == 'faq':
            pregunta_original = doc.metadata.get('pregunta_original', 'N/A')
            respuesta_original = doc.metadata.get('respuesta_original', 'N/A')
            print(f"Pregunta original: {pregunta_original}")
            print(f"Respuesta original: {respuesta_original}")
            
            # Calcular similitud específica
            sim_pregunta = similitud_texto(pregunta, pregunta_original)
            print(f"Similitud con pregunta original: {sim_pregunta:.3f}")
            
            # ¿Es match exacto?
            if sim_pregunta >= 0.75:
                print("*** MATCH EXACTO ENCONTRADO! ***")
        else:
            sim_contenido = similitud_texto(pregunta, doc.page_content[:200])
            print(f"Similitud con contenido: {sim_contenido:.3f}")
            
        print(f"Contenido (primeros 200 chars): {doc.page_content[:200]}...")
        print()
    
    # 4. Verificar validación de relevancia
    relevante = validar_relevancia_respuesta(pregunta, "", documentos)
    print(f"¿Es relevante según validar_relevancia_respuesta?: {relevante}")
    
    if not relevante:
        print("ERROR: La validación de relevancia está fallando!")
        
        # Analizar por qué falla
        print("\n=== ANÁLISIS DE RELEVANCIA ===")
        tiene_pdf = any(doc.metadata.get("source") == "pdf" for doc in documentos)
        print(f"¿Tiene documentos PDF?: {tiene_pdf}")
        
        relevancia_promedio = 0
        documentos_validos = 0
        
        for doc in documentos:
            if doc.metadata.get("source") in ["faq", "web", "pdf"]:
                score = similitud_texto(pregunta, doc.page_content[:200])
                relevancia_promedio += score
                documentos_validos += 1
                print(f"Doc {doc.metadata.get('source')}: score {score:.3f}")
        
        if documentos_validos > 0:
            relevancia_promedio /= documentos_validos
            print(f"Relevancia promedio: {relevancia_promedio:.3f}")
        
        umbral = 0.01 if tiene_pdf else 0.05
        print(f"Umbral requerido: {umbral}")
        print(f"¿Supera umbral?: {relevancia_promedio >= umbral}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
