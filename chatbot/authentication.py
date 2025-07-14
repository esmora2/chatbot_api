from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.contrib.auth.models import AnonymousUser


class FAQTokenAuthentication(BaseAuthentication):
    """
    Autenticación personalizada para el manejo de FAQ usando un token específico
    """
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return None
            
        try:
            token_type, token = auth_header.split()
            if token_type.lower() != 'bearer':
                return None
        except ValueError:
            return None
        
        expected_token = getattr(settings, 'FAQ_MANAGEMENT_TOKEN', None)
        
        if not expected_token:
            raise AuthenticationFailed('Token de FAQ no configurado en el servidor')
        
        if token != expected_token:
            raise AuthenticationFailed('Token de autorización inválido')
        
        # Retornar usuario anónimo ya que no necesitamos un usuario específico
        # solo verificar que tenga el token correcto
        return (AnonymousUser(), token)
    
    def authenticate_header(self, request):
        return 'Bearer'


class PublicAuthentication(BaseAuthentication):
    """
    Autenticación que permite acceso público (para el chatbot)
    """
    
    def authenticate(self, request):
        return (AnonymousUser(), None)
