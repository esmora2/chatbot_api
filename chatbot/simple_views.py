from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from .simple_auth import SimpleTokenAuthentication
from .faq_utils import agregar_faq_entry_simple, validar_faq_duplicado_simple, obtener_estadisticas_faq_simple


class FAQManagementAPIView(APIView):
    """
    Endpoint protegido para agregar preguntas y respuestas al FAQ
    Requiere token: Bearer your-secure-token-here-change-in-production
    """
    authentication_classes = [SimpleTokenAuthentication]
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Agregar nueva entrada al FAQ
        """
        pregunta = request.data.get('pregunta')
        respuesta = request.data.get('respuesta')
        categoria = request.data.get('categoria', 'General')  # Categoría opcional, por defecto "General"
        
        if not pregunta or not respuesta:
            return Response({
                'error': 'Los campos pregunta y respuesta son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar longitud mínima
        if len(pregunta.strip()) < 5:
            return Response({
                'error': 'La pregunta debe tener al menos 5 caracteres'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(respuesta.strip()) < 10:
            return Response({
                'error': 'La respuesta debe tener al menos 10 caracteres'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        verificar_duplicados = request.data.get('verificar_duplicados', True)
        forzar = request.data.get('forzar', False)
        
        # Verificar duplicados si está habilitado
        if verificar_duplicados and not forzar:
            duplicado_info = validar_faq_duplicado_simple(pregunta)
            if duplicado_info['es_duplicado']:
                return Response({
                    'error': 'Pregunta duplicada detectada',
                    'pregunta_similar': duplicado_info['pregunta_similar'],
                    'similitud': duplicado_info['similitud'],
                    'sugerencia': 'Use forzar=true para agregar de todos modos'
                }, status=status.HTTP_409_CONFLICT)
        
        # Agregar la entrada con la nueva función que incluye categoría
        resultado = agregar_faq_entry_simple(pregunta, respuesta, categoria)
        
        if resultado['success']:
            return Response({
                'mensaje': 'FAQ agregado exitosamente',
                'entrada': resultado['entrada'],
                'estadisticas': obtener_estadisticas_faq_simple(),
                'synced_to_s3': resultado.get('synced_to_s3', False)  # 🚀 Agregado
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': 'Error al agregar FAQ',
                'detalle': resultado['message']
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """
        Obtener estadísticas del FAQ
        """
        estadisticas = obtener_estadisticas_faq_simple()
        return Response({
            'estadisticas': estadisticas,
            'mensaje': 'Estadísticas del FAQ obtenidas exitosamente'
        }, status=status.HTTP_200_OK)


class FAQDuplicateCheckAPIView(APIView):
    """
    Endpoint protegido para verificar duplicados en el FAQ
    """
    authentication_classes = [SimpleTokenAuthentication]
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Verificar si una pregunta ya existe en el FAQ
        """
        pregunta = request.data.get('pregunta')
        if not pregunta:
            return Response({
                'error': 'El campo pregunta es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        umbral = request.data.get('umbral_similitud', 0.8)
        
        try:
            umbral = float(umbral)
            if not 0 <= umbral <= 1:
                raise ValueError()
        except (ValueError, TypeError):
            return Response({
                'error': 'umbral_similitud debe ser un número entre 0 y 1'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        resultado = validar_faq_duplicado_simple(pregunta, umbral)
        
        return Response({
            'pregunta_consultada': pregunta,
            'umbral_usado': umbral,
            'es_duplicado': resultado['es_duplicado'],
            'pregunta_similar': resultado['pregunta_similar'],
            'similitud': resultado['similitud'],
            'recomendacion': 'No agregar' if resultado['es_duplicado'] else 'Puede agregar'
        }, status=status.HTTP_200_OK)


class SimpleTestAPIView(APIView):
    """
    Vista de prueba simple
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        return Response({
            'message': 'FAQ endpoint is working!',
            'data_received': request.data
        }, status=status.HTTP_200_OK)
    
    def get(self, request):
        return Response({
            'message': 'FAQ management endpoint',
            'methods': ['GET', 'POST']
        }, status=status.HTTP_200_OK)
