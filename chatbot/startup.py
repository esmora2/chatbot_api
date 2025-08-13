"""
Módulo de inicialización automática para el chatbot.
Se ejecuta al arrancar Django para precargar índices y optimizar el rendimiento.
"""
import logging
import threading
from django.conf import settings

logger = logging.getLogger(__name__)

def inicializar_chatbot_startup():
    """
    Inicializa automáticamente todos los componentes del chatbot al arrancar Django.
    Se ejecuta en un hilo separado para no bloquear el arranque del servidor.
    """
    # Verificar si la precarga está habilitada
    if not getattr(settings, 'CHATBOT_PRELOAD_ON_STARTUP', True):
        logger.info("⏹️ Precarga automática deshabilitada en configuración")
        return
    
    def inicializar_en_background():
        try:
            logger.info("🚀 Iniciando precarga automática del chatbot...")
            
            # 1. Precargar Firebase embeddings
            from .firebase_embeddings import firebase_embeddings
            firebase_embeddings.inicializar_automaticamente()
            
            # 2. Precargar vector store principal (opcional)
            try:
                from .vector_store import inicializar_vector_store
                inicializar_vector_store()
                logger.info("✅ Vector store principal precargado")
            except Exception as e:
                logger.info(f"Vector store principal se cargará bajo demanda: {e}")
            
            logger.info("🎉 Precarga automática del chatbot completada exitosamente")
            
        except Exception as e:
            logger.error(f"❌ Error en precarga automática del chatbot: {e}")
            logger.info("El chatbot funcionará normalmente con carga bajo demanda")
    
    # Ejecutar en background para no bloquear Django
    thread = threading.Thread(target=inicializar_en_background, daemon=True)
    thread.start()
    logger.info("🔧 Precarga automática del chatbot iniciada en background...")

def inicializar_solo_firebase():
    """
    Versión más ligera que solo inicializa Firebase embeddings.
    Usar si hay problemas de memoria o tiempo de arranque.
    """
    def inicializar_firebase_bg():
        try:
            from .firebase_embeddings import firebase_embeddings
            firebase_embeddings.inicializar_automaticamente()
        except Exception as e:
            logger.error(f"Error inicializando Firebase embeddings: {e}")
    
    thread = threading.Thread(target=inicializar_firebase_bg, daemon=True)
    thread.start()
