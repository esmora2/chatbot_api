#!/usr/bin/env python3
import requests
import json

def test_api_mejorada():
    url = "http://127.0.0.1:8000/api/chatbot/"
    
    tests = [
        {
            "pregunta": "director de carrera de software",
            "esperado": "Firebase (no CSV backup)"
        },
        {
            "pregunta": "donde esta el departamento de computacion", 
            "esperado": "Firebase (no CSV backup)"
        },
        {
            "pregunta": "¿Dónde se encuentra el psicólogo de la universidad?",
            "esperado": "Firebase"
        }
    ]
    
    print("🧪 PROBANDO API CON ALGORITMO MEJORADO")
    print("=" * 60)
    
    for i, test in enumerate(tests, 1):
        print(f"\n{i}. Pregunta: {test['pregunta']}")
        print(f"   Esperado: {test['esperado']}")
        
        data = {"pregunta": test["pregunta"]}
        
        try:
            response = requests.post(url, json=data, timeout=8)
            
            if response.status_code == 200:
                result = response.json()
                respuesta = result.get('respuesta', 'No disponible')
                metodo = result.get('metodo', 'No disponible')
                fuente = result.get('fuente', 'No disponible')
                score = result.get('score', 'No disponible')
                
                print(f"   ✅ Respuesta: {respuesta[:100]}...")
                print(f"   📊 Método: {metodo}")
                print(f"   🔍 Fuente: {fuente}")
                print(f"   🎯 Score: {score}")
                
                # Verificar si usa Firebase en lugar de CSV
                if "Firebase" in fuente and "CSV" not in fuente:
                    print(f"   🎉 PERFECTO: Usando Firebase!")
                elif "CSV" in fuente:
                    print(f"   ⚠️ ADVERTENCIA: Aún usa CSV backup")
                    
            else:
                print(f"   ❌ Error HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Error: {e}")

if __name__ == "__main__":
    test_api_mejorada()
