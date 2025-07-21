#!/usr/bin/env python3
"""
Script para sincronizar FAQs faltantes entre CSV y Firebase
"""
import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

try:
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    # Inicializar Firebase
    if not firebase_admin._apps:
        creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        cred = credentials.Certificate(creds_path)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    print("🔍 Comparando datos CSV vs Firebase...")
    
    # Leer CSV local
    csv_path = 'media/docs/basecsvf.csv'
    df = pd.read_csv(csv_path)
    print(f"📄 FAQs en CSV: {len(df)}")
    
    # Obtener FAQs de Firebase
    faqs_ref = db.collection('faqs')
    firebase_docs = {doc.id: doc.to_dict() for doc in faqs_ref.stream()}
    print(f"🔥 FAQs en Firebase: {len(firebase_docs)}")
    
    # Encontrar FAQs faltantes
    missing_faqs = []
    
    for index, row in df.iterrows():
        faq_id = f"faq_{index + 1:03d}"  # faq_001, faq_002, etc.
        
        if faq_id not in firebase_docs:
            missing_faqs.append({
                'id': faq_id,
                'pregunta': str(row['Pregunta']).strip(),
                'respuesta': str(row['Respuesta']).strip(),
                'categoria': str(row.get('Categoria', 'general')).strip() if 'Categoria' in row else 'general'
            })
    
    if missing_faqs:
        print(f"\n📋 Se encontraron {len(missing_faqs)} FAQs faltantes:")
        for faq in missing_faqs:
            print(f"- {faq['id']}: {faq['pregunta'][:50]}...")
        
        response = input(f"\n¿Migrar estas {len(missing_faqs)} FAQs faltantes? (s/n): ")
        
        if response.lower() in ['s', 'si', 'sí', 'y', 'yes']:
            print("🚀 Migrando FAQs faltantes...")
            
            batch = db.batch()
            for faq in missing_faqs:
                doc_ref = faqs_ref.document(faq['id'])
                batch.set(doc_ref, {
                    'pregunta': faq['pregunta'],
                    'respuesta': faq['respuesta'],
                    'categoria': faq['categoria'],
                    'migrated_at': firestore.SERVER_TIMESTAMP
                })
            
            batch.commit()
            print(f"✅ {len(missing_faqs)} FAQs migradas exitosamente!")
            
            # Verificar resultado final
            final_count = len(list(faqs_ref.stream()))
            print(f"📊 Total final en Firebase: {final_count}")
        else:
            print("❌ Migración cancelada")
    else:
        print("✅ Todos los datos están sincronizados!")
        
        # Verificar si hay FAQs extra en Firebase
        if len(firebase_docs) > len(df):
            print(f"⚠️  Firebase tiene {len(firebase_docs) - len(df)} FAQs adicionales que no están en el CSV")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
