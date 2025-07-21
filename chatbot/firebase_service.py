"""
Servicio de Firebase para gestionar FAQ en Firestore
"""
import os
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore
from django.conf import settings

logger = logging.getLogger(__name__)

class FirebaseService:
    """
    Servicio para gestionar el contenido FAQ en Firebase Firestore
    """
    
    def __init__(self):
        self.db = None
        self.collection_name = 'faqs'
        self._initialize_firebase()
    
    def _initialize_firebase(self):
        """
        Inicializa la conexión con Firebase
        """
        try:
            # Verificar si Firebase ya está inicializado
            if not firebase_admin._apps:
                project_id = getattr(settings, 'FIREBASE_PROJECT_ID', 'chatbot-dcco')
                
                # Configurar credenciales
                # En desarrollo, usar credenciales por defecto (requiere gcloud auth)
                # En producción, usar archivo de credenciales
                cred_path = getattr(settings, 'GOOGLE_APPLICATION_CREDENTIALS', None)
                
                if cred_path and os.path.exists(cred_path):
                    # Usar archivo de credenciales
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred, {
                        'projectId': project_id,
                    })
                else:
                    # Usar credenciales por defecto (para desarrollo local)
                    firebase_admin.initialize_app(options={
                        'projectId': project_id,
                    })
                
                logger.info(f"Firebase inicializado para proyecto: {project_id}")
            
            # Obtener cliente de Firestore
            self.db = firestore.client()
            logger.info("Cliente de Firestore conectado exitosamente")
            
        except Exception as e:
            logger.error(f"Error inicializando Firebase: {e}")
            self.db = None
    
    def is_connected(self) -> bool:
        """
        Verifica si Firebase está conectado
        """
        return self.db is not None
    
    def migrate_csv_to_firestore(self, csv_data: List[Dict]) -> Tuple[bool, str]:
        """
        Migra datos del CSV a Firestore
        
        Args:
            csv_data: Lista de diccionarios con datos del CSV
            
        Returns:
            Tuple (success, message)
        """
        if not self.is_connected():
            return False, "Firebase no está conectado"
        
        try:
            batch = self.db.batch()
            migrated_count = 0
            
            for index, row in enumerate(csv_data):
                if not row.get('Pregunta') or not row.get('Respuesta'):
                    continue
                
                # Crear documento con ID único
                doc_id = f"faq_{index + 1:03d}"
                doc_ref = self.db.collection(self.collection_name).document(doc_id)
                
                # Preparar datos
                faq_data = {
                    'id': index + 1,
                    'pregunta': row['Pregunta'].strip(),
                    'respuesta': row['Respuesta'].strip(),
                    'categoria': row.get('Categoría', '').strip(),
                    'fecha_creacion': datetime.now(),
                    'fecha_modificacion': None,
                    'activo': True,
                    'fuente': 'csv_migration',
                    'metadata': {
                        'palabras_clave': self._extract_keywords(row['Pregunta']),
                        'longitud_respuesta': len(row['Respuesta']),
                        'migrado_desde_csv': True
                    }
                }
                
                batch.set(doc_ref, faq_data)
                migrated_count += 1
                
                # Ejecutar batch cada 500 documentos (límite de Firestore)
                if migrated_count % 500 == 0:
                    batch.commit()
                    batch = self.db.batch()
                    logger.info(f"Migrados {migrated_count} documentos...")
            
            # Ejecutar el último batch
            if migrated_count % 500 != 0:
                batch.commit()
            
            logger.info(f"Migración completada: {migrated_count} documentos")
            return True, f"Migrados exitosamente {migrated_count} documentos"
            
        except Exception as e:
            logger.error(f"Error en migración: {e}")
            return False, f"Error durante la migración: {str(e)}"
    
    def get_all_faqs(self) -> List[Dict]:
        """
        Obtiene todas las FAQs de Firestore
        """
        if not self.is_connected():
            return []
        
        try:
            docs = self.db.collection(self.collection_name).where('activo', '==', True).stream()
            faqs = []
            
            for doc in docs:
                data = doc.to_dict()
                data['document_id'] = doc.id
                faqs.append(data)
            
            logger.info(f"Obtenidas {len(faqs)} FAQs de Firestore")
            return faqs
            
        except Exception as e:
            logger.error(f"Error obteniendo FAQs: {e}")
            return []
    
    def search_faqs(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Busca FAQs por texto (búsqueda simple)
        """
        if not self.is_connected():
            return []
        
        try:
            # Búsqueda simple por palabras clave
            query_lower = query.lower()
            docs = self.db.collection(self.collection_name).where('activo', '==', True).limit(limit * 3).stream()
            
            matching_faqs = []
            for doc in docs:
                data = doc.to_dict()
                pregunta = data.get('pregunta', '').lower()
                respuesta = data.get('respuesta', '').lower()
                
                # Búsqueda simple por contención de texto
                if query_lower in pregunta or query_lower in respuesta:
                    data['document_id'] = doc.id
                    matching_faqs.append(data)
                    
                    if len(matching_faqs) >= limit:
                        break
            
            return matching_faqs
            
        except Exception as e:
            logger.error(f"Error buscando FAQs: {e}")
            return []
    
    def add_faq(self, pregunta: str, respuesta: str, categoria: str = "") -> Tuple[bool, str]:
        """
        Agrega una nueva FAQ a Firestore
        """
        if not self.is_connected():
            return False, "Firebase no está conectado"
        
        try:
            # Generar ID único
            doc_ref = self.db.collection(self.collection_name).document()
            
            faq_data = {
                'pregunta': pregunta.strip(),
                'respuesta': respuesta.strip(),
                'categoria': categoria.strip(),
                'fecha_creacion': datetime.now(),
                'fecha_modificacion': None,
                'activo': True,
                'fuente': 'api_add',
                'metadata': {
                    'palabras_clave': self._extract_keywords(pregunta),
                    'longitud_respuesta': len(respuesta)
                }
            }
            
            doc_ref.set(faq_data)
            logger.info(f"FAQ agregada con ID: {doc_ref.id}")
            return True, f"FAQ agregada exitosamente con ID: {doc_ref.id}"
            
        except Exception as e:
            logger.error(f"Error agregando FAQ: {e}")
            return False, f"Error agregando FAQ: {str(e)}"
    
    def update_faq(self, document_id: str, pregunta: str = None, respuesta: str = None, categoria: str = None) -> Tuple[bool, str]:
        """
        Actualiza una FAQ existente
        """
        if not self.is_connected():
            return False, "Firebase no está conectado"
        
        try:
            doc_ref = self.db.collection(self.collection_name).document(document_id)
            
            # Verificar que el documento existe
            doc = doc_ref.get()
            if not doc.exists:
                return False, f"FAQ con ID {document_id} no encontrada"
            
            # Preparar datos de actualización
            update_data = {
                'fecha_modificacion': datetime.now()
            }
            
            if pregunta is not None:
                update_data['pregunta'] = pregunta.strip()
                update_data['metadata.palabras_clave'] = self._extract_keywords(pregunta)
            
            if respuesta is not None:
                update_data['respuesta'] = respuesta.strip()
                update_data['metadata.longitud_respuesta'] = len(respuesta)
            
            if categoria is not None:
                update_data['categoria'] = categoria.strip()
            
            doc_ref.update(update_data)
            logger.info(f"FAQ actualizada: {document_id}")
            return True, f"FAQ {document_id} actualizada exitosamente"
            
        except Exception as e:
            logger.error(f"Error actualizando FAQ: {e}")
            return False, f"Error actualizando FAQ: {str(e)}"
    
    def delete_faq(self, document_id: str) -> Tuple[bool, str]:
        """
        Elimina (desactiva) una FAQ
        """
        if not self.is_connected():
            return False, "Firebase no está conectado"
        
        try:
            doc_ref = self.db.collection(self.collection_name).document(document_id)
            
            # Verificar que el documento existe
            doc = doc_ref.get()
            if not doc.exists:
                return False, f"FAQ con ID {document_id} no encontrada"
            
            # Marcar como inactiva en lugar de eliminar
            doc_ref.update({
                'activo': False,
                'fecha_modificacion': datetime.now()
            })
            
            logger.info(f"FAQ desactivada: {document_id}")
            return True, f"FAQ {document_id} eliminada exitosamente"
            
        except Exception as e:
            logger.error(f"Error eliminando FAQ: {e}")
            return False, f"Error eliminando FAQ: {str(e)}"
    
    def get_stats(self) -> Dict:
        """
        Obtiene estadísticas de las FAQs
        """
        if not self.is_connected():
            return {}
        
        try:
            # Total de FAQs activas
            active_count = len(list(self.db.collection(self.collection_name).where('activo', '==', True).stream()))
            
            # Total de FAQs inactivas
            inactive_count = len(list(self.db.collection(self.collection_name).where('activo', '==', False).stream()))
            
            # FAQs por categoría
            docs = self.db.collection(self.collection_name).where('activo', '==', True).stream()
            categories = {}
            for doc in docs:
                data = doc.to_dict()
                cat = data.get('categoria', 'Sin categoría')
                categories[cat] = categories.get(cat, 0) + 1
            
            return {
                'total_activas': active_count,
                'total_inactivas': inactive_count,
                'total': active_count + inactive_count,
                'por_categoria': categories,
                'firebase_conectado': True
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {e}")
            return {'error': str(e), 'firebase_conectado': False}
    
    def _extract_keywords(self, text: str) -> List[str]:
        """
        Extrae palabras clave básicas de un texto
        """
        import re
        
        # Limpiar texto y convertir a minúsculas
        text = re.sub(r'[^\w\s]', ' ', text.lower())
        words = text.split()
        
        # Filtrar palabras muy cortas y comunes
        stop_words = {'de', 'la', 'el', 'en', 'y', 'a', 'que', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'una', 'ser', 'al', 'como', 'más', 'fue', 'del', 'ha', 'muy', 'ya', 'todo', 'está', 'le', 'pero', 'ese', 'algo', 'qué', 'cómo', 'dónde', 'cuándo', 'quién'}
        
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        
        # Retornar primeras 10 palabras clave únicas
        return list(dict.fromkeys(keywords))[:10]


# Instancia global del servicio
firebase_service = FirebaseService()
