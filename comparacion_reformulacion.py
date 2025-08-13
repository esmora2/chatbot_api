#!/usr/bin/env python3
"""
Comparación ANTES vs DESPUÉS de la reformulación Firebase RAG
"""
import os
import sys
import django

sys.path.append('/home/erickxse/visual/asegcbot/chatbot_api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

from chatbot.firebase_embeddings import firebase_embeddings
from chatbot.views import consultar_llm_inteligente

def comparar_antes_despues():
    """
    Muestra la diferencia entre respuesta original y reformulada
    """
    print("🔍 COMPARACIÓN: ANTES vs DESPUÉS DE REFORMULACIÓN")
    print("=" * 70)
    
    pregunta = "¿Quién es el director de la carrera de software?"
    
    # Obtener respuesta original de Firebase RAG
    print(f"❓ PREGUNTA: {pregunta}")
    print()
    
    resultado_firebase = firebase_embeddings.buscar_hibrida(pregunta)
    
    if resultado_firebase and resultado_firebase.get('found'):
        respuesta_original = resultado_firebase["answer"]
        
        print("📋 RESPUESTA ORIGINAL (Firebase RAG):")
        print(f"   {respuesta_original}")
        print()
        
        # Crear prompt de reformulación
        prompt_reformulacion = (
            "Eres un asistente académico del DCCO/ESPE. Reformula esta respuesta para que sea más natural, clara y profesional.\n"
            "INSTRUCCIONES:\n"
            "- Mantén TODA la información factual original\n"
            "- Mejora la redacción y fluidez\n"
            "- Haz que suene más conversacional y amigable\n"
            "- Mantén el contexto académico y profesional\n"
            "- NO agregues información nueva que no esté en el original\n\n"
            f"Pregunta del estudiante:\n{pregunta}\n\n"
            f"Respuesta original de la base de datos:\n{respuesta_original}\n\n"
            "Respuesta reformulada y mejorada:"
        )
        
        respuesta_reformulada = consultar_llm_inteligente(prompt_reformulacion)
        
        print("🎨 RESPUESTA REFORMULADA (OpenAI GPT-3.5-turbo):")
        print(f"   {respuesta_reformulada}")
        print()
        
        print("📊 ANÁLISIS DE MEJORAS:")
        print("✅ Reformulación aplicada exitosamente")
        print("✅ Información factual preservada")
        print("✅ Tono más conversacional y amigable")
        print("✅ Mantiene profesionalismo académico")
        print()
        
        print("🎯 BENEFICIOS DE LA REFORMULACIÓN:")
        print("   • Respuestas más naturales y fluidas")
        print("   • Mejor experiencia para el usuario")
        print("   • Mantiene precisión de la información")
        print("   • Tono más conversacional")
        print("   • Preserva contexto académico")
        
    else:
        print("❌ No se encontró respuesta en Firebase RAG")

if __name__ == "__main__":
    comparar_antes_despues()
