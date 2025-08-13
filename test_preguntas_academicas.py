#!/usr/bin/env python3
"""
Prueba para verificar que preguntas académicas válidas sean procesadas correctamente
"""
import os
import sys
import django
import requests
import json

sys.path.append('/home/erickxse/visual/asegcbot/chatbot_api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

def test_preguntas_academicas_validas():
    """
    Prueba preguntas que están en contexto académico pero pueden no tener documentos específicos
    """
    print("🧪 PRUEBA: PREGUNTAS ACADÉMICAS VÁLIDAS")
    print("=" * 60)
    print("Verificando que preguntas como 'dónde queda la ESPE' y")
    print("'de qué trata aplicaciones basadas en el conocimiento' sean procesadas")
    print("=" * 60)
    
    # Preguntas que deberían ser procesadas, no rechazadas
    preguntas_academicas = [
        "¿Dónde queda la ESPE?",
        "¿De qué se trata la materia de aplicaciones basadas en el conocimiento?",
        "¿Qué carreras tiene el DCCO?",
        "¿Cómo llegar a la universidad ESPE?",
        "¿Qué es el departamento de ciencias de la computación?",
        "¿Cuáles son las materias de ingeniería en software?",
        "¿Dónde está ubicado el campus de la ESPE?",
        "¿Qué se estudia en tecnologías de la información?",
        "¿De qué trata la materia de aplicaciones distribuidas?",
        "¿Quién es el director del DCCO?"
    ]
    
    resultados = {
        "procesadas_correctamente": 0,
        "rechazadas_incorrectamente": 0,
        "detalles": []
    }
    
    for i, pregunta in enumerate(preguntas_academicas, 1):
        print(f"\n{i}️⃣ PREGUNTA: {pregunta}")
        print("-" * 50)
        
        try:
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
                
                print(f"📝 RESPUESTA: {respuesta[:150]}...")
                print(f"🔍 FUENTE: {fuente}")
                print(f"⚙️  MÉTODO: {metodo}")
                
                # Analizar si fue procesada correctamente
                if metodo in ['sin_contexto_relevante', 'fuera_de_contexto', 'respuesta_no_relevante']:
                    print("❌ RECHAZADA INCORRECTAMENTE")
                    resultados["rechazadas_incorrectamente"] += 1
                    resultados["detalles"].append({
                        "pregunta": pregunta,
                        "estado": "rechazada",
                        "metodo": metodo
                    })
                else:
                    print("✅ PROCESADA CORRECTAMENTE")
                    resultados["procesadas_correctamente"] += 1
                    resultados["detalles"].append({
                        "pregunta": pregunta,
                        "estado": "procesada",
                        "metodo": metodo,
                        "fuente": fuente
                    })
                
            else:
                print(f"❌ Error HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Mostrar resumen
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE RESULTADOS:")
    print(f"✅ Procesadas correctamente: {resultados['procesadas_correctamente']}")
    print(f"❌ Rechazadas incorrectamente: {resultados['rechazadas_incorrectamente']}")
    print(f"📈 Tasa de éxito: {(resultados['procesadas_correctamente']/len(preguntas_academicas)*100):.1f}%")
    
    if resultados["rechazadas_incorrectamente"] > 0:
        print("\n🔧 PREGUNTAS QUE AÚN SE RECHAZAN:")
        for detalle in resultados["detalles"]:
            if detalle["estado"] == "rechazada":
                print(f"   • {detalle['pregunta']} (método: {detalle['metodo']})")
    
    print("\n🎯 OBJETIVO:")
    print("   Todas las preguntas académicas válidas deberían ser procesadas")
    print("   por OpenAI con método 'llm_academico_inteligente' o similar")

if __name__ == "__main__":
    test_preguntas_academicas_validas()
