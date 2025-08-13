#!/usr/bin/env python3
"""
Script para agregar la pregunta sobre DCCO directamente a Firebase
"""
import os
import sys
import django

sys.path.append('/home/erickxse/visual/asegcbot/chatbot_api')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')
django.setup()

def agregar_pregunta_dcco_firebase():
    print("📝 AGREGANDO PREGUNTA '¿Qué es el DCCO?' A FIREBASE")
    print("=" * 60)
    
    try:
        from chatbot.firebase_service import FirebaseService
        firebase_service = FirebaseService()
        
        # Datos de la nueva FAQ
        nueva_faq = {
            'pregunta': '¿Qué es el DCCO?',
            'respuesta': 'El DCCO es el Departamento de Ciencias de la Computación de la Universidad ESPE. Es una unidad académica que se encarga de la formación de profesionales en el área de informática y tecnología. El DCCO ofrece carreras como Ingeniería en Software, Tecnologías de la Información, Sistemas de Información y Ciencias de la Computación. Además, imparte materias relacionadas con programación, algoritmos, base de datos, inteligencia artificial y sistemas distribuidos.',
            'categoria': 'Información Institucional',
            'tags': ['dcco', 'departamento', 'ciencias', 'computacion', 'carreras', 'universidad', 'espe'],
            'fecha_creacion': firebase_service.db.SERVER_TIMESTAMP,
            'activa': True
        }
        
        # Agregar a Firebase
        doc_ref = firebase_service.db.collection('faqs').add(nueva_faq)
        doc_id = doc_ref[1].id
        
        print(f"✅ FAQ agregada a Firebase con ID: {doc_id}")
        print(f"📝 Pregunta: {nueva_faq['pregunta']}")
        print(f"💬 Respuesta: {nueva_faq['respuesta'][:100]}...")
        print()
        
        # Generar embeddings automáticamente
        print("🤖 Generando embeddings para la nueva FAQ...")
        from chatbot.firebase_embeddings import firebase_embeddings
        
        # Generar embeddings
        embedding_pregunta = firebase_embeddings.generar_embedding(nueva_faq['pregunta'])
        embedding_respuesta = firebase_embeddings.generar_embedding(nueva_faq['respuesta'])
        embedding_combinado = firebase_embeddings.generar_embedding(f"{nueva_faq['pregunta']} {nueva_faq['respuesta']}")
        
        # Actualizar documento con embeddings
        doc_ref[1].update({
            'embedding_pregunta': embedding_pregunta,
            'embedding_respuesta': embedding_respuesta,
            'embedding_combinado': embedding_combinado,
            'fecha_embedding': firebase_service.db.SERVER_TIMESTAMP
        })
        
        print("✅ Embeddings generados y guardados")
        print()
        
        # Recargar el índice vectorial
        print("🔄 Recargando índice vectorial...")
        firebase_embeddings._initialized = False  # Forzar recarga
        exito = firebase_embeddings.cargar_indice_vectorial()
        
        if exito:
            print("✅ Índice vectorial recargado exitosamente")
        else:
            print("⚠️ Error recargando índice vectorial")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    agregar_pregunta_dcco_firebase()
