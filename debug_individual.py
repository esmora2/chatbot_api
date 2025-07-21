#!/usr/bin/env python3
import requests
import json

def test_debug_individual():
    url = "http://127.0.0.1:8000/api/chatbot/"
    
    # Preguntas específicas problemáticas
    preguntas_problema = [
        "¿Cuál es la capital de Francia?",
        "donde esta el departamento de computacion"
    ]
    
    # Preguntas que funcionan
    preguntas_ok = [
        "¿Cómo está el clima hoy?",
        "¿Dónde se encuentra el psicólogo de la universidad?"
    ]
    
    print("🔍 DEBUGGEANDO PREGUNTAS PROBLEMÁTICAS")
    print("=" * 50)
    
    for pregunta in preguntas_problema:
        print(f"\n❌ PROBLEMÁTICA: {pregunta}")
        
        try:
            response = requests.post(url, json={"pregunta": pregunta}, timeout=5)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ Respuesta: {result.get('respuesta', 'N/A')[:100]}...")
                print(f"   📊 Método: {result.get('metodo', 'N/A')}")
            elif response.status_code == 500:
                print(f"   💥 ERROR 500: {response.text}")
            else:
                print(f"   ⚠️ Otro error: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ TIMEOUT después de 5 segundos")
        except Exception as e:
            print(f"   💥 Excepción: {e}")
    
    print(f"\n" + "=" * 50)
    print("✅ PREGUNTAS QUE FUNCIONAN")
    print("=" * 50)
    
    for pregunta in preguntas_ok:
        print(f"\n✅ FUNCIONA: {pregunta}")
        
        try:
            response = requests.post(url, json={"pregunta": pregunta}, timeout=3)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   📊 Método: {result.get('metodo', 'N/A')}")
            
        except Exception as e:
            print(f"   💥 Error inesperado: {e}")

if __name__ == "__main__":
    test_debug_individual()
