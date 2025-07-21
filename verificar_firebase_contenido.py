#!/usr/bin/env python3
import sys
import os
sys.path.append('.')

import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

from chatbot.firebase_service import FirebaseService

def verificar_firebase():
    firebase_service = FirebaseService()
    
    print("🔍 VERIFICANDO CONTENIDO DE FIREBASE")
    print("=" * 50)
    
    try:
        faqs = firebase_service.get_all_faqs()
        print(f"📊 Total FAQs en Firebase: {len(faqs)}")
        
        # Buscar preguntas relacionadas con "director" o "software"
        preguntas_director = []
        preguntas_software = []
        
        for faq in faqs:
            pregunta = faq.get("pregunta", "").lower()
            respuesta = faq.get("respuesta", "").lower()
            
            if "director" in pregunta or "director" in respuesta:
                preguntas_director.append({
                    "pregunta": faq.get("pregunta", ""),
                    "respuesta": faq.get("respuesta", "")
                })
            
            if "software" in pregunta or "software" in respuesta:
                preguntas_software.append({
                    "pregunta": faq.get("pregunta", ""),
                    "respuesta": faq.get("respuesta", "")
                })
        
        print(f"\n👨‍💼 FAQs con 'director': {len(preguntas_director)}")
        for i, faq in enumerate(preguntas_director[:3], 1):
            print(f"   {i}. P: {faq['pregunta'][:80]}...")
            print(f"      R: {faq['respuesta'][:80]}...")
        
        print(f"\n💻 FAQs con 'software': {len(preguntas_software)}")
        for i, faq in enumerate(preguntas_software[:3], 1):
            print(f"   {i}. P: {faq['pregunta'][:80]}...")
            print(f"      R: {faq['respuesta'][:80]}...")
        
        # Buscar una coincidencia específica
        print(f"\n🔍 Buscando específicamente 'Mauricio Camapaña'...")
        mauricio_encontrado = False
        for faq in faqs:
            if "mauricio" in faq.get("respuesta", "").lower() or "camapaña" in faq.get("respuesta", "").lower():
                print(f"   ✅ ENCONTRADO:")
                print(f"      P: {faq.get('pregunta', '')}")
                print(f"      R: {faq.get('respuesta', '')}")
                mauricio_encontrado = True
                break
        
        if not mauricio_encontrado:
            print(f"   ❌ NO se encontró 'Mauricio Camapaña' en Firebase")
        
    except Exception as e:
        print(f"💥 Error: {e}")

if __name__ == "__main__":
    verificar_firebase()
