#!/usr/bin/env python3
"""
Prueba específica para verificar reformulación de respuestas Firebase RAG
"""
import os
import sys
import django
import requests
import json

sys.path.append('/home/erickxse/visual/asegcbot/chatbot_api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

def test_firebase_rag_reformulation():
    """
    Prueba que las respuestas de Firebase RAG sean reformuladas por OpenAI
    """
    print("🧪 PRUEBA: REFORMULACIÓN DE FIREBASE RAG CON OPENAI")
    print("=" * 60)
    
    # Preguntas que probablemente tengan respuestas en Firebase RAG
    preguntas_test = [
        "¿Quién es el director de la carrera de software?",
        "¿Cuál es el horario de atención de la secretaría?",
        "¿Dónde está ubicada la universidad?",
        "¿Qué carreras tiene el DCCO?",
        "¿Cómo contactar al departamento?"
    ]
    
    for i, pregunta in enumerate(preguntas_test, 1):
        print(f"\n{i}️⃣ PREGUNTA: {pregunta}")
        print("-" * 50)
        
        try:
            # Hacer consulta al chatbot
            response = requests.post(
                'http://localhost:8000/chatbot/',
                headers={'Content-Type': 'application/json'},
                json={'pregunta': pregunta},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                respuesta = result.get('respuesta', '')
                fuente = result.get('fuente', '')
                metodo = result.get('metodo', '')
                confidence = result.get('confidence', 0)
                
                print(f"📝 RESPUESTA: {respuesta}")
                print(f"🔍 FUENTE: {fuente}")
                print(f"⚙️  MÉTODO: {metodo}")
                print(f"🎯 CONFIDENCE: {confidence}")
                
                # Analizar si viene de Firebase RAG y si fue reformulada
                if 'firebase_rag' in metodo:
                    print("✅ Respuesta viene de Firebase RAG")
                    if 'reformulada' in metodo:
                        print("🎨 ✅ REFORMULADA CON OPENAI")
                    elif 'directa' in metodo:
                        print("📋 ⚠️  RESPUESTA DIRECTA (OpenAI falló)")
                    else:
                        print("❓ Estado de reformulación desconocido")
                else:
                    print(f"ℹ️  No viene de Firebase RAG (método: {metodo})")
                
            else:
                print(f"❌ Error HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error de conexión: {e}")
        except Exception as e:
            print(f"❌ Error inesperado: {e}")
    
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE LA PRUEBA:")
    print("   - Esta prueba verifica que las respuestas de Firebase RAG")
    print("     sean reformuladas por OpenAI para mejorar su presentación")
    print("   - Buscar métodos que contengan 'firebase_rag_*_reformulada'")
    print("   - Si ves 'firebase_rag_*_directa' significa que OpenAI falló")
    print("     y se usó la respuesta original sin reformular")

if __name__ == "__main__":
    test_firebase_rag_reformulation()
