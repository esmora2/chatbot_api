#!/usr/bin/env python3
"""
Diagnóstico del problema con la pregunta "¿Qué es el DCCO?"
"""
import os
import sys
import django

sys.path.append('/home/erickxse/visual/asegcbot/chatbot_api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

from chatbot.firebase_embeddings import firebase_embeddings

def diagnosticar_problema_dcco():
    print("🔍 DIAGNÓSTICO: ¿Por qué 'que es el DCCO?' devuelve respuesta sobre Monster?")
    print("=" * 80)
    
    pregunta_problematica = "que es el DCCO?"
    
    print(f"📝 Pregunta problemática: '{pregunta_problematica}'")
    print()
    
    # 1. Probar búsqueda híbrida en Firebase
    print("1️⃣ RESULTADO DE FIREBASE RAG:")
    resultado_firebase = firebase_embeddings.buscar_hibrida(pregunta_problematica)
    
    if resultado_firebase.get('found'):
        print(f"   ✅ Encontrado: {resultado_firebase['found']}")
        print(f"   📊 Similitud: {resultado_firebase.get('similarity', 0):.3f}")
        print(f"   🔧 Método: {resultado_firebase.get('metodo', 'N/A')}")
        print(f"   ❓ Pregunta original: '{resultado_firebase.get('pregunta_original', 'N/A')}'")
        print(f"   💬 Respuesta: '{resultado_firebase.get('answer', 'N/A')[:100]}...'")
        print()
        
        # Mostrar detalles de todos los resultados
        print("📊 DETALLE DE RESULTADOS ENCONTRADOS:")
        resultados_detalle = resultado_firebase.get('resultados_detalle', [])
        for i, resultado in enumerate(resultados_detalle):
            print(f"   {i+1}. Score: {resultado.get('peso_total', 0):.3f} | Método: {resultado.get('metodo', 'N/A')}")
            print(f"      Pregunta: '{resultado['documento']['pregunta']}'")
            print(f"      Respuesta: '{resultado['documento']['respuesta'][:80]}...'")
            print()
    else:
        print("   ❌ No encontrado en Firebase")
        print()
    
    # 2. Probar solo búsqueda semántica
    print("2️⃣ SOLO BÚSQUEDA SEMÁNTICA:")
    resultados_semanticos = firebase_embeddings.buscar_semantica(pregunta_problematica, top_k=5, umbral=0.5)
    
    if resultados_semanticos:
        for i, resultado in enumerate(resultados_semanticos):
            print(f"   {i+1}. Score: {resultado['score']:.3f}")
            print(f"      Pregunta: '{resultado['documento']['pregunta']}'")
            print(f"      Respuesta: '{resultado['documento']['respuesta'][:80]}...'")
            print()
    else:
        print("   ❌ No hay resultados semánticos")
        print()
    
    # 3. Buscar manualmente preguntas relacionadas con DCCO
    print("3️⃣ BÚSQUEDA MANUAL DE PREGUNTAS DCCO:")
    try:
        from chatbot.firebase_service import FirebaseService
        firebase_service = FirebaseService()
        
        faqs = firebase_service.get_all_faqs()
        preguntas_dcco = []
        
        for faq in faqs:
            pregunta = faq.get('pregunta', '').lower()
            if 'dcco' in pregunta:
                preguntas_dcco.append({
                    'pregunta': faq.get('pregunta', ''),
                    'respuesta': faq.get('respuesta', '')[:100]
                })
        
        print(f"   📊 Total preguntas con 'DCCO': {len(preguntas_dcco)}")
        for i, faq in enumerate(preguntas_dcco):
            print(f"   {i+1}. '{faq['pregunta']}'")
            print(f"      → '{faq['respuesta']}...'")
            print()
            
    except Exception as e:
        print(f"   ❌ Error en búsqueda manual: {e}")
    
    # 4. Analizar por qué Monster gana
    print("4️⃣ ANÁLISIS DEL PROBLEMA:")
    print("   🔍 Hipótesis posibles:")
    print("   1. La pregunta 'Monster' tiene embedding más similar")
    print("   2. El algoritmo de peso está mal calibrado")
    print("   3. Falta una pregunta específica '¿Qué es el DCCO?' en Firebase")
    print("   4. El umbral de similitud está muy bajo")
    print()
    
    # 5. Verificar si existe pregunta directa sobre qué es DCCO
    print("5️⃣ VERIFICACIÓN DE PREGUNTA DIRECTA:")
    pregunta_directa_encontrada = False
    for faq in faqs:
        pregunta = faq.get('pregunta', '').lower()
        if any(termino in pregunta for termino in ['qué es el dcco', 'que es el dcco', 'qué es dcco', 'que es dcco']):
            print(f"   ✅ Encontrada: '{faq.get('pregunta', '')}'")
            print(f"      → '{faq.get('respuesta', '')[:100]}...'")
            pregunta_directa_encontrada = True
    
    if not pregunta_directa_encontrada:
        print("   ❌ NO existe una pregunta directa '¿Qué es el DCCO?' en Firebase")
        print("   💡 SOLUCIÓN: Agregar esta pregunta específica a Firebase")

if __name__ == "__main__":
    diagnosticar_problema_dcco()
