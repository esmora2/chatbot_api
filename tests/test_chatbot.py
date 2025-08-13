"""
Pruebas unitarias para el sistema de chatbot
"""
import pytest
import django
from django.test import TestCase
from django.test.client import RequestFactory
from unittest.mock import patch, MagicMock
import json

# Configurar Django para las pruebas
django.setup()

from chatbot.views import ChatbotAPIView, es_pregunta_fuera_contexto, similitud_texto
from chatbot.firebase_service import FirebaseService


class TestChatbotViews(TestCase):
    """
    Pruebas unitarias para las vistas del chatbot
    """
    
    def setUp(self):
        """
        Configuración inicial para cada test
        """
        self.factory = RequestFactory()
        self.chatbot_view = ChatbotAPIView()
    
    @pytest.mark.unit
    def test_similitud_texto(self):
        """
        Prueba la función de similitud de texto
        """
        # Caso 1: Textos idénticos
        similitud = similitud_texto("hola mundo", "hola mundo")
        self.assertEqual(similitud, 1.0)
        
        # Caso 2: Textos completamente diferentes
        similitud = similitud_texto("hola", "adiós")
        self.assertLess(similitud, 0.5)
        
        # Caso 3: Textos similares
        similitud = similitud_texto("¿Qué es el DCCO?", "¿Que es el dcco?")
        self.assertGreater(similitud, 0.8)
    
    @pytest.mark.unit
    def test_es_pregunta_fuera_contexto(self):
        """
        Prueba la detección de preguntas fuera de contexto
        """
        # Preguntas académicas válidas
        preguntas_validas = [
            "¿Qué es el DCCO?",
            "¿Dónde queda la ESPE?",
            "¿Quién es el director de software?",
            "¿Qué materias tiene la carrera?",
            "¿Cómo inscribirse en la universidad?"
        ]
        
        for pregunta in preguntas_validas:
            with self.subTest(pregunta=pregunta):
                resultado = es_pregunta_fuera_contexto(pregunta)
                self.assertFalse(resultado, f"'{pregunta}' debería ser válida")
        
        # Preguntas fuera de contexto
        preguntas_invalidas = [
            "¿Quién es el presidente?",
            "¿Cómo cocinar pasta?",
            "¿Qué película recomiendas?",
            "¿Cuál es la capital de Francia?",
            "¿Cómo está el clima?"
        ]
        
        for pregunta in preguntas_invalidas:
            with self.subTest(pregunta=pregunta):
                resultado = es_pregunta_fuera_contexto(pregunta)
                self.assertTrue(resultado, f"'{pregunta}' debería ser inválida")
    
    @pytest.mark.unit
    def test_detectar_intencion(self):
        """
        Prueba la detección de intenciones básicas
        """
        # Saludos
        self.assertEqual(self.chatbot_view.detectar_intencion("hola"), "saludos")
        self.assertEqual(self.chatbot_view.detectar_intencion("buenos días"), "saludos")
        
        # Despedidas
        self.assertEqual(self.chatbot_view.detectar_intencion("adiós"), "despedidas")
        self.assertEqual(self.chatbot_view.detectar_intencion("hasta luego"), "despedidas")
        
        # Agradecimientos
        self.assertEqual(self.chatbot_view.detectar_intencion("gracias"), "agradecimientos")
        self.assertEqual(self.chatbot_view.detectar_intencion("muchas gracias"), "agradecimientos")
        
        # Sin intención detectada
        self.assertIsNone(self.chatbot_view.detectar_intencion("¿Qué es el DCCO?"))
    
    @pytest.mark.unit
    def test_es_pregunta_academica_valida(self):
        """
        Prueba la validación de preguntas académicas
        """
        # Preguntas que deberían ser válidas
        preguntas_academicas = [
            "¿Qué es el DCCO?",
            "¿Dónde queda la ESPE?",
            "¿De qué trata aplicaciones basadas en el conocimiento?",
            "¿Quién es el director de software?",
            "¿Cómo llegar a la universidad?"
        ]
        
        for pregunta in preguntas_academicas:
            with self.subTest(pregunta=pregunta):
                resultado = self.chatbot_view._es_pregunta_academica_valida(pregunta)
                self.assertTrue(resultado, f"'{pregunta}' debería ser académicamente válida")
    
    @pytest.mark.unit
    @patch('chatbot.views.consultar_openai')
    def test_consultar_llm_inteligente_openai_success(self, mock_openai):
        """
        Prueba que consultar_llm_inteligente use OpenAI correctamente
        """
        from chatbot.views import consultar_llm_inteligente
        
        # Configurar mock
        mock_openai.return_value = "Respuesta de OpenAI"
        
        # Ejecutar función
        resultado = consultar_llm_inteligente("Test prompt")
        
        # Verificar
        self.assertEqual(resultado, "Respuesta de OpenAI")
        mock_openai.assert_called_once_with("Test prompt")
    
    @pytest.mark.unit
    @patch('chatbot.views.consultar_openai')
    def test_consultar_llm_inteligente_openai_failure(self, mock_openai):
        """
        Prueba el comportamiento cuando OpenAI falla
        """
        from chatbot.views import consultar_llm_inteligente
        
        # Configurar mock para fallar
        mock_openai.return_value = None
        
        # Ejecutar función
        resultado = consultar_llm_inteligente("Test prompt")
        
        # Verificar que retorna None cuando OpenAI falla
        self.assertIsNone(resultado)


