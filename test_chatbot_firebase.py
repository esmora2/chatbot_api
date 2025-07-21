#!/usr/bin/env python3
"""
Script para probar el chatbot con Firebase
"""
import os
import django
from dotenv import load_dotenv

load_dotenv()

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

from chatbot.views import ChatbotHibridoAPIView
from rest_framework.test import APIRequestFactory

def test_chatbot_firebase():
    """Probar el chatbot con algunas preguntas"""
    
    factory = APIRequestFactory()
    view = ChatbotHibridoAPIView()
    
    preguntas_test = [
        "¿Dónde está el psicólogo?",
        "¿Dónde se encuentra el departamento de computación?",
        "¿Cada cuánto dan las becas?",
        "¿Dónde puedo comer?"
    ]
    
    print("🤖 Probando chatbot con Firebase...\n")
    
    for i, pregunta in enumerate(preguntas_test, 1):
        print(f"{i}. Pregunta: {pregunta}")
        
        try:
            # Crear request simulado
            request = factory.post('/api/chatbot/', {'pregunta': pregunta})
            request.data = {'pregunta': pregunta}
            
            # Llamar al método del chatbot
            response = view.post(request)
            
            if response.status_code == 200:
                data = response.data
                print(f"   ✅ Respuesta: {data.get('respuesta', '')[:100]}...")
                print(f"   🔍 Fuente: {data.get('fuente', 'N/A')}")
                print(f"   📊 Método: {data.get('metodo', 'N/A')}")
                if 'score' in data:
                    print(f"   🎯 Score: {data['score']}")
            else:
                print(f"   ❌ Error: {response.data}")
                
        except Exception as e:
            print(f"   💥 Excepción: {e}")
        
        print()

if __name__ == "__main__":
    test_chatbot_firebase()
