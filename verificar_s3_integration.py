#!/usr/bin/env python
"""
Script para verificar que document_loader funcione correctamente con S3.
Este script verifica la carga de documentos desde S3 y la funcionalidad del chatbot.
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append('/home/erickxse/visual/asegcbot/chatbot_api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

from dotenv import load_dotenv
import boto3
from chatbot.document_loader import cargar_documentos
from chatbot.vector_store import buscar_documentos, inicializar_vector_store

# Cargar variables de entorno
load_dotenv()

def verificar_conexion_s3():
    """Verifica la conexión a S3 y lista los archivos"""
    print("🔍 VERIFICANDO CONEXIÓN A S3...")
    
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_S3_REGION_NAME', 'us-east-1')
        )
        
        response = s3_client.list_objects_v2(
            Bucket=os.getenv('AWS_STORAGE_BUCKET_NAME'),
            Prefix='media/docs/'
        )
        
        if 'Contents' in response:
            print(f"✅ Conexión exitosa a S3")
            print(f"📂 Archivos encontrados en S3:")
            for obj in response['Contents']:
                file_path = obj['Key'].replace('media/docs/', '')
                if file_path:  # Ignorar carpetas vacías
                    file_size = obj['Size']
                    print(f"   - {file_path} ({file_size} bytes)")
            return True
        else:
            print("❌ No se encontraron archivos en S3")
            return False
            
    except Exception as e:
        print(f"❌ Error conectando a S3: {e}")
        return False

def verificar_urls_s3():
    """Verifica las URLs de los archivos en S3"""
    print("\n🌐 VERIFICANDO URLs DE S3...")
    
    aws_domain = os.getenv('AWS_S3_CUSTOM_DOMAIN')
    base_url = f"https://{aws_domain}/media/docs/"
    
    archivos_test = [
        'espe_software_aplicaciones_distribuidas.pdf',
        'espe_software_aplicaciones_basadas_en_el_conocimiento.pdf',
        'basecsvf.csv'
    ]
    
    for archivo in archivos_test:
        url = f"{base_url}{archivo}"
        print(f"📄 {archivo}:")
        print(f"   URL: {url}")
        
        # Verificar con requests (opcional)
        try:
            import requests
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                print(f"   ✅ Accesible (Status: {response.status_code})")
            else:
                print(f"   ❌ No accesible (Status: {response.status_code})")
        except Exception as e:
            print(f"   ⚠️ Error verificando: {e}")

def verificar_document_loader():
    """Verifica que el document_loader funcione con S3"""
    print("\n📚 VERIFICANDO DOCUMENT LOADER...")
    
    try:
        # Intentar cargar documentos
        print("🔄 Cargando documentos...")
        documents = cargar_documentos()
        
        print(f"✅ Documentos cargados: {len(documents)}")
        
        # Mostrar algunos ejemplos
        for i, doc in enumerate(documents[:3]):
            print(f"\n📄 Documento {i+1}:")
            print(f"   Fuente: {doc.metadata.get('source', 'No especificada')}")
            print(f"   Contenido (primeros 200 caracteres): {doc.page_content[:200]}...")
            
        return True
        
    except Exception as e:
        print(f"❌ Error cargando documentos: {e}")
        return False

def verificar_vector_store():
    """Verifica que el vector store funcione correctamente"""
    print("\n🔍 VERIFICANDO VECTOR STORE...")
    
    try:
        # Inicializar vector store
        inicializar_vector_store()
        
        # Hacer una búsqueda de prueba
        query = "¿Qué es una aplicación distribuida?"
        print(f"🔍 Buscando: '{query}'")
        
        results = buscar_documentos(query, top_k=3)
        
        print(f"✅ Resultados encontrados: {len(results)}")
        
        for i, result in enumerate(results):
            print(f"\n📄 Resultado {i+1}:")
            print(f"   Fuente: {result.metadata.get('source', 'No especificada')}")
            print(f"   Contenido: {result.page_content[:150]}...")
            
        return True
        
    except Exception as e:
        print(f"❌ Error con vector store: {e}")
        return False

def main():
    """Función principal de verificación"""
    print("🚀 VERIFICACIÓN COMPLETA DEL SISTEMA S3")
    print("=" * 60)
    
    # Verificar configuración
    print("⚙️ CONFIGURACIÓN:")
    print(f"   AWS_STORAGE_BUCKET_NAME: {os.getenv('AWS_STORAGE_BUCKET_NAME')}")
    print(f"   AWS_S3_CUSTOM_DOMAIN: {os.getenv('AWS_S3_CUSTOM_DOMAIN')}")
    print(f"   AWS_S3_REGION_NAME: {os.getenv('AWS_S3_REGION_NAME')}")
    
    # Ejecutar verificaciones
    resultados = []
    
    resultados.append(("Conexión S3", verificar_conexion_s3()))
    verificar_urls_s3()
    resultados.append(("Document Loader", verificar_document_loader()))
    resultados.append(("Vector Store", verificar_vector_store()))
    
    # Resumen final
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE VERIFICACIÓN:")
    
    for nombre, exitoso in resultados:
        status = "✅" if exitoso else "❌"
        print(f"   {status} {nombre}")
    
    todas_exitosas = all(resultado[1] for resultado in resultados)
    
    if todas_exitosas:
        print("\n🎉 ¡TODAS LAS VERIFICACIONES EXITOSAS!")
        print("   Tu sistema está listo para usar S3 con CloudFront")
    else:
        print("\n⚠️ ALGUNAS VERIFICACIONES FALLARON")
        print("   Revisa los errores anteriores")

if __name__ == "__main__":
    main()
