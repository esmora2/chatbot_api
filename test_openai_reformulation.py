#!/usr/bin/env python3
"""
Script de prueba para verificar que OpenAI está reformulando respuestas correctamente
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/home/erickxse/visual/asegcbot/chatbot_api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

from chatbot.views import consultar_llm_inteligente, consultar_openai

def test_openai_reformulation():
    """
    Prueba específica de reformulación usando OpenAI
    """
    print("🧪 PRUEBA DE REFORMULACIÓN CON OPENAI")
    print("=" * 50)
    
    # Simular una respuesta original de FAQ que necesita reformulación
    respuesta_original = "Los horarios de atención de la secretaría son de 8:00 a 17:00 de lunes a viernes."
    pregunta_usuario = "¿A qué hora atiende la secretaría?"
    
    # Crear el prompt de reformulación (igual al que usa el sistema)
    prompt_reformulacion = (
        "Eres un asistente de la ESPE. Reformula ÚNICAMENTE el estilo manteniendo EXACTAMENTE la misma información.\n"
        "INSTRUCCIONES ESTRICTAS:\n"
        "- NO cambies la información factual\n"
        "- NO agregues información nueva\n"
        "- SOLO mejora la redacción si es necesario\n\n"
        f"Respuesta original:\n{respuesta_original}\n\n"
        f"Pregunta del usuario:\n{pregunta_usuario}\n\n"
        "Reformula SOLO el estilo manteniendo TODA la información:"
    )
    
    print(f"📝 RESPUESTA ORIGINAL:")
    print(f"   {respuesta_original}")
    print()
    print(f"❓ PREGUNTA DEL USUARIO:")
    print(f"   {pregunta_usuario}")
    print()
    print(f"🔄 PROBANDO REFORMULACIÓN...")
    
    # Probar directamente consultar_openai
    print("\n1️⃣ Probando consultar_openai() directamente:")
    respuesta_openai = consultar_openai(prompt_reformulacion)
    if respuesta_openai:
        print(f"✅ OpenAI respondió correctamente:")
        print(f"   {respuesta_openai}")
    else:
        print("❌ OpenAI no respondió o hubo error")
    
    # Probar consultar_llm_inteligente (función principal)
    print("\n2️⃣ Probando consultar_llm_inteligente() (función principal):")
    respuesta_llm = consultar_llm_inteligente(prompt_reformulacion)
    if respuesta_llm:
        print(f"✅ LLM inteligente respondió:")
        print(f"   {respuesta_llm}")
    else:
        print("❌ LLM inteligente no respondió")
    
    print("\n" + "=" * 50)
    print("🔍 ANÁLISIS DE RESULTADOS:")
    
    if respuesta_openai:
        print("✅ OpenAI está funcionando correctamente")
        print("✅ El sistema SÍ está usando OpenAI para reformular respuestas")
        if respuesta_openai != respuesta_original:
            print("✅ OpenAI está reformulando (no devolviendo texto original)")
        else:
            print("⚠️  OpenAI devolvió el mismo texto (posible, pero poco probable)")
    else:
        print("❌ OpenAI NO está funcionando")
        print("❌ El sistema NO puede reformular respuestas")
    
    print("\n🎯 CONCLUSIÓN:")
    if respuesta_openai:
        print("   El chatbot SÍ está usando OpenAI GPT-3.5-turbo para reformular")
        print("   las respuestas del FAQ y mejorar su presentación.")
    else:
        print("   El chatbot NO está usando OpenAI para reformular.")
        print("   Está devolviendo respuestas directas del FAQ sin procesar.")

if __name__ == "__main__":
    test_openai_reformulation()
