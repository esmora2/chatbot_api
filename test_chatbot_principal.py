#!/usr/bin/env python3
"""
Script para probar el chatbot principal actualizado con Firebase
"""
import requests
import json

def test_chatbot_principal():
    url = "http://127.0.0.1:8000/api/chatbot/"
    
    preguntas = [
        "¿Dónde está el psicólogo?",
        "¿Dónde se encuentra el departamento de computación?",
        "¿Cada cuánto dan las becas?",
        "¿Dónde puedo parquear?",
        "Hola, ¿cómo estás?"
    ]
    
    print("🤖 Probando chatbot principal actualizado con Firebase...\n")
    
    for i, pregunta in enumerate(preguntas, 1):
        print(f"{i}. Pregunta: {pregunta}")
        
        try:
            response = requests.post(url, 
                                   json={'pregunta': pregunta},
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Respuesta: {data.get('respuesta', '')[:100]}...")
                print(f"   🔍 Fuente: {data.get('fuente', 'N/A')}")
                print(f"   📊 Método: {data.get('metodo', 'N/A')}")
                if 'score' in data:
                    print(f"   🎯 Score: {data['score']}")
            else:
                print(f"   ❌ Error HTTP: {response.status_code}")
                print(f"   📄 Respuesta: {response.text}")
                
        except Exception as e:
            print(f"   💥 Excepción: {e}")
        
        print()

if __name__ == "__main__":
    test_chatbot_principal()
