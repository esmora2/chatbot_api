#!/usr/bin/env python3
"""
Script simple para probar Firebase
"""
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

print("🔧 Verificando configuración...")
print(f"FIREBASE_PROJECT_ID: {os.getenv('FIREBASE_PROJECT_ID')}")
print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")

creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if creds_path and os.path.exists(creds_path):
    print("✅ Archivo de credenciales encontrado")
    
    try:
        import firebase_admin
        from firebase_admin import credentials, firestore
        
        print("🔥 Intentando conectar con Firebase...")
        
        # Inicializar Firebase
        if not firebase_admin._apps:
            cred = credentials.Certificate(creds_path)
            firebase_admin.initialize_app(cred, {
                'projectId': os.getenv('FIREBASE_PROJECT_ID', 'chatbot-dcco'),
            })
        
        # Obtener cliente de Firestore
        db = firestore.client()
        
        # Probar conexión
        collections = list(db.collections())
        print(f"✅ Conectado exitosamente!")
        print(f"📊 Colecciones encontradas: {[c.id for c in collections]}")
        
    except Exception as e:
        print(f"❌ Error conectando: {e}")
        
else:
    print("❌ Archivo de credenciales no encontrado")
    print(f"Buscando en: {creds_path}")
