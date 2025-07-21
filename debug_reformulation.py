#!/usr/bin/env python3
import sys
import os
sys.path.append('.')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

from chatbot.views import consultar_llm_inteligente

def test_reformulation_debug():
    respuesta_original = "En bienestar estudiantil, junto al bar"
    
    prompt = f"""Eres un asistente virtual del Departamento de Ciencias de la Computación de la ESPE.

Tu tarea es reformular la siguiente respuesta para que suene más natural y conversacional, manteniendo EXACTAMENTE la misma información factual.

RESPUESTA ORIGINAL:
{respuesta_original}

REGLAS ESTRICTAS:
1. Mantén todos los datos exactos (ubicaciones, nombres, horarios, etc.)
2. NO agregues información nueva
3. NO cambies el significado
4. Hazla más natural y amigable
5. Responde SOLO con la versión reformulada

RESPUESTA REFORMULADA:"""
    
    print("🦙 Probando reformulación con llama3:latest...")
    print(f"📝 Respuesta original: {respuesta_original}")
    print(f"📏 Longitud original: {len(respuesta_original)}")
    
    try:
        respuesta_reformulada = consultar_llm_inteligente(prompt)
        
        print(f"✅ Respuesta reformulada: {respuesta_reformulada}")
        
        if respuesta_reformulada:
            print(f"📏 Longitud reformulada: {len(respuesta_reformulada)}")
            print(f"📊 Límite máximo (x2): {len(respuesta_original) * 2}")
            
            # Verificar validaciones
            print(f"\n🔍 Verificando validaciones:")
            print(f"- len >= 10: {len(respuesta_reformulada.strip()) >= 10}")
            print(f"- len <= original*2: {len(respuesta_reformulada) <= len(respuesta_original) * 2}")
            print(f"- no contiene 'no puedo': {'no puedo' not in respuesta_reformulada.lower()}")
            print(f"- no contiene 'información personal': {'información personal' not in respuesta_reformulada.lower()}")
            print(f"- no contiene 'respuesta reformulada': {'respuesta reformulada' not in respuesta_reformulada.lower()}")
            
            # Resultado final
            if (respuesta_reformulada and 
                len(respuesta_reformulada.strip()) >= 10 and
                len(respuesta_reformulada) <= len(respuesta_original) * 2 and
                "no puedo" not in respuesta_reformulada.lower() and
                "información personal" not in respuesta_reformulada.lower() and
                "respuesta reformulada" not in respuesta_reformulada.lower()):
                print("✅ PASARÍA todas las validaciones")
            else:
                print("❌ FALLARÍA alguna validación")
        else:
            print("❌ Respuesta es None")
        
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    test_reformulation_debug()
