#!/usr/bin/env python3
"""
Script de prueba para verificar que OpenAI funciona correctamente
"""
import os
import sys
import django
from dotenv import load_dotenv

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

# Importar después de configurar Django
from chatbot.views import consultar_openai

def test_openai_connection():
    """Prueba la conexión con OpenAI"""
    print("🚀 Probando conexión con OpenAI GPT-3.5-turbo...")
    print("=" * 50)
    
    # Prompt de prueba simple
    prompt_test = """Eres un asistente del DCCO de la ESPE. 
Responde brevemente: ¿Qué es el Departamento de Ciencias de la Computación?"""
    
    try:
        respuesta = consultar_openai(prompt_test)
        
        if respuesta:
            print("✅ CONEXIÓN EXITOSA con OpenAI!")
            print(f"📝 Respuesta recibida ({len(respuesta)} caracteres):")
            print("-" * 30)
            print(respuesta)
            print("-" * 30)
            return True
        else:
            print("❌ Error: No se recibió respuesta de OpenAI")
            return False
            
    except Exception as e:
        print(f"❌ Error al conectar con OpenAI: {e}")
        return False

def test_api_key():
    """Verifica que la API key esté configurada"""
    from django.conf import settings
    
    api_key = getattr(settings, 'OPENAI_API_KEY', '')
    
    if not api_key:
        print("❌ OPENAI_API_KEY no está configurada en settings")
        return False
    elif api_key in ['your-openai-api-key-here', '']:
        print("❌ OPENAI_API_KEY contiene un valor placeholder")
        return False
    elif len(api_key) < 20:
        print("❌ OPENAI_API_KEY parece ser muy corta")
        return False
    else:
        print(f"✅ OPENAI_API_KEY configurada correctamente (longitud: {len(api_key)})")
        print(f"🔑 Inicio de la key: {api_key[:10]}...")
        return True

if __name__ == "__main__":
    print("🔍 VERIFICACIÓN DE CONFIGURACIÓN OPENAI")
    print("=" * 50)
    
    # 1. Verificar API Key
    if not test_api_key():
        print("\n❌ Configuración de API Key incorrecta. Verifica tu archivo .env")
        sys.exit(1)
    
    print()
    
    # 2. Probar conexión
    if test_openai_connection():
        print("\n🎉 ¡Todo funciona correctamente!")
        print("Tu chatbot está listo para usar OpenAI GPT-3.5-turbo")
    else:
        print("\n❌ Hay problemas con la conexión a OpenAI")
        print("Verifica tu API key y conexión a internet")
        sys.exit(1)
