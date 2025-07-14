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

from .vector_store import buscar_documentos
from .serializers import FAQEntrySerializer, ChatbotQuerySerializer
from .authentication import FAQTokenAuthentication, PublicAuthentication
from .document_loader import agregar_faq_entry, validar_faq_duplicado, obtener_estadisticas_faq

import logging

logger = logging.getLogger(__name__)

# API mejorada que maneja correctamente las respuestas del CSV
# Función para calcular similitud entre textos
OPENAI_API_KEY = "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"  # Pega aquí tu clave real

# --------- FUNCIONES AUXILIARES ---------

def similitud_texto(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def consultar_openai(prompt):
    """
    Llama a OpenAI (GPT-3.5) con un prompt.
    """
    endpoint = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
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
        return f"[Error {response.status_code}] {response.text}"

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

        # 1. Intenciones básicas
        intencion = self.detectar_intencion(pregunta)
        if intencion:
            return Response({
                "respuesta": self.RESPUESTAS_BASICAS[intencion],
                "fuente": "sistema",
                "metodo": "intencion_basica"
            }, status=200)
        try:
            documentos = buscar_documentos(pregunta, top_k=5)

            # 2. Buscar coincidencia exacta en FAQs
            for doc in documentos:
                if doc.metadata.get("source") == "faq":
                    score = similitud_texto(pregunta, doc.metadata.get("pregunta_original", ""))
                    if score >= 0.75:
                        respuesta_base = doc.metadata["respuesta_original"]
                        prompt = f"""La siguiente es una posible respuesta basada en una FAQ de la ESPE:

Respuesta base:
{respuesta_base}

Por favor, reformúlala si es necesario para que suene más natural y completa para el usuario que preguntó:

{pregunta}

Respuesta:"""
                        respuesta_mejorada = consultar_openai(prompt)
                        return Response({
                            "respuesta": respuesta_mejorada,
                            "pregunta_relacionada": doc.metadata["pregunta_original"],
                            "fuente": "FAQ",
                            "metodo": "faq_reformulada",
                            "similitud": round(score, 3)
                        }, status=200)

            # 3. Buscar mejor contenido en web/pdf
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
                respuesta_llm = consultar_openai(prompt)
                return Response({
                    "respuesta": respuesta_llm,
                    "fuente": mejor_doc.metadata.get("source", "web"),
                    "titulo": mejor_doc.metadata.get("titulo", ""),
                    "metodo": "web_llm_refinado",
                    "similitud": round(mejor_score, 3)
                }, status=200)

            # 4. Último recurso: pasar todo el contexto al LLM
            contexto_general = "\n\n".join([doc.page_content[:400] for doc in documentos])
            prompt = f"""Responde la siguiente pregunta del usuario usando la información disponible.

Contexto:
{contexto_general}

Pregunta:
{pregunta}

Respuesta:"""
            respuesta_fallback = consultar_openai(prompt)
            return Response({
                "respuesta": respuesta_fallback,
                "fuente": "LLM",
                "metodo": "llm_sin_respuesta_base"
            }, status=200)

        except Exception as e:
            return Response({
                "error": "Error interno del servidor",
                "detalle": str(e)
            }, status=500)

# Versión alternativa con búsqueda híbrida
class ChatbotHibridoAPIView(APIView):
    """
    Búsqueda híbrida: exacta + semántica
    """
    def busqueda_exacta_csv(self, pregunta):
        """
        Busca coincidencias exactas de palabras clave en el CSV
        """
        import pandas as pd
        import os
        
        csv_path = os.path.join("media", "docs", "basecsvf.csv")
        if not os.path.exists(csv_path):
            return None
            
        df = pd.read_csv(csv_path)
        df = df.dropna(subset=["Pregunta", "Respuesta"])
        
        pregunta_lower = pregunta.lower()
        
        # Buscar palabras clave importantes
        palabras_clave = ["psicólogo", "psicóloga", "bienestar", "bar", "comedor", 
                         "departamento", "computación", "biblioteca", "parqueo", 
                         "secretaria", "coordinador"]
        
        for _, row in df.iterrows():
            pregunta_csv = row["Pregunta"].lower()
            
            # Calcular similitud por palabras clave
            palabras_pregunta = set(pregunta_lower.split())
            palabras_csv = set(pregunta_csv.split())
            
            # Buscar coincidencias en palabras importantes
            coincidencias_importantes = 0
            for palabra in palabras_clave:
                if palabra in pregunta_lower and palabra in pregunta_csv:
                    coincidencias_importantes += 2
            
            # Buscar coincidencias generales
            coincidencias_generales = len(palabras_pregunta.intersection(palabras_csv))
            
            score_total = coincidencias_importantes + coincidencias_generales
            
            # Si hay buena coincidencia, devolver la respuesta
            if score_total >= 2:
                return {
                    "respuesta": row["Respuesta"],
                    "pregunta_original": row["Pregunta"],
                    "score": score_total
                }
        
        return None

    def post(self, request):
        pregunta = request.data.get("pregunta")
        if not pregunta:
            return Response({"error": "Falta el campo 'pregunta'"}, status=400)

        try:
            # 1. Intentar búsqueda exacta primero
            resultado_exacto = self.busqueda_exacta_csv(pregunta)
            
            if resultado_exacto:
                return Response({
                    "respuesta": resultado_exacto["respuesta"],
                    "pregunta_relacionada": resultado_exacto["pregunta_original"],
                    "fuente": "FAQ",
                    "metodo": "busqueda_exacta",
                    "score": resultado_exacto["score"]
                }, status=200)
            
            # 2. Si no hay coincidencia exacta, usar búsqueda semántica
            documentos = buscar_documentos(pregunta, top_k=3)
            
            if documentos:
                doc = documentos[0]
                
                # Si es del CSV
                if doc.metadata.get("source") == "faq":
                    if "respuesta_original" in doc.metadata:
                        respuesta = doc.metadata["respuesta_original"]
                    elif "Respuesta:" in doc.page_content:
                        respuesta = doc.page_content.split("Respuesta:")[-1].strip()
                    else:
                        respuesta = doc.page_content
                    
                    return Response({
                        "respuesta": respuesta,
                        "fuente": "FAQ",
                        "metodo": "busqueda_semantica"
                    }, status=200)
                else:
                    # Es de PDF
                    respuesta = doc.page_content[:400]
                    if len(doc.page_content) > 400:
                        respuesta += "..."
                    
                    return Response({
                        "respuesta": respuesta,
                        "fuente": doc.metadata.get("source", "PDF"),
                        "metodo": "documento_pdf"
                    }, status=200)
            
            return Response({
                "respuesta": "No encontré información relevante para tu pregunta."
            }, status=200)
            
        except Exception as e:
            return Response({
                "error": "Error interno del servidor",
                "detalle": str(e)
            }, status=500)

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