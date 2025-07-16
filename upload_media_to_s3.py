#!/usr/bin/env python
"""
Script para subir documentos locales a S3 y mantener la estructura.
Uso: python upload_media_to_s3.py
"""

import os
import boto3
from pathlib import Path
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Cargar variables de entorno
load_dotenv()

# Configuración S3
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'us-east-1')

# Directorio local de documentos
MEDIA_DOCS_DIR = Path(__file__).parent / 'media' / 'docs'
S3_PREFIX = 'media/docs/'

def upload_to_s3():
    """Sube todos los documentos de media/docs a S3"""
    
    # Crear cliente S3
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_S3_REGION_NAME
    )
    
    # Verificar que el directorio existe
    if not MEDIA_DOCS_DIR.exists():
        print(f"❌ El directorio {MEDIA_DOCS_DIR} no existe")
        return
    
    print(f"📂 Subiendo archivos desde: {MEDIA_DOCS_DIR}")
    print(f"🪣 Bucket S3: {AWS_STORAGE_BUCKET_NAME}")
    print(f"📁 Prefijo S3: {S3_PREFIX}")
    print("-" * 50)
    
    uploaded_files = []
    failed_files = []
    
    # Recorrer todos los archivos en media/docs
    for file_path in MEDIA_DOCS_DIR.rglob('*'):
        if file_path.is_file():
            # Obtener la ruta relativa
            relative_path = file_path.relative_to(MEDIA_DOCS_DIR)
            s3_key = f"{S3_PREFIX}{relative_path}"
            
            try:
                # Subir archivo (sin ACL ya que el bucket no lo permite)
                s3_client.upload_file(
                    str(file_path),
                    AWS_STORAGE_BUCKET_NAME,
                    s3_key
                )
                
                print(f"✅ Subido: {relative_path}")
                uploaded_files.append(str(relative_path))
                
            except ClientError as e:
                print(f"❌ Error subiendo {relative_path}: {e}")
                failed_files.append(str(relative_path))
    
    # Resumen
    print("-" * 50)
    print(f"📊 RESUMEN:")
    print(f"   ✅ Archivos subidos: {len(uploaded_files)}")
    print(f"   ❌ Archivos fallidos: {len(failed_files)}")
    
    if uploaded_files:
        print(f"\n📁 Archivos subidos exitosamente:")
        for file in uploaded_files:
            print(f"   - {file}")
    
    if failed_files:
        print(f"\n❌ Archivos que fallaron:")
        for file in failed_files:
            print(f"   - {file}")
    
    print(f"\n🌐 Los archivos están disponibles en:")
    print(f"   https://{os.getenv('AWS_S3_CUSTOM_DOMAIN')}/media/docs/")

def list_s3_files():
    """Lista los archivos que ya están en S3"""
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_S3_REGION_NAME
    )
    
    try:
        response = s3_client.list_objects_v2(
            Bucket=AWS_STORAGE_BUCKET_NAME,
            Prefix=S3_PREFIX
        )
        
        if 'Contents' in response:
            print(f"📂 Archivos en S3 (bucket: {AWS_STORAGE_BUCKET_NAME}):")
            for obj in response['Contents']:
                file_path = obj['Key'].replace(S3_PREFIX, '')
                file_size = obj['Size']
                modified = obj['LastModified'].strftime('%Y-%m-%d %H:%M:%S')
                print(f"   - {file_path} ({file_size} bytes) - {modified}")
        else:
            print("📂 No se encontraron archivos en S3")
            
    except ClientError as e:
        print(f"❌ Error listando archivos en S3: {e}")

if __name__ == "__main__":
    print("🚀 SCRIPT DE MIGRACIÓN A S3")
    print("=" * 50)
    
    # Verificar credenciales
    if not all([AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_STORAGE_BUCKET_NAME]):
        print("❌ Faltan credenciales de AWS en el archivo .env")
        exit(1)
    
    # Mostrar archivos actuales en S3
    print("\n1️⃣ ARCHIVOS ACTUALES EN S3:")
    list_s3_files()
    
    # Preguntar si continuar
    print("\n2️⃣ SUBIR ARCHIVOS LOCALES:")
    respuesta = input("¿Deseas subir los archivos locales a S3? (s/n): ").lower()
    
    if respuesta in ['s', 'sí', 'si', 'y', 'yes']:
        upload_to_s3()
    else:
        print("❌ Operación cancelada")
