#!/usr/bin/env python3
"""
Probar el chatbot con reformulación de Llama habilitada
"""
import requests
import json

def test_llama_reformulation():
    url = "http://127.0.0.1:8000/api/chatbot/"
    
    preguntas = [
        # Pregunta que debería encontrar en Firebase y reformular
        "¿Dónde se encuentra el psicólogo de la universidad?",
        
        # Pregunta que debería encontrar en Firebase y reformular  
        "donde esta el departamento de computacion",
        
        # Pregunta fuera de contexto (debería usar Llama para responder amablemente)
        "¿Cuál es la capital de Francia?",
        
        # Saludo básico
        "Hola, ¿cómo estás?"
    ]
    
    print("🦙 Probando Llama para reformulación...\n")
    
    for i, pregunta in enumerate(preguntas, 1):
        print(f"{i}. Pregunta: {pregunta}")
        
        try:
            response = requests.post(url, 
                                   json={'pregunta': pregunta},
                                   timeout=15)  # Más tiempo para Llama
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Respuesta: {data.get('respuesta', '')}")
                print(f"   🔍 Fuente: {data.get('fuente', 'N/A')}")
                print(f"   📊 Método: {data.get('metodo', 'N/A')}")
                if 'score' in data:
                    print(f"   🎯 Score: {data['score']}")
                    
                # Verificar si usó Llama
                metodo = data.get('metodo', '')
                if 'llama' in metodo.lower() or 'reformulada' in metodo:
                    print(f"   🦙 ¡Usó Llama para reformular!")
                else:
                    print(f"   ⚠️  No usó Llama")
                    
            else:
                print(f"   ❌ Error HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Excepción: {e}")
        
        print()

if __name__ == "__main__":
    test_llama_reformulation()
