#!/usr/bin/env python3
"""
Test final del sistema RAG completo
"""
import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

from chatbot.firebase_embeddings import firebase_embeddings

def test_rag_system():
    """Prueba el sistema RAG completo"""
    
    preguntas_test = [
        "¿Dónde está el psicólogo?",
        "¿Quién es el director de software?", 
        "¿Dónde está el departamento de computación?",
        "¿Cómo contactar al coordinador?",
        "¿Qué materias hay en primer semestre?"
    ]
    
    print("🧪 Probando sistema RAG completo de Firebase...\n")
    
    for i, pregunta in enumerate(preguntas_test, 1):
        print(f"   {i}. Pregunta: '{pregunta}'")
        
        try:
            resultado = firebase_embeddings.buscar_hibrida(pregunta)
            
            if resultado and resultado.get('found'):
                print(f"      ✅ Respuesta: {resultado['answer'][:100]}...")
                print(f"      📊 Confianza: {resultado.get('similarity', 0.0):.3f}")
                print(f"      🔧 Método: {resultado.get('metodo', 'desconocido')}")
            else:
                print("      ❌ No se encontró respuesta")
                
        except Exception as e:
            print(f"      💥 Error: {str(e)}")
            
        print()
    
    print("🎯 Test completado!")

if __name__ == "__main__":
    test_rag_system()
