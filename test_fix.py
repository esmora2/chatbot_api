#!/usr/bin/env python3
"""
Probar el chatbot con las preguntas problemáticas
"""
import requests
import json

def test_problematic_questions():
    url = "http://127.0.0.1:8000/api/chatbot/"
    
    preguntas = [
        "¿Dónde se encuentra el psicólogo de la universidad?",
        "donde esta el departamento de computacion"
    ]
    
    print("🧪 Probando preguntas que tenían problemas...\n")
    
    for i, pregunta in enumerate(preguntas, 1):
        print(f"{i}. Pregunta: {pregunta}")
        
        try:
            response = requests.post(url, 
                                   json={'pregunta': pregunta},
                                   timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Respuesta: {data.get('respuesta', '')}")
                print(f"   🔍 Fuente: {data.get('fuente', 'N/A')}")
                print(f"   📊 Método: {data.get('metodo', 'N/A')}")
                if 'score' in data:
                    print(f"   🎯 Score: {data['score']}")
            else:
                print(f"   ❌ Error HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Excepción: {e}")
        
        print()

if __name__ == "__main__":
    test_problematic_questions()
