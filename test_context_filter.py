#!/usr/bin/env python3
"""
Script de prueba para validar el filtrado de contexto del chatbot
"""
import requests
import json

# Configuración
BASE_URL = "http://localhost:8000/chatbot"
HEADERS = {"Content-Type": "application/json"}

def test_pregunta(pregunta, esperado_fuera_contexto=False):
    """
    Prueba una pregunta específica
    """
    print(f"\n🔍 Probando: '{pregunta}'")
    
    # Probar con el endpoint de análisis
    response = requests.post(
        f"{BASE_URL}/test-context/",
        headers=HEADERS,
        json={"pregunta": pregunta}
    )
    
    if response.status_code == 200:
        data = response.json()
        es_fuera_contexto = data.get("es_fuera_contexto", False)
        decision = data.get("analisis", {}).get("decision", "")
        relevancia = data.get("relevancia_promedio", 0)
        
        print(f"   📊 Análisis: {decision}")
        print(f"   🎯 Fuera de contexto: {es_fuera_contexto}")
        print(f"   📈 Relevancia promedio: {relevancia}")
        
        # Validar resultado esperado
        if esperado_fuera_contexto == es_fuera_contexto:
            print("   ✅ CORRECTO")
        else:
            print("   ❌ INCORRECTO")
            
    else:
        print(f"   ❌ Error: {response.status_code}")

def test_respuesta_chatbot(pregunta):
    """
    Prueba la respuesta real del chatbot
    """
    print(f"\n🤖 Respuesta del chatbot para: '{pregunta}'")
    
    response = requests.post(
        f"{BASE_URL}/",
        headers=HEADERS,
        json={"pregunta": pregunta}
    )
    
    if response.status_code == 200:
        data = response.json()
        respuesta = data.get("respuesta", "")
        fuente = data.get("fuente", "")
        metodo = data.get("metodo", "")
        
        print(f"   💬 Respuesta: {respuesta[:100]}...")
        print(f"   📍 Fuente: {fuente}")
        print(f"   🔧 Método: {metodo}")
        
        # Verificar si es una respuesta de fuera de contexto
        if "fuera" in metodo or "contexto" in metodo:
            print("   ✅ FILTRADO CORRECTAMENTE")
        else:
            print("   ⚠️  RESPUESTA PROCESADA")
            
    else:
        print(f"   ❌ Error: {response.status_code}")

def main():
    print("🚀 Iniciando pruebas de filtrado de contexto...")
    
    # Casos de prueba - FUERA DE CONTEXTO
    print("\n" + "="*50)
    print("📝 CASOS FUERA DE CONTEXTO")
    print("="*50)
    
    preguntas_fuera_contexto = [
        "¿Quién es el presidente de Ecuador?",
        "¿Qué país es el más grande del mundo?",
        "¿Qué hora es?",
        "¿Cuál es la capital de Francia?",
        "¿Cómo se hace una pizza?",
        "¿Quién ganó el último Mundial de fútbol?",
        "¿Cuál es el precio del dólar?",
        "¿Qué película recomiendan?",
        "¿Cómo está el clima hoy?",
        "¿Cuándo fue la Segunda Guerra Mundial?"
    ]
    
    for pregunta in preguntas_fuera_contexto:
        test_pregunta(pregunta, esperado_fuera_contexto=True)
        test_respuesta_chatbot(pregunta)
    
    # Casos de prueba - DENTRO DE CONTEXTO
    print("\n" + "="*50)
    print("📚 CASOS DENTRO DE CONTEXTO")
    print("="*50)
    
    preguntas_dentro_contexto = [
        "¿Dónde está el departamento de computación?",
        "¿Qué carreras ofrece el DCCO?",
        "¿Cuál es el horario de atención?",
        "¿Cómo me inscribo en una materia?",
        "¿Dónde está la biblioteca de la ESPE?",
        "¿Qué requisitos necesito para graduarme?",
        "¿Hay laboratorios de programación?",
        "¿Quién es el coordinador de la carrera?",
        "¿Cómo puedo acceder a becas?",
        "¿Qué es ingeniería de software?"
    ]
    
    for pregunta in preguntas_dentro_contexto:
        test_pregunta(pregunta, esperado_fuera_contexto=False)
        test_respuesta_chatbot(pregunta)
    
    print("\n" + "="*50)
    print("🎯 PRUEBAS COMPLETADAS")
    print("="*50)

if __name__ == "__main__":
    main()
