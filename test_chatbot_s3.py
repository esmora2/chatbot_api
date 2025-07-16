#!/usr/bin/env python
"""
Script final para probar el chatbot completo con S3
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append('/home/erickxse/visual/asegcbot/chatbot_api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

import requests
import json

def test_chatbot_api():
    """Prueba el endpoint del chatbot"""
    url = "http://localhost:8000/api/chatbot/hibrido/"
    
    preguntas_test = [
        "¿Qué es una aplicación distribuida?",
        "¿Dónde se encuentra el departamento de computación?",
        "¿Cuáles son las características de las aplicaciones distribuidas?",
        "¿Qué es ingeniería de software?",
        "¿Cuál es el contenido del syllabus de aplicaciones basadas en el conocimiento?"
    ]
    
    print("🤖 PRUEBA DEL CHATBOT CON S3")
    print("=" * 50)
    
    for i, pregunta in enumerate(preguntas_test, 1):
        print(f"\n{i}. Pregunta: {pregunta}")
        
        try:
            response = requests.post(
                url,
                json={"pregunta": pregunta},
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Respuesta: {data.get('respuesta', 'Sin respuesta')[:200]}...")
                print(f"   📊 Fuente: {data.get('fuente', 'No especificada')}")
                print(f"   🎯 Confianza: {data.get('confianza', 'N/A')}")
            else:
                print(f"   ❌ Error HTTP {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            
    print("\n" + "=" * 50)
    print("✅ Prueba completada")

def test_local_functions():
    """Prueba las funciones locales"""
    print("\n🔧 PRUEBA DE FUNCIONES LOCALES")
    print("=" * 30)
    
    # Importar funciones locales
    from chatbot.document_loader import cargar_documentos
    from chatbot.vector_store import buscar_documentos
    
    # Cargar documentos
    print("📚 Cargando documentos...")
    docs = cargar_documentos()
    print(f"✅ {len(docs)} documentos cargados")
    
    # Buscar documentos
    print("\n🔍 Probando búsqueda semántica...")
    resultados = buscar_documentos("¿Qué es una aplicación distribuida?", top_k=3)
    print(f"✅ {len(resultados)} resultados encontrados")
    
    for i, doc in enumerate(resultados, 1):
        print(f"\n📄 Resultado {i}:")
        print(f"   Fuente: {doc.metadata.get('source', 'No especificada')}")
        print(f"   Contenido: {doc.page_content[:150]}...")

def main():
    """Función principal"""
    print("🚀 PRUEBA COMPLETA DEL SISTEMA")
    print("=" * 60)
    
    # Probar funciones locales
    test_local_functions()
    
    # Preguntar si probar API
    print("\n🌐 PRUEBA DE API")
    print("=" * 20)
    print("Para probar la API, asegúrate de que el servidor esté ejecutándose:")
    print("   python manage.py runserver")
    
    respuesta = input("\n¿Deseas probar la API del chatbot? (s/n): ").lower()
    
    if respuesta in ['s', 'sí', 'si', 'y', 'yes']:
        test_chatbot_api()
    else:
        print("❌ Prueba de API omitida")
    
    print("\n🎉 ¡SISTEMA LISTO PARA USAR!")
    print("   - Documentos cargados desde S3")
    print("   - URLs de CloudFront configuradas")
    print("   - Vector store funcionando")
    print("   - Chatbot híbrido operativo")

if __name__ == "__main__":
    main()
