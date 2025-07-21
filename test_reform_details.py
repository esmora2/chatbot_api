#!/usr/bin/env python3
import requests
import json

def test_reformulation():
    url = "http://127.0.0.1:8000/api/chatbot/"
    
    preguntas = [
        "¿Dónde se encuentra el psicólogo de la universidad?",
        "¿Cuál es la capital de Francia?",
    ]
    
    for pregunta in preguntas:
        print(f"\n🔍 Probando: {pregunta}")
        
        data = {"pregunta": pregunta}
        
        try:
            response = requests.post(url, json=data, timeout=20)
            result = response.json()
            
            print(f"✅ Status: {response.status_code}")
            print(f"📄 Respuesta: {result.get('respuesta', 'No disponible')}")
            print(f"🔍 Fuente: {result.get('fuente', 'No disponible')}")
            print(f"📊 Método: {result.get('metodo', 'No disponible')}")
            if 'score' in result:
                print(f"🎯 Score: {result['score']}")
            
        except Exception as e:
            print(f"💥 Error: {e}")

if __name__ == "__main__":
    test_reformulation()
