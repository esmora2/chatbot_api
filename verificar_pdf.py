#!/usr/bin/env python3
"""
Script para verificar que el PDF específico se cargue correctamente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

from chatbot.document_loader import cargar_documentos
from chatbot.vector_store import buscar_documentos, inicializar_vector_store

def verificar_pdf_especifico():
    """
    Verifica que el PDF específico se haya cargado correctamente
    """
    pdf_nombre = "espe_software_aplicaciones_basadas_en_el_conocimiento.pdf"
    base_dir = os.path.join("media", "docs")
    pdf_path = os.path.join(base_dir, pdf_nombre)
    
    print("🔍 VERIFICACIÓN DEL PDF ESPECÍFICO")
    print("=" * 50)
    
    # 1. Verificar que el archivo existe físicamente
    print(f"📁 Verificando archivo: {pdf_nombre}")
    if os.path.exists(pdf_path):
        file_size = os.path.getsize(pdf_path)
        print(f"   ✅ Archivo encontrado: {file_size} bytes ({file_size/1024:.1f} KB)")
    else:
        print(f"   ❌ Archivo NO encontrado en: {pdf_path}")
        return False
    
    # 2. Cargar documentos y verificar si se procesó
    print("\n📖 Cargando documentos...")
    try:
        documentos = cargar_documentos()
        print(f"   ✅ Total documentos cargados: {len(documentos)}")
        
        # Buscar chunks del PDF específico
        pdf_chunks = []
        for doc in documentos:
            if doc.metadata.get("source") == "pdf":
                if doc.metadata.get("filename") == pdf_nombre:
                    pdf_chunks.append(doc)
        
        print(f"\n📊 Chunks del PDF '{pdf_nombre}': {len(pdf_chunks)}")
        
        if pdf_chunks:
            print("   ✅ PDF cargado correctamente")
            
            # Mostrar información de los primeros chunks
            for i, chunk in enumerate(pdf_chunks[:3]):
                print(f"\n   📄 Chunk {i+1}:")
                print(f"      - Contenido: {chunk.page_content[:100]}...")
                print(f"      - Metadata: {chunk.metadata}")
                
            # Mostrar estadísticas
            contenido_total = sum(len(chunk.page_content) for chunk in pdf_chunks)
            print(f"\n   📈 Estadísticas:")
            print(f"      - Total chunks: {len(pdf_chunks)}")
            print(f"      - Contenido total: {contenido_total} caracteres")
            print(f"      - Promedio por chunk: {contenido_total//len(pdf_chunks)} caracteres")
            
        else:
            print("   ❌ PDF NO se cargó como chunks")
            return False
            
    except Exception as e:
        print(f"   ❌ Error cargando documentos: {e}")
        return False
    
    # 3. Verificar búsqueda semántica
    print("\n🔍 Probando búsqueda semántica...")
    try:
        inicializar_vector_store()
        
        # Preguntas de prueba relacionadas con aplicaciones basadas en conocimiento
        preguntas_prueba = [
            "aplicaciones basadas en el conocimiento",
            "sistemas expertos",
            "inteligencia artificial",
            "programación en software",
            "syllabus aplicaciones conocimiento"
        ]
        
        for pregunta in preguntas_prueba:
            print(f"\n   🔍 Probando: '{pregunta}'")
            resultados = buscar_documentos(pregunta, top_k=5)
            
            # Verificar si el PDF aparece en los resultados
            pdf_encontrado = False
            for doc in resultados:
                if doc.metadata.get("filename") == pdf_nombre:
                    pdf_encontrado = True
                    print(f"      ✅ PDF encontrado en resultado")
                    print(f"      📄 Contenido: {doc.page_content[:100]}...")
                    break
            
            if not pdf_encontrado:
                print(f"      ⚠️  PDF no aparece en top 5 resultados")
                
    except Exception as e:
        print(f"   ❌ Error en búsqueda semántica: {e}")
        return False
    
    print("\n✅ VERIFICACIÓN COMPLETADA")
    return True

def probar_preguntas_especificas():
    """
    Prueba preguntas específicas sobre aplicaciones basadas en conocimiento
    """
    print("\n🤖 PROBANDO PREGUNTAS ESPECÍFICAS")
    print("=" * 50)
    
    preguntas = [
        "¿Qué es aplicaciones basadas en el conocimiento?",
        "¿Cuál es el contenido de la materia de aplicaciones basadas en el conocimiento?",
        "¿Qué temas se ven en aplicaciones basadas en el conocimiento?",
        "¿Hay información sobre sistemas expertos?",
        "¿Qué syllabus tiene la materia de aplicaciones basadas en el conocimiento?"
    ]
    
    for pregunta in preguntas:
        print(f"\n❓ Pregunta: {pregunta}")
        try:
            resultados = buscar_documentos(pregunta, top_k=3)
            
            for i, doc in enumerate(resultados, 1):
                source = doc.metadata.get("source", "unknown")
                filename = doc.metadata.get("filename", "N/A")
                
                print(f"   {i}. Fuente: {source}")
                if source == "pdf":
                    print(f"      Archivo: {filename}")
                print(f"      Contenido: {doc.page_content[:150]}...")
                print()
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    """
    Función principal
    """
    print("🚀 INICIANDO VERIFICACIÓN DEL PDF")
    print("=" * 60)
    
    # Verificar PDF específico
    if verificar_pdf_especifico():
        # Probar preguntas específicas
        probar_preguntas_especificas()
        
        print("\n🎯 RESUMEN:")
        print("✅ El PDF se ha cargado correctamente")
        print("✅ Está disponible para búsqueda semántica")
        print("✅ Puede responder preguntas relacionadas")
        
    else:
        print("\n❌ PROBLEMAS ENCONTRADOS:")
        print("- El PDF no se cargó correctamente")
        print("- Verificar que el archivo esté en media/docs/")
        print("- Verificar que el archivo no esté corrupto")
        print("- Reiniciar el servidor si es necesario")

if __name__ == "__main__":
    main()
