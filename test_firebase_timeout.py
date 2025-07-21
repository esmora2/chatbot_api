#!/usr/bin/env python3
"""
Script para probar Firebase con timeout
"""
import os
import signal
from dotenv import load_dotenv

# Timeout handler
def timeout_handler(signum, frame):
    raise TimeoutError("Firebase connection timed out")

# Cargar variables de entorno
load_dotenv()

print("🔧 Verificando conectividad a internet...")

try:
    # Probar conectividad básica
    import requests
    response = requests.get("https://google.com", timeout=5)
    print("✅ Conectividad a internet OK")
except Exception as e:
    print(f"❌ Sin conectividad: {e}")
    exit(1)

print("🔥 Probando Firebase con timeout...")

try:
    # Configurar timeout de 10 segundos
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(10)
    
    import firebase_admin
    from firebase_admin import credentials, firestore
    
    creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    if not firebase_admin._apps:
        cred = credentials.Certificate(creds_path)
        firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    
    # Cancelar timeout si llegamos aquí
    signal.alarm(0)
    
    print("✅ Firebase conectado exitosamente!")
    
    # Probar una operación simple
    collections = list(db.collections())
    print(f"📊 Colecciones: {[c.id for c in collections]}")
    
except TimeoutError:
    print("❌ Timeout: Firebase no responde en 10 segundos")
    print("Esto puede indicar problemas de firewall o credenciales")
except Exception as e:
    signal.alarm(0)  # Cancelar timeout
    print(f"❌ Error: {e}")
    print(f"Tipo de error: {type(e).__name__}")
