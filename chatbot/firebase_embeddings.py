import numpy as np
from sentence_transformers import SentenceTransformer
import firebase_admin
from firebase_admin import firestore
from django.conf import settings
import logging
import json
from typing import List, Dict, Tuple
import faiss

logger = logging.getLogger(__name__)

class FirebaseEmbeddingsService:
    """
    Servicio para manejar embeddings y búsqueda vectorial en Firebase
    """
    
    def __init__(self):
        self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Inicializar Firebase si no está inicializado
        try:
            self.db = firestore.client()
        except ValueError:
            # Firebase no está inicializado, usar el servicio existente
            from .firebase_service import FirebaseService
            firebase_service = FirebaseService()
            self.db = firebase_service.db
        
        self.dimension = 384  # Dimensión del modelo all-MiniLM-L6-v2
        self.index = None
        self.documents = []
        
    def generar_embedding(self, texto: str) -> List[float]:
        """
        Genera embedding para un texto
        """
        try:
            embedding = self.model.encode(texto)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generando embedding: {e}")
            return []
    
    def migrar_faqs_con_embeddings(self):
        """
        Migra todas las FAQs de Firebase agregando embeddings
        """
        try:
            # Obtener todas las FAQs de Firebase
            faqs_ref = self.db.collection('faqs')
            docs = faqs_ref.stream()
            
            contador = 0
            for doc in docs:
                data = doc.to_dict()
                
                # Verificar si ya tiene embedding
                if 'embedding_pregunta' not in data or 'embedding_respuesta' not in data:
                    pregunta = data.get('pregunta', '')
                    respuesta = data.get('respuesta', '')
                    
                    # Generar embeddings
                    embedding_pregunta = self.generar_embedding(pregunta)
                    embedding_respuesta = self.generar_embedding(respuesta)
                    
                    # Actualizar documento en Firebase
                    doc.reference.update({
                        'embedding_pregunta': embedding_pregunta,
                        'embedding_respuesta': embedding_respuesta,
                        'embedding_combinado': self.generar_embedding(f"{pregunta} {respuesta}"),
                        'fecha_embedding': firestore.SERVER_TIMESTAMP
                    })
                    
                    contador += 1
                    if contador % 10 == 0:
                        logger.info(f"Procesadas {contador} FAQs...")
            
            logger.info(f"✅ Migración completada: {contador} FAQs actualizadas con embeddings")
            return True
            
        except Exception as e:
            logger.error(f"Error en migración de embeddings: {e}")
            return False
    
    def cargar_indice_vectorial(self):
        """
        Carga todas las FAQs de Firebase y crea índice FAISS
        """
        try:
            faqs_ref = self.db.collection('faqs')
            docs = faqs_ref.stream()
            
            embeddings = []
            documentos = []
            
            for doc in docs:
                data = doc.to_dict()
                
                if 'embedding_combinado' in data:
                    embedding = np.array(data['embedding_combinado'], dtype=np.float32)
                    embeddings.append(embedding)
                    documentos.append({
                        'id': doc.id,
                        'pregunta': data.get('pregunta', ''),
                        'respuesta': data.get('respuesta', ''),
                        'metadata': data
                    })
            
            if embeddings:
                # Crear índice FAISS
                embeddings_matrix = np.vstack(embeddings)
                self.index = faiss.IndexFlatIP(self.dimension)  # Inner Product (cosine similarity)
                faiss.normalize_L2(embeddings_matrix)  # Normalizar para cosine similarity
                self.index.add(embeddings_matrix)
                self.documents = documentos
                
                logger.info(f"✅ Índice vectorial cargado: {len(documentos)} documentos")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error cargando índice vectorial: {e}")
            return False
    
    def buscar_semantica(self, pregunta: str, top_k: int = 5, umbral: float = 0.75) -> List[Dict]:
        """
        Búsqueda semántica usando embeddings y FAISS
        """
        try:
            if not self.index or not self.documents:
                logger.warning("Índice vectorial no cargado, cargando...")
                if not self.cargar_indice_vectorial():
                    return []
            
            # Generar embedding de la pregunta
            query_embedding = self.generar_embedding(pregunta)
            if not query_embedding:
                return []
            
            query_vector = np.array([query_embedding], dtype=np.float32)
            faiss.normalize_L2(query_vector)
            
            # Buscar similares
            scores, indices = self.index.search(query_vector, top_k)
            
            resultados = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if score >= umbral:  # Filtrar por umbral de similitud
                    doc = self.documents[idx]
                    resultados.append({
                        'documento': doc,
                        'score': float(score),
                        'rank': i + 1,
                        'similitud_coseno': float(score)
                    })
            
            return resultados
            
        except Exception as e:
            logger.error(f"Error en búsqueda semántica: {e}")
            return []
    
    def buscar_hibrida(self, pregunta: str, top_k: int = 3) -> Dict:
        """
        Búsqueda híbrida: semántica + textual con respuesta final
        """
        try:
            # 1. Búsqueda semántica (embeddings)
            resultados_semanticos = self.buscar_semantica(pregunta, top_k=top_k, umbral=0.7)
            
            # 2. Búsqueda textual simple (fallback)
            resultados_textuales = self._buscar_textual_simple(pregunta, top_k=top_k)
            
            # 3. Combinar y rankear resultados
            todos_resultados = []
            
            # Agregar resultados semánticos con peso alto
            for resultado in resultados_semanticos:
                resultado['peso_total'] = resultado['score'] * 0.8  # 80% peso semántico
                resultado['metodo'] = 'semantico'
                todos_resultados.append(resultado)
            
            # Agregar resultados textuales si no hay suficientes semánticos
            if len(resultados_semanticos) < 2:
                for resultado in resultados_textuales:
                    # Evitar duplicados
                    ya_existe = any(r['documento']['id'] == resultado['documento']['id'] 
                                  for r in todos_resultados)
                    if not ya_existe:
                        resultado['peso_total'] = resultado['score'] * 0.4  # 40% peso textual
                        resultado['metodo'] = 'textual'
                        todos_resultados.append(resultado)
            
            # Ordenar por peso total
            todos_resultados.sort(key=lambda x: x['peso_total'], reverse=True)
            
            # 4. Si hay resultados, devolver el mejor
            if todos_resultados and todos_resultados[0]['peso_total'] > 0.3:  # Umbral más alto
                mejor_resultado = todos_resultados[0]
                respuesta_original = mejor_resultado['documento']['respuesta']
                
                # Usar respuesta directa sin reformulación para evitar alucinaciones
                return {
                    'found': True,
                    'answer': respuesta_original,
                    'pregunta_original': mejor_resultado['documento']['pregunta'],
                    'similarity': mejor_resultado['peso_total'],
                    'metodo': mejor_resultado['metodo'],
                    'resultados_detalle': todos_resultados[:top_k]
                }
            
            # 5. Si no hay resultados suficientes
            return {
                'found': False,
                'answer': None,
                'similarity': 0.0,
                'metodo': 'sin_resultados',
                'resultados_detalle': todos_resultados[:top_k] if todos_resultados else []
            }
            
        except Exception as e:
            logger.error(f"Error en búsqueda híbrida: {e}")
            return {
                'found': False,
                'answer': None,
                'similarity': 0.0,
                'metodo': 'error',
                'error': str(e)
            }
    
    def _buscar_textual_simple(self, pregunta: str, top_k: int = 3) -> List[Dict]:
        """
        Búsqueda textual simple como fallback
        """
        try:
            from difflib import SequenceMatcher
            
            faqs_ref = self.db.collection('faqs')
            docs = faqs_ref.stream()
            
            resultados = []
            
            for doc in docs:
                data = doc.to_dict()
                pregunta_faq = data.get('pregunta', '')
                
                # Calcular similitud textual
                similitud = SequenceMatcher(None, pregunta.lower(), pregunta_faq.lower()).ratio()
                
                if similitud >= 0.3:  # Umbral mínimo
                    resultados.append({
                        'documento': {
                            'id': doc.id,
                            'pregunta': pregunta_faq,
                            'respuesta': data.get('respuesta', ''),
                            'metadata': data
                        },
                        'score': similitud,
                        'similitud_textual': similitud
                    })
            
            # Ordenar por similitud
            resultados.sort(key=lambda x: x['score'], reverse=True)
            return resultados[:top_k]
            
        except Exception as e:
            logger.error(f"Error en búsqueda textual: {e}")
            return []

# Instancia global del servicio
firebase_embeddings = FirebaseEmbeddingsService()
