#!/usr/bin/env python3
import sys
import os
sys.path.append('.')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

from chatbot.views import ChatbotAPIView

def debug_firebase_search():
    chatbot = ChatbotAPIView()
    
    preguntas_test = [
        "¿Dónde se encuentra el psicólogo de la universidad?",
        "director de carrera de software",
        "donde esta el departamento de computacion",
        "¿Cuál es la capital de Francia?"
    ]
    
    for pregunta in preguntas_test:
        print(f"\n🔍 DEBUGGEANDO: {pregunta}")
        print("-" * 50)
        
        resultado = chatbot.busqueda_firebase_inteligente(pregunta)
        
        if resultado:
            print(f"✅ ENCONTRÓ MATCH:")
            print(f"   📊 Score: {resultado['score']}")
            print(f"   🎯 Similitud: {resultado['similitud_exacta']}")
            print(f"   ❓ Pregunta original: {resultado['pregunta_original']}")
            print(f"   💬 Respuesta: {resultado['respuesta']}")
            
            # Verificar si pasaría el umbral
            if resultado['score'] >= 12:
                print(f"   ✅ PASARÍA umbral (>=12)")
            else:
                print(f"   ❌ NO pasaría umbral (<12)")
        else:
            print(f"❌ NO encontró match en Firebase")

if __name__ == "__main__":
    debug_firebase_search()
