#!/usr/bin/env python3
"""
Script para probar la API del chatbot con la nueva arquitectura RAG
"""

import requests
import json
import sys

def test_chatbot_api():
    url = "http://127.0.0.1:8000/api/chatbot/"
    
    # Lista de preguntas de prueba
    preguntas_test = [
        "¿Dónde está el psicólogo?",
        "director de software",
        "departamento de computación",
        "¿Cuándo son las clases de programación?",
        "¿Quién es el coordinador?",
        "hola"
    ]
    
    print("🧪 Probando API del chatbot con arquitectura RAG...")
    print("=" * 60)
    
    for i, pregunta in enumerate(preguntas_test, 1):
        print(f"\n{i}. Pregunta: '{pregunta}'")
        print("-" * 40)
        
        try:
            # Hacer la consulta
            response = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={"pregunta": pregunta},
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Respuesta: {data.get('respuesta', 'N/A')}")
                print(f"📁 Fuente: {data.get('fuente', 'N/A')}")
                print(f"🔧 Método: {data.get('metodo', 'N/A')}")
                if 'confidence' in data:
                    print(f"📊 Confidence: {data['confidence']}")
                if 'pregunta_relacionada' in data:
                    print(f"🔗 Pregunta relacionada: {data['pregunta_relacionada']}")
            else:
                print(f"❌ Error: {response.status_code}")
                print(f"Response: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
        
        print()

if __name__ == "__main__":
    test_chatbot_api()
