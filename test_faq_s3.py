#!/usr/bin/env python
"""
Script para probar el endpoint de FAQ que ahora sincroniza con S3
"""

import requests
import json

def test_faq_management():
    """Prueba el endpoint de gestión de FAQ"""
    
    # URL del endpoint
    url = "http://127.0.0.1:8000/faq/manage/"
    
    # Token de gestión (del .env)
    token = "your-secure-token-here-change-in-production"
    
    # Datos de prueba
    test_data = {
        "pregunta": "¿Cómo se obtiene el certificado de inglés?",
        "respuesta": "El certificado de inglés se obtiene aprobando el examen TOEFL o mediante suficiencia",
        "categoria": "Requisitos",
        "verificar_duplicados": True,
        "forzar": False
    }
    
    # Headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {token}"
    }
    
    print("🧪 PRUEBA DEL ENDPOINT FAQ CON S3")
    print("=" * 50)
    print(f"🔗 URL: {url}")
    print(f"📝 Pregunta: {test_data['pregunta']}")
    print(f"💬 Respuesta: {test_data['respuesta']}")
    print("-" * 50)
    
    try:
        # Hacer la petición POST
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code in [200, 201]:  # 200 OK o 201 Created
            data = response.json()
            print("✅ RESPUESTA EXITOSA:")
            print(f"   📄 Mensaje: {data.get('mensaje', data.get('message', 'No message'))}")
            print(f"   🎯 Éxito: {data.get('success', True)}")
            print(f"   ☁️ Sincronizado con S3: {data.get('synced_to_s3', 'N/A')}")
            
            if 'entrada' in data:
                entrada = data['entrada']
                print(f"   📝 Entrada creada:")
                print(f"      - ID: {entrada.get('id', 'N/A')}")
                print(f"      - Pregunta: {entrada.get('Pregunta', 'N/A')}")
                print(f"      - Respuesta: {entrada.get('Respuesta', 'N/A')}")
                print(f"      - Categoría: {entrada.get('Categoría', 'N/A')}")
                print(f"      - Fecha: {entrada.get('fechaCreacion', entrada.get('Fecha_Agregado', 'N/A'))}")
                
            if 'estadisticas' in data:
                stats = data['estadisticas']
                print(f"   📊 Estadísticas:")
                print(f"      - Total preguntas: {stats.get('total_preguntas', 'N/A')}")
                print(f"      - Última modificación: {stats.get('ultima_modificacion', 'N/A')}")
                
        elif response.status_code == 401:
            print("❌ ERROR DE AUTENTICACIÓN")
            print("   Verifica que el token sea correcto")
            
        elif response.status_code == 400:
            print("❌ ERROR DE DATOS")
            try:
                error_data = response.json()
                print(f"   Detalles: {error_data}")
            except:
                print(f"   Texto: {response.text}")
                
        else:
            print(f"❌ ERROR HTTP {response.status_code}")
            print(f"   Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ ERROR DE CONEXIÓN")
        print("   Asegúrate de que el servidor esté ejecutándose:")
        print("   python manage.py runserver")
        
    except Exception as e:
        print(f"❌ ERROR: {e}")

def verify_s3_sync():
    """Verifica que el archivo se haya sincronizado con S3"""
    print("\n🔍 VERIFICANDO SINCRONIZACIÓN CON S3")
    print("=" * 40)
    
    # URL directa del CSV en CloudFront
    csv_url = "https://d2iqkgcoua86dq.cloudfront.net/media/docs/basecsvf.csv"
    
    try:
        response = requests.get(csv_url, timeout=10)
        if response.status_code == 200:
            print("✅ CSV accesible en CloudFront")
            
            # Contar líneas para ver si se agregó
            lines = response.text.strip().split('\n')
            print(f"📊 Total de líneas en CSV: {len(lines)}")
            
            # Mostrar las últimas 3 líneas
            print("📄 Últimas entradas:")
            for i, line in enumerate(lines[-3:], 1):
                if line.strip():
                    parts = line.split(',')
                    if len(parts) >= 2:
                        print(f"   {i}. {parts[1][:50]}...")
                        
        else:
            print(f"❌ CSV no accesible: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error verificando S3: {e}")

if __name__ == "__main__":
    print("🚀 PRUEBA COMPLETA DEL ENDPOINT FAQ CON S3")
    print("=" * 60)
    
    # Probar endpoint
    test_faq_management()
    
    # Esperar un poco para que se propague en CloudFront
    import time
    print("\n⏳ Esperando 5 segundos para propagación...")
    time.sleep(5)
    
    # Verificar sincronización
    verify_s3_sync()
    
    print("\n🎉 PRUEBA COMPLETADA")
    print("=" * 30)
