from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from difflib import SequenceMatcher
import re

from .vector_store import buscar_documentos

# API mejorada que maneja correctamente las respuestas del CSV
def similitud_texto(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

class ChatbotAPIView(APIView):
    # Añadir estas constantes para intenciones básicas
    INTENCIONES_BASICAS = {
        "saludos": ["hola", "buenos días", "buenos dias", "buenas tardes", "hi", "hello"],
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
        # 1. Manejar intenciones básicas primero
        intencion = self.detectar_intencion(pregunta)
        if intencion:
            return Response({
                "respuesta": self.RESPUESTAS_BASICAS[intencion],
                "fuente": "sistema",
                "metodo": "intencion_basica"
            }, status=200)
        try:
            documentos = buscar_documentos(pregunta, top_k=5)
            if not documentos:
                return Response({"respuesta": "No encontré información relevante para tu pregunta."}, status=200)

            # 2. Búsqueda en FAQs con umbral estricto
            mejor_doc_faq = None
            mejor_score_faq = 0

            for doc in documentos:
                if doc.metadata.get("source") == "faq":
                    pregunta_csv = doc.metadata.get("pregunta_original", "")
                    score = similitud_texto(pregunta, pregunta_csv)
                    if score > mejor_score_faq:
                        mejor_doc_faq = doc
                        mejor_score_faq = score

            if mejor_doc_faq and mejor_score_faq >= 0.75:
                return Response({
                    "respuesta": mejor_doc_faq.metadata["respuesta_original"],
                    "pregunta_relacionada": mejor_doc_faq.metadata["pregunta_original"],
                    "fuente": "FAQ",
                    "metodo": "faq_similitud_validada",
                    "similitud": round(mejor_score_faq, 3)
                }, status=200)

            # 3. Búsqueda en otros documentos con umbral mínimo
            mejor_doc_general = None
            mejor_score_general = 0
            umbral_minimo = 0.25  # Ajustar según necesidad

            for doc in documentos:
                if doc.metadata.get("source") != "faq":
                    # Calcular similitud con el contenido del documento
                    score = similitud_texto(pregunta, doc.page_content[:100])  # Comparar con inicio del contenido
                    if score > mejor_score_general:
                        mejor_doc_general = doc
                        mejor_score_general = score

            if mejor_doc_general and mejor_score_general >= umbral_minimo:
                respuesta = mejor_doc_general.page_content[:400]
                if len(mejor_doc_general.page_content) > 400:
                    respuesta += "..."
                return Response({
                    "respuesta": respuesta,
                    "fuente": mejor_doc_general.metadata.get("source", "desconocido"),
                    "titulo": mejor_doc_general.metadata.get("titulo", ""),
                    "metodo": mejor_doc_general.metadata.get("tipo", "documento"),
                    "similitud": round(mejor_score_general, 3)
                }, status=200)

            # 4. Si no hay coincidencias válidas
            return Response({
                "respuesta": "No encontré información relevante para tu pregunta. ¿Podrías reformularla o ser más específico?",
                "fuente": "sistema",
                "metodo": "sin_coincidencias_validas"
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
