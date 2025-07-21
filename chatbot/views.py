import csv, os, datetime
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone 
from django.http import Http404
from rest_framework import status
from rest_framework.permissions import AllowAny
from difflib import SequenceMatcher
import re
import requests
import ollama

from .vector_store import buscar_documentos
from .serializers import FAQEntrySerializer, ChatbotQuerySerializer
from .authentication import FAQTokenAuthentication, PublicAuthentication
from .document_loader import agregar_faq_entry, validar_faq_duplicado, obtener_estadisticas_faq

import logging

logger = logging.getLogger(__name__)

# API mejorada que maneja correctamente las respuestas del CSV
# Función para calcular similitud entre textos
from django.conf import settings

# Obtener API key desde settings/environment
OPENAI_API_KEY = getattr(settings, 'OPENAI_API_KEY', '')

# --------- FUNCIONES AUXILIARES ---------

def similitud_texto(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def es_pregunta_fuera_contexto(pregunta):
    """
    Detecta si una pregunta está fuera del contexto del DCCO/ESPE
    """
    pregunta_lower = pregunta.lower().strip()
    
    # Palabras clave que indican contexto académico/universitario válido
    contexto_valido = [
        # Universidad/ESPE
        "espe", "universidad", "fuerzas armadas", "militar", "dcco", 
        "departamento", "computación", "ciencias de la computación",
        
        # Académico
        "carrera", "materia", "profesor", "docente", "estudiante", "alumno",
        "clase", "curso", "syllabus", "programa", "semestre", "periodo",
        "examen", "tarea", "proyecto", "tesis", "calificación", "nota",
        "inscripción", "matricula", "registro", "graduación", "titulación",
        
        # Servicios universitarios
        "biblioteca", "laboratorio", "aula", "salón", "edificio", "bloque",
        "secretaria", "coordinador", "director", "decano", "rector",
        "bienestar", "psicólogo", "médico", "enfermería", "comedor", "bar",
        "parqueo", "transporte", "beca", "ayuda", "financiera",
        
        # Tecnología/Computación
        "programación", "software", "hardware", "algoritmo", "base de datos",
        "redes", "sistemas", "ingeniería", "desarrollo", "código", "aplicación",
        "web", "móvil", "inteligencia artificial", "machine learning",
        "aplicaciones", "conocimiento", "basadas", "expertos", "ia",
        
        # Procesos universitarios
        "admisión", "requisitos", "documentos", "certificado", "horario",
        "cronograma", "calendario", "actividades", "eventos", "conferencia"
    ]
    
    # Temas claramente fuera de contexto
    temas_prohibidos = [
        # Política
        "presidente", "gobierno", "político", "elecciones", "democracia",
        "congreso", "asamblea", "ministro", "alcalde", "prefecto",
        
        # Geografía general
        "país", "países", "capital", "ciudad", "continente", "océano",
        "río", "montaña", "clima", "temperatura", "población",
        
        # Historia general
        "guerra", "batalla", "imperio", "conquista", "independencia",
        "revolución", "histórico", "siglo", "época", "era",
        
        # Entretenimiento
        "película", "actor", "cantante", "música", "deporte", "fútbol",
        "televisión", "series", "videojuego", "celebridad",
        
        # Ciencias generales (no computación)
        "medicina", "biología", "química", "física", "astronomía",
        "matemáticas", "psicología", "filosofía", "sociología",
        
        # Tiempo/Fecha
        "hora", "tiempo", "fecha", "día", "mes", "año", "calendario",
        
        # Otros temas generales
        "receta", "cocina", "comida", "restaurante", "viaje", "turismo",
        "dinero", "precio", "costo", "comprar", "vender", "negocio"
    ]
    
    # Verificar si contiene palabras de contexto válido
    tiene_contexto_valido = any(palabra in pregunta_lower for palabra in contexto_valido)
    
    # Verificar si contiene temas prohibidos
    tiene_tema_prohibido = any(palabra in pregunta_lower for palabra in temas_prohibidos)
    
    # La pregunta está fuera de contexto si:
    # 1. No tiene palabras de contexto válido Y tiene temas prohibidos
    # 2. O si tiene claramente temas prohibidos sin contexto universitario
    if tiene_tema_prohibido and not tiene_contexto_valido:
        return True
    
    return False

def validar_relevancia_respuesta(pregunta, respuesta, documentos):
    """
    Valida si la respuesta generada es relevante al contexto del DCCO/ESPE
    """
    # Si no hay documentos relevantes, la respuesta probablemente no es válida
    if not documentos:
        return False
    
    # Si hay documentos PDF, ser más permisivo
    tiene_pdf = any(doc.metadata.get("source") == "pdf" for doc in documentos)
    
    # Calcular relevancia promedio de los documentos encontrados
    relevancia_promedio = 0
    documentos_validos = 0
    
    for doc in documentos:
        # Incluir todos los tipos de documentos (FAQ, web, PDF)
        if doc.metadata.get("source") in ["faq", "web", "pdf"]:
            score = similitud_texto(pregunta, doc.page_content[:200])
            relevancia_promedio += score
            documentos_validos += 1
    
    if documentos_validos > 0:
        relevancia_promedio /= documentos_validos
    
    # Ajustar umbral basado en el tipo de documentos
    umbral = 0.01 if tiene_pdf else 0.05
    if relevancia_promedio < umbral:
        return False
    
    # Si la respuesta está vacía (llamada previa), permitir continuar
    if not respuesta.strip():
        return True
    
    # Verificar si la respuesta contiene información específica del DCCO/ESPE
    respuesta_lower = respuesta.lower()
    indicadores_especificos = [
        "espe", "dcco", "departamento", "computación", "universidad",
        "estudiante", "curso", "materia", "profesor", "carrera",
        "syllabus", "programa", "aplicaciones", "conocimiento", "software"
    ]
    
    tiene_indicadores = any(indicador in respuesta_lower for indicador in indicadores_especificos)
    
    return tiene_indicadores

def generar_respuesta_fuera_contexto():
    """
    Genera una respuesta estándar para preguntas fuera del contexto
    """
    respuestas = [
        "Lo siento, pero solo puedo ayudarte con preguntas relacionadas al Departamento de Ciencias de la Computación (DCCO) de la ESPE. ¿Hay algo específico sobre la universidad, carreras, materias o servicios estudiantiles en lo que pueda ayudarte?",
        
        "Mi función es asistir con consultas relacionadas al DCCO y la ESPE. No puedo responder preguntas fuera de este contexto académico. ¿Tienes alguna pregunta sobre la universidad, el departamento o los servicios estudiantiles?",
        
        "Estoy diseñado para ayudarte específicamente con información del Departamento de Ciencias de la Computación de la ESPE. ¿Podrías hacer una pregunta relacionada con la universidad, las carreras o los servicios académicos?",
        
        "Solo puedo proporcionar información relacionada con el DCCO y la Universidad de las Fuerzas Armadas ESPE. ¿Hay algo sobre la institución, las carreras de computación o los servicios estudiantiles que te gustaría saber?"
    ]
    
    import random
    return random.choice(respuestas)

def consultar_openai(prompt):
    """
    Llama a OpenAI (GPT-3.5) con un prompt.
    Fallback: si falla, devuelve None para usar respuesta directa.
    """
    try:
        # Usar API key desde settings si está disponible
        api_key = getattr(settings, 'OPENAI_API_KEY', None) or OPENAI_API_KEY
        
        if not api_key or api_key == 'your-openai-api-key-here':
            logger.warning("OpenAI API key no configurada correctamente")
            return None
            
        endpoint = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "Eres un asistente académico del Departamento de Ciencias de la Computación de la ESPE. Responde siempre en español."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.6
        }
        response = requests.post(endpoint, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"].strip()
        else:
            logger.error(f"Error OpenAI API: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        logger.error(f"Error consultando OpenAI: {e}")
        return None

def consultar_ollama(prompt):
    """
    Llama a Ollama con un prompt usando el modelo local.
    Fallback: si falla, devuelve None para usar respuesta directa.
    """
    try:
        # Obtener configuración de Ollama desde settings
        ollama_host = getattr(settings, 'OLLAMA_HOST', 'http://localhost:11434')
        ollama_model = getattr(settings, 'OLLAMA_MODEL', 'llama3.2:1b')
        
        # Configurar cliente de Ollama
        client = ollama.Client(host=ollama_host)
        
        # Hacer la consulta
        response = client.chat(model=ollama_model, messages=[
            {
                'role': 'system',
                'content': 'Eres un asistente académico del Departamento de Ciencias de la Computación de la ESPE. Responde siempre en español de manera clara y concisa.'
            },
            {
                'role': 'user',
                'content': prompt
            }
        ])
        
        if response and 'message' in response and 'content' in response['message']:
            return response['message']['content'].strip()
        else:
            logger.error("Respuesta de Ollama con formato inesperado")
            return None
            
    except Exception as e:
        logger.error(f"Error consultando Ollama: {e}")
        return None

def consultar_llm_inteligente(prompt):
    """
    Función inteligente que intenta primero OpenAI y luego Ollama como fallback.
    Si ambos fallan, devuelve None para usar respuesta directa.
    """
    # Intentar primero con OpenAI
    respuesta_openai = consultar_openai(prompt)
    if respuesta_openai is not None:
        logger.info("Respuesta generada con OpenAI")
        return respuesta_openai
    
    # Si OpenAI falla, intentar con Ollama (si está habilitado)
    use_ollama_fallback = getattr(settings, 'USE_OLLAMA_FALLBACK', True)
    if use_ollama_fallback:
        logger.info("OpenAI falló, intentando con Ollama...")
        respuesta_ollama = consultar_ollama(prompt)
        if respuesta_ollama is not None:
            logger.info("Respuesta generada con Ollama")
            return respuesta_ollama
    
    # Si ambos fallan, retornar None para usar respuesta directa
    logger.warning("Tanto OpenAI como Ollama fallaron")
    return None

# --------- CLASE PRINCIPAL DE LA API ---------

class ChatbotAPIView(APIView):
    authentication_classes = [PublicAuthentication]
    permission_classes = [AllowAny]
    
    INTENCIONES_BASICAS = {
        "saludos": ["hola", "buenos días", "buenas tardes", "hi", "hello"],
        "despedidas": ["adiós", "hasta luego", "nos vemos", "bye"],
        "agradecimientos": ["gracias", "muchas gracias", "thanks"]
    }

    RESPUESTAS_BASICAS = {
        "saludos": "¡Hola! ¿En qué puedo ayudarte hoy?",
        "despedidas": "¡Hasta luego! No dudes en volver si tienes más preguntas.",
        "agradecimientos": "¡De nada! Estoy aquí para ayudarte."
    }

    def detectar_intencion(self, pregunta):
        pregunta = pregunta.lower().strip()
        for intencion, palabras in self.INTENCIONES_BASICAS.items():
            if any(palabra in pregunta for palabra in palabras):
                return intencion
        return None

    def post(self, request):
        pregunta = request.data.get("pregunta")
        if not pregunta:
            return Response({"error": "Falta el campo 'pregunta'"}, status=400)

        # 1. Verificar si la pregunta está fuera del contexto del DCCO/ESPE
        if es_pregunta_fuera_contexto(pregunta):
            return Response({
                "respuesta": generar_respuesta_fuera_contexto(),
                "fuente": "sistema",
                "metodo": "fuera_de_contexto"
            }, status=200)

        # 2. Intenciones básicas
        intencion = self.detectar_intencion(pregunta)
        if intencion:
            return Response({
                "respuesta": self.RESPUESTAS_BASICAS[intencion],
                "fuente": "sistema",
                "metodo": "intencion_basica"
            }, status=200)

        try:
            # 3. Buscar primero en Firebase con búsqueda exacta
            resultado_firebase = self.busqueda_firebase_inteligente(pregunta)
            
            if resultado_firebase:
                # Reformular respuesta usando LLM para que suene más natural
                respuesta_base = resultado_firebase["respuesta"]
                prompt = f"""La siguiente es una respuesta basada en nuestra base de conocimientos de la ESPE:

Respuesta base:
{respuesta_base}

Por favor, reformúlala si es necesario para que suene más natural y completa para el usuario que preguntó:

{pregunta}

Respuesta:"""
                
                respuesta_mejorada = consultar_llm_inteligente(prompt)
                
                return Response({
                    "respuesta": respuesta_mejorada if respuesta_mejorada else respuesta_base,
                    "pregunta_relacionada": resultado_firebase["pregunta_original"],
                    "fuente": "FAQ (Firebase)",
                    "metodo": "firebase_reformulada" if respuesta_mejorada else "firebase_directa",
                    "score": resultado_firebase["score"]
                }, status=200)

            # 4. Si no hay resultados en Firebase, usar búsqueda semántica tradicional
            documentos = buscar_documentos(pregunta, top_k=5)

            # 5. Buscar coincidencia exacta en FAQs del vector store (fallback)
            mejor_faq_doc = None
            mejor_faq_score = 0
            
            for doc in documentos:
                if doc.metadata.get("source") == "faq":
                    score = similitud_texto(pregunta, doc.metadata.get("pregunta_original", ""))
                    
                    # Si el score es muy alto (>= 0.75), responder inmediatamente
                    if score >= 0.75:
                        respuesta_base = doc.metadata["respuesta_original"]
                        prompt = f"""La siguiente es una posible respuesta basada en una FAQ de la ESPE:

Respuesta base:
{respuesta_base}

Por favor, reformúlala si es necesario para que suene más natural y completa para el usuario que preguntó:

{pregunta}

Respuesta:"""
                        respuesta_mejorada = consultar_llm_inteligente(prompt)
                        
                        # Si OpenAI falla, usar respuesta original
                        if respuesta_mejorada is None:
                            respuesta_mejorada = respuesta_base
                            metodo = "faq_directa"
                        else:
                            metodo = "faq_reformulada"
                            
                        return Response({
                            "respuesta": respuesta_mejorada,
                            "pregunta_relacionada": doc.metadata["pregunta_original"],
                            "fuente": "FAQ (CSV Backup)",
                            "metodo": metodo,
                            "similitud": round(score, 3)
                        }, status=200)
                    
                    # Guardar el mejor FAQ para usar después si no hay match exacto
                    if score > mejor_faq_score:
                        mejor_faq_doc = doc
                        mejor_faq_score = score

            # 6. Buscar mejor contenido en web/pdf
            mejor_doc = None
            mejor_score = 0
            for doc in documentos:
                if doc.metadata.get("source") != "faq":
                    score = similitud_texto(pregunta, doc.page_content[:200])
                    if score > mejor_score:
                        mejor_doc = doc
                        mejor_score = score

            if mejor_doc and mejor_score >= 0.3:
                contexto = mejor_doc.page_content[:800]
                prompt = f"""Con base únicamente en el siguiente contenido:

{contexto}

Responde la siguiente pregunta de manera clara y académica:

{pregunta}

Respuesta:"""
                respuesta_llm = consultar_llm_inteligente(prompt)
                
                # Si OpenAI falla, usar contenido directamente
                if respuesta_llm is None:
                    respuesta_llm = f"Según la información disponible: {contexto[:400]}..."
                    metodo = "contenido_procesado"
                else:
                    metodo = "pdf_llm_refinado"
                    
                return Response({
                    "respuesta": respuesta_llm,
                    "fuente": mejor_doc.metadata.get("source", "PDF"),
                    "titulo": mejor_doc.metadata.get("titulo", ""),
                    "metodo": metodo,
                    "similitud": round(mejor_score, 3)
                }, status=200)

            # 7. Si no hay buen contenido web/pdf, usar el mejor FAQ si es suficientemente bueno
            if mejor_faq_doc and mejor_faq_score >= 0.6:  # Umbral más bajo para FAQs
                respuesta_base = mejor_faq_doc.metadata["respuesta_original"]
                prompt = f"""La siguiente es una posible respuesta basada en una FAQ de la ESPE:

Respuesta base:
{respuesta_base}

Por favor, reformúlala si es necesario para que suene más natural y completa para el usuario que preguntó:

{pregunta}

Respuesta:"""
                respuesta_mejorada = consultar_llm_inteligente(prompt)
                
                # Si OpenAI falla, usar respuesta original del FAQ
                if respuesta_mejorada is None:
                    respuesta_mejorada = respuesta_base
                    metodo = "faq_backup_directa"
                else:
                    metodo = "faq_mejor_match"
                    
                return Response({
                    "respuesta": respuesta_mejorada,
                    "pregunta_relacionada": mejor_faq_doc.metadata["pregunta_original"],
                    "fuente": "FAQ (CSV Backup)",
                    "metodo": metodo,
                    "similitud": round(mejor_faq_score, 3)
                }, status=200)

            # 8. Validar relevancia antes del fallback
            if not validar_relevancia_respuesta(pregunta, "", documentos):
                return Response({
                    "respuesta": generar_respuesta_fuera_contexto(),
                    "fuente": "sistema",
                    "metodo": "sin_contexto_relevante"
                }, status=200)

            # 9. Último recurso: pasar todo el contexto al LLM con restricción
            contexto_general = "\n\n".join([doc.page_content[:400] for doc in documentos])
            prompt = f"""Eres un asistente del Departamento de Ciencias de la Computación (DCCO) de la ESPE. 
SOLO puedes responder preguntas relacionadas con la universidad, el departamento, carreras, materias, servicios estudiantiles, o información académica.

Si la pregunta no está relacionada con estos temas, responde que solo puedes ayudar con información del DCCO y la ESPE.

Contexto disponible:
{contexto_general}

Pregunta:
{pregunta}

Respuesta:"""
            respuesta_fallback = consultar_llm_inteligente(prompt)
            
            # Si OpenAI falla, usar respuesta genérica del primer documento
            if respuesta_fallback is None:
                if documentos:
                    primer_doc = documentos[0]
                    if primer_doc.metadata.get("source") == "faq":
                        respuesta_fallback = primer_doc.metadata.get("respuesta_original", "")
                    else:
                        respuesta_fallback = primer_doc.page_content[:200] + "..."
                    metodo = "contenido_directo"
                else:
                    return Response({
                        "respuesta": generar_respuesta_fuera_contexto(),
                        "fuente": "sistema",
                        "metodo": "sin_contenido"
                    }, status=200)
            else:
                metodo = "llm_con_restriccion_contexto"
            
            # Validar que la respuesta generada sea relevante (solo si viene de LLM)
            if metodo == "llm_con_restriccion_contexto" and not validar_relevancia_respuesta(pregunta, respuesta_fallback, documentos):
                return Response({
                    "respuesta": generar_respuesta_fuera_contexto(),
                    "fuente": "sistema",
                    "metodo": "respuesta_no_relevante"
                }, status=200)
            
            return Response({
                "respuesta": respuesta_fallback,
                "fuente": "LLM" if metodo == "llm_con_restriccion_contexto" else "Sistema",
                "metodo": metodo
            }, status=200)

        except Exception as e:
            return Response({
                "error": "Error interno del servidor",
                "detalle": str(e)
            }, status=500)

    def busqueda_firebase_inteligente(self, pregunta):
        """
        Busca en Firebase con algoritmo inteligente de matching
        """
        try:
            from .firebase_service import FirebaseService
            firebase_service = FirebaseService()
            
            pregunta_lower = pregunta.lower()
            
            # Palabras clave importantes para dar mayor peso
            palabras_clave = ["psicólogo", "psicóloga", "bienestar", "bar", "comedor", 
                             "departamento", "computación", "biblioteca", "parqueo", 
                             "secretaria", "coordinador", "carrera", "materia", "profesor"]
            
            # Obtener todas las FAQs de Firebase
            faqs = firebase_service.get_all_faqs()
            
            mejor_resultado = None
            mejor_score = 0
            
            for faq in faqs:
                pregunta_faq = faq.get("pregunta", "").lower()
                
                # Calcular similitud exacta
                similitud_exacta = similitud_texto(pregunta_lower, pregunta_faq)
                
                # Calcular coincidencias de palabras
                palabras_pregunta = set(pregunta_lower.split())
                palabras_faq = set(pregunta_faq.split())
                
                # Buscar coincidencias en palabras importantes
                coincidencias_importantes = 0
                for palabra in palabras_clave:
                    if palabra in pregunta_lower and palabra in pregunta_faq:
                        coincidencias_importantes += 3  # Mayor peso
                
                # Buscar coincidencias generales
                coincidencias_generales = len(palabras_pregunta.intersection(palabras_faq))
                
                # Score total combinado
                score_total = (similitud_exacta * 10) + coincidencias_importantes + coincidencias_generales
                
                # Si hay buena coincidencia y es mejor que la anterior
                if score_total >= 5 and score_total > mejor_score:
                    mejor_score = score_total
                    mejor_resultado = {
                        "respuesta": faq.get("respuesta", ""),
                        "pregunta_original": faq.get("pregunta", ""),
                        "score": round(score_total, 2),
                        "similitud_exacta": round(similitud_exacta, 3)
                    }
            
            return mejor_resultado
            
        except Exception as e:
            print(f"Error en búsqueda Firebase: {e}")
            return None

# ------- API para agregar entradas al CSV de la base de conocimiento -----
class KnowledgeBaseAPIView(APIView):
    CSV_PATH = os.path.join("media", "docs", "basecsvf.csv")
    FIELDNAMES = ["id", "Pregunta", "Respuesta",
                  "Categoría", "fechaCreacion", "fechaModificacion"]

    # ---------- helpers ----------
    def _read_rows(self):
        """Devuelve la lista de dicts del CSV (vacía si no existe)."""
        if not os.path.exists(self.CSV_PATH):
            return []
        with open(self.CSV_PATH, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def _write_rows(self, rows):
        """Sobrescribe todo el CSV (encabezado incluido)."""
        with open(self.CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=self.FIELDNAMES)
            writer.writeheader()
            writer.writerows(rows)

    # ---------- GET collection ----------
    def get(self, request, entry_id=None):
        rows = self._read_rows()

        if entry_id is None:                       # /knowledge-base/
            return Response({"entries": rows}, status=200)

        # /knowledge-base/<id>/
        for row in rows:
            if row["id"] == str(entry_id):
                return Response(row)
        raise Http404("Entrada no encontrada")

    # ---------- POST create ----------
    def post(self, request):
        pregunta = request.data.get("pregunta", "").strip()
        respuesta = request.data.get("respuesta", "").strip()
        categoria = request.data.get("categoria", "").strip()

        if not pregunta or not respuesta:
            return Response(
                {"error": "Los campos 'pregunta' y 'respuesta' son obligatorios."},
                status=400,
            )

        rows = self._read_rows()
        next_id = (
            max([int(r["id"]) for r in rows] or [0]) + 1
        )  # ▼ auto-incremento ▼

        now = timezone.now().isoformat()

        new_row = {
            "id": str(next_id),
            "Pregunta": pregunta,
            "Respuesta": respuesta,
            "Categoría": categoria,
            "fechaCreacion": now,
            "fechaModificacion": "",
        }

        rows.append(new_row)
        self._write_rows(rows)

        return Response(new_row, status=201)

    # ---------- PUT update ----------
    def put(self, request, entry_id):
        rows = self._read_rows()
        updated = False
        now = timezone.now().isoformat()

        for row in rows:
            if row["id"] == str(entry_id):
                row["Pregunta"] = request.data.get("pregunta", row["Pregunta"]).strip()
                row["Respuesta"] = request.data.get("respuesta", row["Respuesta"]).strip()
                row["Categoría"] = request.data.get("categoria", row["Categoría"]).strip()
                row["fechaModificacion"] = now
                updated = True
                break

        if not updated:
            raise Http404("Entrada no encontrada")

        self._write_rows(rows)
        return Response(row)                       # la fila actualizada

    # ---------- DELETE ----------
    def delete(self, request, entry_id):
        rows = self._read_rows()
        new_rows = [r for r in rows if r["id"] != str(entry_id)]

        if len(new_rows) == len(rows):
            raise Http404("Entrada no encontrada")

        self._write_rows(new_rows)
        return Response({"message": "Entrada eliminada"})

class FAQManagementAPIView(APIView):
    """
    Endpoint protegido para agregar preguntas y respuestas al FAQ
    Requiere token de autorización: Bearer your-secure-token-here-change-in-production
    """
    authentication_classes = [FAQTokenAuthentication]
    permission_classes = [AllowAny]  # La autenticación se maneja en FAQTokenAuthentication
    
    def post(self, request):
        """
        Agregar nueva entrada al FAQ
        
        Body JSON:
        {
            "pregunta": "¿Cuál es el horario de atención?",
            "respuesta": "El horario de atención es de 8:00 a 17:00",
            "verificar_duplicados": true  # opcional, por defecto true
        }
        """
        serializer = FAQEntrySerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response({
                'error': 'Datos inválidos',
                'detalles': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        pregunta = serializer.validated_data['pregunta']
        respuesta = serializer.validated_data['respuesta']
        verificar_duplicados = request.data.get('verificar_duplicados', True)
        
        # Verificar duplicados si está habilitado
        if verificar_duplicados:
            duplicado_info = validar_faq_duplicado(pregunta)
            if duplicado_info['es_duplicado']:
                return Response({
                    'error': 'Pregunta duplicada detectada',
                    'pregunta_similar': duplicado_info['pregunta_similar'],
                    'similitud': duplicado_info['similitud'],
                    'sugerencia': 'Use forzar=true para agregar de todos modos'
                }, status=status.HTTP_409_CONFLICT)
        
        # Verificar si se está forzando a pesar de duplicados
        forzar = request.data.get('forzar', False)
        if not verificar_duplicados or not duplicado_info['es_duplicado'] or forzar:
            resultado = agregar_faq_entry(pregunta, respuesta)
            
            if resultado['success']:
                return Response({
                    'mensaje': 'FAQ agregado exitosamente',
                    'entrada': resultado['entrada'],
                    'estadisticas': obtener_estadisticas_faq()
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'error': 'Error al agregar FAQ',
                    'detalle': resultado['message']
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'error': 'Operación no permitida'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        """
        Obtener estadísticas del FAQ
        """
        estadisticas = obtener_estadisticas_faq()
        return Response({
            'estadisticas': estadisticas,
            'mensaje': 'Estadísticas del FAQ obtenidas exitosamente'
        }, status=status.HTTP_200_OK)


class FAQDuplicateCheckAPIView(APIView):
    """
    Endpoint protegido para verificar duplicados en el FAQ
    """
    authentication_classes = [FAQTokenAuthentication]
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Verificar si una pregunta ya existe en el FAQ
        
        Body JSON:
        {
            "pregunta": "¿Cuál es el horario?",
            "umbral_similitud": 0.8  # opcional, por defecto 0.8
        }
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
        
        resultado = validar_faq_duplicado(pregunta, umbral)
        
        return Response({
            'pregunta_consultada': pregunta,
            'umbral_usado': umbral,
            'es_duplicado': resultado['es_duplicado'],
            'pregunta_similar': resultado['pregunta_similar'],
            'similitud': resultado['similitud'],
            'recomendacion': 'No agregar' if resultado['es_duplicado'] else 'Puede agregar'
        }, status=status.HTTP_200_OK)

class ChatbotTestContextAPIView(APIView):
    """
    Endpoint para probar el filtrado de contexto
    """
    authentication_classes = [PublicAuthentication]
    permission_classes = [AllowAny]
    
    def post(self, request):
        pregunta = request.data.get("pregunta")
        if not pregunta:
            return Response({"error": "Falta el campo 'pregunta'"}, status=400)
        
        # Analizar la pregunta
        es_fuera_contexto = es_pregunta_fuera_contexto(pregunta)
        
        # Obtener documentos relevantes
        documentos = buscar_documentos(pregunta, top_k=3)
        
        # Calcular relevancia promedio
        relevancia_promedio = 0
        if documentos:
            for doc in documentos:
                score = similitud_texto(pregunta, doc.page_content[:200])
                relevancia_promedio += score
            relevancia_promedio /= len(documentos)
        
        return Response({
            "pregunta": pregunta,
            "es_fuera_contexto": es_fuera_contexto,
            "documentos_encontrados": len(documentos),
            "relevancia_promedio": round(relevancia_promedio, 3),
            "analisis": {
                "decision": "rechazar" if es_fuera_contexto else "procesar",
                "razon": "Pregunta fuera del contexto DCCO/ESPE" if es_fuera_contexto else "Pregunta válida para el contexto"
            }
        }, status=200)