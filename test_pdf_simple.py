#!/usr/bin/env python3
"""
Pruebas simples para verificar el PDF de aplicaciones basadas en el conocimiento
"""
import requests
import json

BASE_URL = "http://localhost:8000/chatbot"

def probar_pdf_aplicaciones():
    """
    Prueba específica para el PDF de aplicaciones basadas en el conocimiento
    """
    print("🔍 PROBANDO PDF: espe_software_aplicaciones_basadas_en_el_conocimiento.pdf")
    print("=" * 70)
    
    # Preguntas específicas sobre aplicaciones basadas en conocimiento
    preguntas = [
        "¿Qué es aplicaciones basadas en el conocimiento?",
        "¿Cuál es el contenido de aplicaciones basadas en el conocimiento?",
        "¿Qué temas incluye la materia de aplicaciones basadas en el conocimiento?",
        "¿Hay información sobre sistemas expertos?",
        "¿Qué syllabus tiene aplicaciones basadas en el conocimiento?",
        "¿Cuáles son los objetivos de aplicaciones basadas en el conocimiento?",
        "¿Qué metodología se usa en aplicaciones basadas en el conocimiento?",
        "¿Cuál es la bibliografía de aplicaciones basadas en el conocimiento?"
    ]
    
    for i, pregunta in enumerate(preguntas, 1):
        print(f"\n{i}. ❓ {pregunta}")
        print("-" * 50)
        
        try:
            response = requests.post(
                f"{BASE_URL}/",
                headers={"Content-Type": "application/json"},
                json={"pregunta": pregunta}
            )
            
            if response.status_code == 200:
                data = response.json()
                respuesta = data.get("respuesta", "")
                fuente = data.get("fuente", "")
                metodo = data.get("metodo", "")
                
                print(f"📤 Respuesta: {respuesta[:200]}...")
                print(f"📍 Fuente: {fuente}")
                print(f"🔧 Método: {metodo}")
                
                # Verificar si la respuesta parece venir del PDF
                if "aplicaciones basadas" in respuesta.lower() or "conocimiento" in respuesta.lower():
                    print("✅ Respuesta relevante al PDF")
                else:
                    print("⚠️  Respuesta podría no venir del PDF")
                    
            else:
                print(f"❌ Error HTTP: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("🎯 CONCLUSIONES:")
    print("- Si las respuestas mencionan contenido específico del syllabus, el PDF funciona")
    print("- Si respuestas son genéricas, el PDF podría no estar cargado")
    print("- Verificar que el archivo esté en media/docs/")

def verificar_contexto_pdf():
    """
    Verifica si el chatbot puede acceder al contenido del PDF
    """
    print("\n🔍 VERIFICANDO ACCESO AL CONTENIDO DEL PDF")
    print("=" * 50)
    
    # Consultas muy específicas que deberían estar en el PDF
    consultas_especificas = [
        "syllabus aplicaciones basadas conocimiento",
        "contenido programático aplicaciones conocimiento",
        "objetivos aplicaciones basadas conocimiento",
        "evaluación aplicaciones basadas conocimiento"
    ]
    
    for consulta in consultas_especificas:
        print(f"\n🔍 Probando: '{consulta}'")
        
        try:
            response = requests.post(
                f"{BASE_URL}/test-context/",
                headers={"Content-Type": "application/json"},
                json={"pregunta": consulta}
            )
            
            if response.status_code == 200:
                data = response.json()
                documentos = data.get("documentos_encontrados", 0)
                relevancia = data.get("relevancia_promedio", 0)
                
                print(f"   📊 Documentos encontrados: {documentos}")
                print(f"   📈 Relevancia promedio: {relevancia}")
                
                if documentos > 0 and relevancia > 0.2:
                    print("   ✅ Contenido relevante encontrado")
                else:
                    print("   ⚠️  Contenido podría no estar disponible")
                    
        except Exception as e:
            print(f"   ❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 INICIANDO PRUEBAS DEL PDF")
    print("Asegúrate de que el servidor esté ejecutándose en localhost:8000")
    print()
    
    probar_pdf_aplicaciones()
    verificar_contexto_pdf()
    
    print("\n🎯 PARA VERIFICAR MANUALMENTE:")
    print("1. Revisar que el archivo esté en: media/docs/espe_software_aplicaciones_basadas_en_el_conocimiento.pdf")
    print("2. Verificar que el archivo no esté corrupto")
    print("3. Reiniciar el servidor Django para recargar documentos")
    print("4. Ejecutar: python verificar_pdf.py (script más detallado)")
