#!/usr/bin/env python3
import sys
import os
sys.path.append('.')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

from chatbot.views import consultar_llm_inteligente

def test_simple_prompt():
    respuesta_base = "En bienestar estudiantil, junto al bar"
    
    prompt = f"""Mejora la redacción de esta respuesta sin cambiar la información:

Respuesta original: {respuesta_base}

Mejorada:"""
    
    print("🦙 Probando prompt simple...")
    print(f"📝 Prompt enviado:")
    print(prompt)
    print(f"\n🔄 Enviando a Llama...")
    
    try:
        respuesta = consultar_llm_inteligente(prompt)
        print(f"✅ Respuesta de Llama: {respuesta}")
        
        # Verificar condiciones de fallback
        print(f"\n🔍 Verificando condiciones:")
        print(f"- respuesta_reformulada is None: {respuesta is None}")
        if respuesta:
            print(f"- len(respuesta_reformulada): {len(respuesta)}")
            print(f"- len(respuesta_base) * 2: {len(respuesta_base) * 2}")
            print(f"- Respuesta muy larga: {len(respuesta) > len(respuesta_base) * 2}")
            print(f"- Contiene 'no puedo': {'no puedo' in respuesta.lower()}")
            print(f"- Contiene 'información personal': {'información personal' in respuesta.lower()}")
            
            if (len(respuesta) > len(respuesta_base) * 2 or
                "no puedo" in respuesta.lower() or
                "información personal" in respuesta.lower()):
                print("❌ Activará FALLBACK")
            else:
                print("✅ Usará respuesta de Llama")
        
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    test_simple_prompt()