class TestFirebaseService(TestCase):
    """
    Pruebas unitarias para el servicio de Firebase
    """
    
    def setUp(self):
        """
        Configuración inicial
        """
        self.firebase_service = FirebaseService()
    
    @pytest.mark.unit
    def test_extract_keywords(self):
        """
        Prueba la extracción de palabras clave
        """
        texto = "¿Qué es el Departamento de Ciencias de la Computación?"
        keywords = self.firebase_service._extract_keywords(texto)
        
        # Verificar que extrae palabras clave relevantes
        self.assertIn("departamento", keywords)
        self.assertIn("ciencias", keywords)
        self.assertIn("computación", keywords)
        
        # Verificar que no incluye palabras vacías
        self.assertNotIn("de", keywords)
        self.assertNotIn("la", keywords)
        self.assertNotIn("es", keywords)
    
    @pytest.mark.unit
    def test_is_connected(self):
        """
        Prueba la verificación de conexión
        """
        # Verificar que el método is_connected existe y retorna un booleano
        resultado = self.firebase_service.is_connected()
        self.assertIsInstance(resultado, bool)


class TestChatbotAPI(TestCase):
    """
    Pruebas de integración para la API del chatbot
    """
    
    @pytest.mark.integration
    def test_chatbot_endpoint_basic(self):
        """
        Prueba básica del endpoint del chatbot
        """
        response = self.client.post(
            '/chatbot/',
            data=json.dumps({'pregunta': '¿Qué es el DCCO?'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('respuesta', data)
        self.assertIn('metodo', data)
    
    @pytest.mark.integration
    def test_chatbot_endpoint_empty_question(self):
        """
        Prueba el endpoint con pregunta vacía
        """
        response = self.client.post(
            '/chatbot/',
            data=json.dumps({'pregunta': ''}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    @pytest.mark.integration
    def test_chatbot_endpoint_no_question(self):
        """
        Prueba el endpoint sin campo pregunta
        """
        response = self.client.post(
            '/chatbot/',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
    
    @pytest.mark.integration
    def test_chatbot_endpoint_out_of_context(self):
        """
        Prueba el endpoint con pregunta fuera de contexto
        """
        response = self.client.post(
            '/chatbot/',
            data=json.dumps({'pregunta': '¿Quién es el presidente de Ecuador?'}),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('respuesta', data)
        # Verificar que la respuesta indica que está fuera de contexto
        self.assertIn('contexto', data['respuesta'].lower())


class TestSecurityValidation(TestCase):
    """
    Pruebas de seguridad básicas
    """
    
    @pytest.mark.security
    def test_sql_injection_protection(self):
        """
        Prueba protección contra inyección SQL
        """
        malicious_input = "'; DROP TABLE users; --"
        response = self.client.post(
            '/chatbot/',
            data=json.dumps({'pregunta': malicious_input}),
            content_type='application/json'
        )
        
        # Verificar que no ejecuta código malicioso
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertNotIn('DROP TABLE', data.get('respuesta', ''))
    
    @pytest.mark.security
    def test_xss_protection(self):
        """
        Prueba protección contra XSS
        """
        malicious_input = '<script>alert("xss")</script>'
        response = self.client.post(
            '/chatbot/',
            data=json.dumps({'pregunta': malicious_input}),
            content_type='application/json'
        )
        
        # Verificar que no ejecuta scripts
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertNotIn('<script>', data.get('respuesta', ''))
    
    @pytest.mark.security
    def test_large_payload_handling(self):
        """
        Prueba el manejo de payloads grandes
        """
        large_input = 'A' * 10000  # 10KB de datos
        response = self.client.post(
            '/chatbot/',
            data=json.dumps({'pregunta': large_input}),
            content_type='application/json'
        )
        
        # Verificar que maneja el payload sin crashes
        self.assertIn(response.status_code, [200, 400, 413])  # OK, Bad Request, o Payload Too Large


class TestPerformance(TestCase):
    """
    Pruebas básicas de rendimiento
    """
    
    @pytest.mark.performance
    def test_response_time_acceptable(self):
        """
        Prueba que el tiempo de respuesta sea aceptable
        """
        import time
        
        start_time = time.time()
        response = self.client.post(
            '/chatbot/',
            data=json.dumps({'pregunta': '¿Qué es el DCCO?'}),
            content_type='application/json'
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        # Verificar que responde en menos de 10 segundos (test local)
        self.assertLess(response_time, 10.0, "Tiempo de respuesta excesivo")
        self.assertEqual(response.status_code, 200)


# Configuración para pytest
def pytest_configure(config):
    """
    Configuración global para pytest
    """
    import django
    from django.conf import settings
    
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.sqlite3',
                    'NAME': ':memory:',
                }
            },
            INSTALLED_APPS=[
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'chatbot',
            ],
            SECRET_KEY='test-secret-key-for-testing-only'
        )
    
    django.setup()
