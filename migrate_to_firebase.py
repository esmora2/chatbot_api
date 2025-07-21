#!/usr/bin/env python3
"""
Script para migrar datos del CSV a Firebase Firestore
"""
import os
import sys
import django
import csv
from typing import List, Dict

# Configurar Django
sys.path.append('/home/erickxse/visual/asegcbot/chatbot_api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

from chatbot.firebase_service import firebase_service

def load_csv_data(csv_path: str) -> List[Dict]:
    """
    Carga datos del CSV
    """
    data = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Limpiar datos
                if row.get('Pregunta') and row.get('Respuesta'):
                    data.append({
                        'Pregunta': row['Pregunta'].strip(),
                        'Respuesta': row['Respuesta'].strip(),
                        'Categoría': row.get('Categoría', '').strip()
                    })
        
        print(f"✅ CSV cargado: {len(data)} registros válidos")
        return data
        
    except Exception as e:
        print(f"❌ Error cargando CSV: {e}")
        return []

def verify_firebase_connection():
    """
    Verifica la conexión con Firebase
    """
    if firebase_service.is_connected():
        print("✅ Firebase conectado exitosamente")
        return True
    else:
        print("❌ Error: No se pudo conectar a Firebase")
        print("Verifica tu configuración:")
        print("1. FIREBASE_PROJECT_ID en .env")
        print("2. Credenciales de Google Cloud (gcloud auth application-default login)")
        return False

def preview_migration(csv_data: List[Dict], preview_count: int = 5):
    """
    Muestra una vista previa de lo que se va a migrar
    """
    print(f"\n📋 Vista previa de migración ({preview_count} primeros registros):")
    print("-" * 80)
    
    for i, row in enumerate(csv_data[:preview_count]):
        print(f"\n{i+1}. Pregunta: {row['Pregunta'][:60]}...")
        print(f"   Respuesta: {row['Respuesta'][:60]}...")
        print(f"   Categoría: {row['Categoría'] or 'Sin categoría'}")
    
    if len(csv_data) > preview_count:
        print(f"\n... y {len(csv_data) - preview_count} registros más")

def main():
    print("🔥 MIGRACIÓN CSV → FIREBASE FIRESTORE")
    print("=" * 50)
    
    # Verificar conexión Firebase
    if not verify_firebase_connection():
        return
    
    # Cargar datos del CSV
    csv_path = "media/docs/basecsvf.csv"
    if not os.path.exists(csv_path):
        print(f"❌ Error: No se encontró el archivo CSV en {csv_path}")
        return
    
    csv_data = load_csv_data(csv_path)
    if not csv_data:
        print("❌ No hay datos válidos para migrar")
        return
    
    # Vista previa
    preview_migration(csv_data)
    
    # Confirmar migración
    print(f"\n🔄 ¿Migrar {len(csv_data)} registros a Firebase Firestore?")
    print("⚠️  ADVERTENCIA: Esto creará documentos en tu base de datos Firebase")
    
    respuesta = input("Escribe 'SI' para continuar: ").strip().upper()
    
    if respuesta != 'SI':
        print("❌ Migración cancelada")
        return
    
    # Ejecutar migración
    print("\n🚀 Iniciando migración...")
    success, message = firebase_service.migrate_csv_to_firestore(csv_data)
    
    if success:
        print(f"✅ {message}")
        
        # Mostrar estadísticas
        stats = firebase_service.get_stats()
        print(f"\n📊 Estadísticas post-migración:")
        print(f"   Total FAQs activas: {stats.get('total_activas', 0)}")
        print(f"   Total FAQs: {stats.get('total', 0)}")
        
        if stats.get('por_categoria'):
            print(f"   Por categoría:")
            for cat, count in stats['por_categoria'].items():
                print(f"     - {cat}: {count}")
        
        print(f"\n🎉 ¡Migración completada exitosamente!")
        print(f"🔗 Puedes verificar los datos en:")
        print(f"   https://console.firebase.google.com/project/chatbot-dcco/firestore")
        
    else:
        print(f"❌ Error en migración: {message}")

if __name__ == "__main__":
    main()
