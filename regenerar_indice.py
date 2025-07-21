#!/usr/bin/env python3
"""
Regenerar índice vectorial FAISS desde Firebase
"""
import os
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

from chatbot.firebase_embeddings import firebase_embeddings

def regenerar_indice():
    """Regenera el índice vectorial desde Firebase"""
    
    print("🔄 Regenerando índice vectorial FAISS...")
    
    try:
        # Cargar índice directamente desde Firebase
        print("   📥 Cargando índice desde Firebase...")
        success = firebase_embeddings.cargar_indice_vectorial()
        
        if success:
            print("   ✅ Índice generado exitosamente")
            
            # Test rápido
            print("   🔍 Test de búsqueda...")
            resultado = firebase_embeddings.buscar_semantica("psicólogo", top_k=1)
            if resultado:
                print(f"   ✅ Test exitoso: {resultado[0]['pregunta'][:50]}...")
            else:
                print("   ⚠️ Test no devolvió resultados")
                
            print("\n🎉 Regeneración completada!")
        else:
            print("   ❌ Error al generar el índice")
        
    except Exception as e:
        print(f"💥 Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    regenerar_indice()
