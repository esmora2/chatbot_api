#!/usr/bin/env python3
"""
Script para agregar pregunta específica sobre el DCCO a Firebase
"""
import os
import sys
import django

# Configurar Django
sys.path.append('/home/erickxse/visual/asegcbot/chatbot_api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

def agregar_pregunta_dcco():
    """
    Agrega la pregunta específica sobre qué es el DCCO
    """
    print("📝 AGREGANDO PREGUNTA '¿Qué es el DCCO?' A FIREBASE")
    print("=" * 60)
    
    try:
        from chatbot.firebase_service import firebase_service
        
        # Verificar conexión
        if not firebase_service.is_connected():
            print("❌ Error: Firebase no está conectado")
            return False
        
        # Definir la pregunta y respuesta
        pregunta = "¿Qué es el DCCO?"
        respuesta = """El DCCO es el Departamento de Ciencias de la Computación de la Universidad ESPE (Universidad de las Fuerzas Armadas). 

Es una unidad académica especializada en la formación de profesionales en el campo de la informática y la tecnología. El DCCO ofrece las siguientes carreras:

• Ingeniería en Software
• Tecnologías de la Información  
• Sistemas de Información
• Ciencias de la Computación

Sus materias destacadas incluyen:
• Aplicaciones Basadas en el Conocimiento (sistemas expertos, IA, minería de datos)
• Aplicaciones Distribuidas (sistemas distribuidos, microservicios)
• Programación Web, Base de Datos, Estructura de Datos, Algoritmos

El DCCO está ubicado en el Campus Sangolquí de la ESPE y cuenta con directores especializados como el Ing. Mauricio Campaña (Director de la carrera de Software)."""
        
        categoria = "Información Institucional"
        
        # Agregar a Firebase
        exito, mensaje = firebase_service.add_faq(pregunta, respuesta, categoria)
        
        if exito:
            print(f"✅ {mensaje}")
            
            # Verificar que se agregó correctamente
            print("\n🔍 Verificando que se agregó correctamente...")
            faqs = firebase_service.search_faqs("DCCO", limit=3)
            
            if faqs:
                print(f"✅ Encontradas {len(faqs)} FAQs relacionadas con DCCO")
                for faq in faqs:
                    print(f"   - {faq['pregunta'][:50]}...")
            else:
                print("⚠️ No se encontraron FAQs con DCCO (puede tardar unos segundos en indexarse)")
            
            # Probar búsqueda semántica también
            print("\n🔍 Probando búsqueda semántica...")
            from chatbot.firebase_embeddings import firebase_embeddings
            
            # Recargar índice para incluir la nueva FAQ
            firebase_embeddings._initialized = False
            resultado = firebase_embeddings.buscar_hibrida("¿Qué es el DCCO?")
            
            if resultado.get('found'):
                print(f"✅ Búsqueda semántica exitosa:")
                print(f"   - Método: {resultado['metodo']}")
                print(f"   - Similitud: {resultado['similarity']:.3f}")
                print(f"   - Respuesta: {resultado['answer'][:100]}...")
            else:
                print("⚠️ Búsqueda semántica no encontró resultado inmediato")
            
            return True
        else:
            print(f"❌ Error: {mensaje}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def probar_chatbot():
    """
    Prueba el chatbot con la pregunta para verificar que funciona
    """
    print("\n🤖 PROBANDO CHATBOT CON LA PREGUNTA...")
    print("=" * 50)
    
    try:
        import requests
        
        # Hacer solicitud al chatbot
        response = requests.post(
            'http://localhost:8000/chatbot/',
            headers={'Content-Type': 'application/json'},
            json={'pregunta': '¿Qué es el DCCO?'},
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Respuesta del chatbot:")
            print(f"   - Método: {data.get('metodo', 'N/A')}")
            print(f"   - Fuente: {data.get('fuente', 'N/A')}")
            print(f"   - Respuesta: {data.get('respuesta', 'N/A')[:200]}...")
            
            # Verificar que no responda sobre Monster
            if "monster" in data.get('respuesta', '').lower():
                print("⚠️ ADVERTENCIA: Aún responde sobre Monster en lugar del DCCO")
                return False
            else:
                print("✅ Respuesta correcta, no menciona Monster")
                return True
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando chatbot: {e}")
        return False

if __name__ == "__main__":
    # Paso 1: Agregar pregunta a Firebase
    if agregar_pregunta_dcco():
        print("\n" + "="*60)
        
        # Paso 2: Probar chatbot
        import time
        print("⏳ Esperando 3 segundos para que se actualice el índice...")
        time.sleep(3)
        
        if probar_chatbot():
            print("\n🎉 ¡SUCCESS! La pregunta sobre DCCO se agregó y funciona correctamente")
        else:
            print("\n⚠️ La pregunta se agregó pero aún hay problemas en el chatbot")
    else:
        print("\n❌ No se pudo agregar la pregunta a Firebase")
