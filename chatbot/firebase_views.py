"""
Views actualizadas para usar Firebase Firestore en lugar de CSV
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from .firebase_service import firebase_service
from .authentication import FAQTokenAuthentication
import logging

logger = logging.getLogger(__name__)

class FirebaseFAQManagementAPIView(APIView):
    """
    Gestión de FAQ usando Firebase Firestore
    """
    authentication_classes = [FAQTokenAuthentication]
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Obtener todas las FAQs o estadísticas
        """
        action = request.query_params.get('action', 'list')
        
        if action == 'stats':
            stats = firebase_service.get_stats()
            return Response({
                'estadisticas': stats,
                'mensaje': 'Estadísticas obtenidas de Firebase'
            })
        
        elif action == 'list':
            faqs = firebase_service.get_all_faqs()
            return Response({
                'faqs': faqs,
                'total': len(faqs),
                'mensaje': f'{len(faqs)} FAQs obtenidas de Firebase'
            })
        
        else:
            return Response({
                'error': 'Acción no válida. Use: list o stats'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request):
        """
        Agregar nueva FAQ a Firebase
        """
        pregunta = request.data.get('pregunta', '').strip()
        respuesta = request.data.get('respuesta', '').strip()
        categoria = request.data.get('categoria', '').strip()
        
        if not pregunta or not respuesta:
            return Response({
                'error': 'Los campos pregunta y respuesta son obligatorios'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar Firebase conectado
        if not firebase_service.is_connected():
            return Response({
                'error': 'Firebase no está conectado. Verifique la configuración.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Agregar FAQ
        success, message = firebase_service.add_faq(pregunta, respuesta, categoria)
        
        if success:
            stats = firebase_service.get_stats()
            return Response({
                'mensaje': message,
                'pregunta': pregunta,
                'respuesta': respuesta,
                'categoria': categoria,
                'estadisticas': stats
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request):
        """
        Actualizar FAQ existente
        """
        document_id = request.data.get('document_id', '').strip()
        
        if not document_id:
            return Response({
                'error': 'El campo document_id es obligatorio'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar Firebase conectado
        if not firebase_service.is_connected():
            return Response({
                'error': 'Firebase no está conectado'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Extraer campos opcionales
        pregunta = request.data.get('pregunta')
        respuesta = request.data.get('respuesta')
        categoria = request.data.get('categoria')
        
        if pregunta is not None:
            pregunta = pregunta.strip()
        if respuesta is not None:
            respuesta = respuesta.strip()
        if categoria is not None:
            categoria = categoria.strip()
        
        # Actualizar FAQ
        success, message = firebase_service.update_faq(document_id, pregunta, respuesta, categoria)
        
        if success:
            return Response({
                'mensaje': message,
                'document_id': document_id
            })
        else:
            return Response({
                'error': message
            }, status=status.HTTP_404_NOT_FOUND if 'no encontrada' in message else status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request):
        """
        Eliminar (desactivar) FAQ
        """
        document_id = request.data.get('document_id', '').strip()
        
        if not document_id:
            return Response({
                'error': 'El campo document_id es obligatorio'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar Firebase conectado
        if not firebase_service.is_connected():
            return Response({
                'error': 'Firebase no está conectado'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Eliminar FAQ
        success, message = firebase_service.delete_faq(document_id)
        
        if success:
            return Response({
                'mensaje': message,
                'document_id': document_id
            })
        else:
            return Response({
                'error': message
            }, status=status.HTTP_404_NOT_FOUND if 'no encontrada' in message else status.HTTP_500_INTERNAL_SERVER_ERROR)


class FirebaseFAQSearchAPIView(APIView):
    """
    Búsqueda de FAQ en Firebase
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Buscar FAQs por query
        """
        query = request.query_params.get('q', '').strip()
        limit = int(request.query_params.get('limit', 10))
        
        if not query:
            return Response({
                'error': 'Parámetro q (query) es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar Firebase conectado
        if not firebase_service.is_connected():
            return Response({
                'error': 'Firebase no está conectado'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Buscar FAQs
        faqs = firebase_service.search_faqs(query, limit)
        
        return Response({
            'query': query,
            'resultados': faqs,
            'total_encontrados': len(faqs),
            'limite': limit
        })
    
    def post(self, request):
        """
        Búsqueda avanzada con POST
        """
        query = request.data.get('query', '').strip()
        limit = request.data.get('limit', 10)
        
        if not query:
            return Response({
                'error': 'El campo query es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar Firebase conectado
        if not firebase_service.is_connected():
            return Response({
                'error': 'Firebase no está conectado'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        
        # Buscar FAQs
        faqs = firebase_service.search_faqs(query, limit)
        
        return Response({
            'query': query,
            'resultados': faqs,
            'total_encontrados': len(faqs),
            'metodo': 'firebase_search'
        })


class FirebaseStatusAPIView(APIView):
    """
    Estado de conexión con Firebase
    """
    authentication_classes = []
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Verificar estado de Firebase
        """
        is_connected = firebase_service.is_connected()
        
        if is_connected:
            stats = firebase_service.get_stats()
            return Response({
                'firebase_conectado': True,
                'proyecto': 'chatbot-dcco',
                'coleccion': 'faqs',
                'estadisticas': stats,
                'mensaje': 'Firebase Firestore conectado y funcionando'
            })
        else:
            return Response({
                'firebase_conectado': False,
                'error': 'No se pudo conectar a Firebase Firestore',
                'solucion': 'Verificar credenciales y configuración'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
