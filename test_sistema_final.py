#!/usr/bin/env python3
import requests
import json

def test_sistema_simplificado():
    url = "http://127.0.0.1:8000/api/chatbot/"
    
    tests = [
        {
            "pregunta": "¿Dónde se encuentra el psicólogo de la universidad?",
            "esperado": "Respuesta directa de Firebase sin alucinaciones"
        },
        {
            "pregunta": "donde esta el departamento de computacion", 
            "esperado": "Respuesta de Firebase o CSV sin alucinaciones"
        },
        {
            "pregunta": "¿Cuál es la capital de Francia?",
            "esperado": "Restricción - NO debe responder París"
        },
        {
            "pregunta": "¿Cómo está el clima hoy?",
            "esperado": "Restricción - fuera de contexto"
        },
        {
            "pregunta": "Hola, ¿cómo estás?",
            "esperado": "Saludo básico"
        }
    ]
    
    print("🧪 PROBANDO SISTEMA SIMPLIFICADO (sin reformulación)")
    print("=" * 60)
    
    for i, test in enumerate(tests, 1):
        print(f"\n{i}. Pregunta: {test['pregunta']}")
        print(f"   Esperado: {test['esperado']}")
        
        data = {"pregunta": test["pregunta"]}
        
        try:
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                respuesta = result.get('respuesta', 'No disponible')
                metodo = result.get('metodo', 'No disponible')
                fuente = result.get('fuente', 'No disponible')
                
                print(f"   ✅ Respuesta: {respuesta}")
                print(f"   📊 Método: {metodo}")
                print(f"   🔍 Fuente: {fuente}")
                
                # Verificar si es apropiada
                if "parís" in respuesta.lower() or "francia" in respuesta.lower():
                    print("   ❌ PROBLEMA: Respondió pregunta fuera de contexto!")
                elif metodo == "firebase_directa":
                    print("   ✅ PERFECTO: Respuesta directa de Firebase")
                elif "contexto" in metodo.lower() or "restriccion" in metodo.lower():
                    print("   ✅ BIEN: Detectó pregunta fuera de contexto")
                    
            else:
                print(f"   ❌ Error HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Error: {e}")

if __name__ == "__main__":
    test_sistema_simplificado()
