from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from django.contrib.auth.models import AnonymousUser


class SimpleTokenAuthentication(BaseAuthentication):
    """
    Autenticación simplificada por token
    """
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return None
            
        try:
            token_type, token = auth_header.split(' ', 1)
            if token_type.lower() != 'bearer':
                return None
        except ValueError:
            return None
        
        # Token por defecto
        expected_token = 'your-secure-token-here-change-in-production'
        
        if token != expected_token:
            raise AuthenticationFailed('Token de autorización inválido')
        
        return (AnonymousUser(), token)
    
    def authenticate_header(self, request):
        return 'Bearer'
