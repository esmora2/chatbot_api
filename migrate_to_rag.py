#!/usr/bin/env python3
"""
Script para migrar completamente a arquitectura RAG con Firebase
"""
import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

from chatbot.firebase_embeddings import firebase_embeddings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """
    Ejecuta la migración completa a RAG
    """
    print("🚀 Iniciando migración a arquitectura RAG completa...")
    
    # 1. Migrar FAQs con embeddings
    print("\n📊 Paso 1: Generando embeddings para FAQs en Firebase...")
    if firebase_embeddings.migrar_faqs_con_embeddings():
        print("✅ Embeddings generados exitosamente")
    else:
        print("❌ Error generando embeddings")
        return
    
    # 2. Cargar índice vectorial
    print("\n🔍 Paso 2: Cargando índice vectorial FAISS...")
    if firebase_embeddings.cargar_indice_vectorial():
        print("✅ Índice vectorial cargado exitosamente")
    else:
        print("❌ Error cargando índice vectorial")
        return
    
    # 3. Probar búsqueda semántica
    print("\n🧪 Paso 3: Probando búsqueda semántica...")
    preguntas_test = [
        "¿Dónde está el psicólogo?",
        "director de software",
        "departamento de computación"
    ]
    
    for pregunta in preguntas_test:
        print(f"\n   🔍 Probando: '{pregunta}'")
        resultado = firebase_embeddings.buscar_hibrida(pregunta, top_k=2)
        
        if resultado['resultados']:
            mejor = resultado['resultados'][0]
            print(f"      ✅ Encontrado: {mejor['documento']['pregunta'][:50]}...")
            print(f"      📊 Score: {mejor['peso_total']:.3f}")
            print(f"      🔧 Método: {mejor['metodo']}")
        else:
            print(f"      ❌ No encontrado")
    
    print("\n🎉 Migración completada! Tu chatbot ahora usa:")
    print("   ✅ Embeddings semánticos")
    print("   ✅ Base vectorial FAISS")
    print("   ✅ Búsqueda híbrida")
    print("   ✅ LLM para reformulación")
    print("   ✅ Arquitectura RAG completa")

if __name__ == "__main__":
    main()
