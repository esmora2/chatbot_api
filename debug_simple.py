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
    from chatbot.document_loader import cargar_documentos
    print("Importando cargar_documentos...")
    documentos = cargar_documentos()
    print(f"Total documentos cargados: {len(documentos)}")
    
    # Buscar documentos específicos sobre director de software
    for i, doc in enumerate(documentos):
        if "director" in doc.page_content.lower() and "software" in doc.page_content.lower():
            print(f"\n--- Documento {i} ---")
            print(f"Fuente: {doc.metadata.get('source', 'N/A')}")
            print(f"Pregunta original: {doc.metadata.get('pregunta_original', 'N/A')}")
            print(f"Respuesta original: {doc.metadata.get('respuesta_original', 'N/A')}")
            print(f"Contenido: {doc.page_content}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
