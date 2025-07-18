#!/usr/bin/env python3
import os
import sys
import json

# Agregar el directorio del proyecto al path
sys.path.append('/home/erickxse/visual/asegcbot/chatbot_api')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chatbot_api.settings')

try:
    import django
    django.setup()
    print("Django configurado correctamente")
except Exception as e:
    print(f"Error configurando Django: {e}")
    sys.exit(1)

try:
    from chatbot.views import ChatbotAPIView
    from rest_framework.test import APIRequestFactory
    
    # Crear una instancia de la vista
    vista = ChatbotAPIView()
    
    # Crear un request de prueba
    factory = APIRequestFactory()
    request = factory.post('/api/chatbot/', 
                          json.dumps({"pregunta": "quien es el director de carrera de software en la ESPE"}),
                          content_type='application/json')
    
    # Simular el procesamiento
    request.data = {"pregunta": "quien es el director de carrera de software en la ESPE"}
    
    print("Procesando consulta...")
    response = vista.post(request)
    
    print("=== RESPUESTA ===")
    print(f"Status: {response.status_code}")
    print(f"Data: {response.data}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
