#!/usr/bin/env python3
"""
Script para verificar datos existentes en Firebase
"""
import os
from dotenv import load_dotenv

load_dotenv()

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    # Inicializar Firebase si no está inicializado
    if not firebase_admin._apps:
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        cred = credentials.Certificate(creds_path)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    print("🔍 Verificando datos existentes en Firebase...")
    
    # Obtener todas las FAQs
    faqs_ref = db.collection('faqs')
    docs = faqs_ref.stream()
    
    faqs_count = 0
    sample_faqs = []
    
    for doc in docs:
        faqs_count += 1
        if faqs_count <= 3:  # Mostrar solo las primeras 3 como ejemplo
            data = doc.to_dict()
            sample_faqs.append({
                'id': doc.id,
                'pregunta': data.get('pregunta', '')[:100] + '...' if len(data.get('pregunta', '')) > 100 else data.get('pregunta', ''),
                'respuesta': data.get('respuesta', '')[:100] + '...' if len(data.get('respuesta', '')) > 100 else data.get('respuesta', '')
            })
    
    print(f"📊 Total de FAQs en Firebase: {faqs_count}")
    
    if sample_faqs:
        print("\n📝 Muestra de FAQs existentes:")
        for i, faq in enumerate(sample_faqs, 1):
            print(f"\n{i}. ID: {faq['id']}")
            print(f"   Pregunta: {faq['pregunta']}")
            print(f"   Respuesta: {faq['respuesta']}")
    
    # Verificar datos en CSV local
    import pandas as pd
    try:
        csv_path = 'media/docs/basecsvf.csv'
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            print(f"\n📄 FAQs en CSV local: {len(df)}")
            
            if faqs_count == len(df):
                print("✅ Los datos parecen estar sincronizados (mismo número de registros)")
            elif faqs_count > len(df):
                print("⚠️  Firebase tiene MÁS datos que el CSV local")
            else:
                print("⚠️  Firebase tiene MENOS datos que el CSV local")
        else:
            print(f"❌ Archivo CSV no encontrado: {csv_path}")
    except Exception as e:
        print(f"❌ Error leyendo CSV: {e}")
    
except Exception as e:
    print(f"❌ Error conectando a Firebase: {e}")
