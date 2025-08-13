from django.apps import AppConfig


class ChatbotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chatbot'

    def ready(self):
        from . import vector_store
        from .document_loader import indexar_pdfs_en_directorio
        from .startup import inicializar_chatbot_startup
        import logging
        
        logger = logging.getLogger(__name__)
        logger.info("🔧 Django apps.py ready() iniciado...")
        
        # Inicializa el vector store (esto carga e indexa todos los documentos, incluidos los PDFs)
        vector_store.inicializar_vector_store()
        
        # Indexa automáticamente los PDFs existentes en /media/docs
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        docs_dir = os.path.join(base_dir, 'media', 'docs')
        indexar_pdfs_en_directorio(docs_dir)
        
        # 🚀 NUEVA FUNCIONALIDAD: Precarga automática del chatbot
        logger.info("🚀 Llamando a inicializar_chatbot_startup()...")
        inicializar_chatbot_startup()
        logger.info("✅ apps.py ready() completado")