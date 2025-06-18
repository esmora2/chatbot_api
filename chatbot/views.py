from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from difflib import SequenceMatcher
import re
import requests

from .vector_store import buscar_documentos

# API mejorada que maneja correctamente las respuestas del CSV
# Función para calcular similitud entre textos
def similitud_texto(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def consultar_llm_mistral(prompt):
    token = "Bearer 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"  # Asegúrate de que tu token aún esté válido
    endpoint = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1"

    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    data = {
        "inputs": prompt
    }

    response = requests.post(endpoint, headers=headers, json=data)

    if response.status_code == 200:
        respuesta_json = response.json()
        if isinstance(respuesta_json, list):
            return respuesta_json[0]["generated_text"].strip()
        elif "generated_text" in respuesta_json:
            return respuesta_json["generated_text"].strip()
        else:
            return "[Error] Formato de respuesta desconocido"
    else:
        return f"[Error {response.status_code}] {response.text}"

# -------------------------
# VISTA PRINCIPAL DEL CHATBOT
# -------------------------

class ChatbotAPIView(APIView):
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

            # 1. Si encuentra una FAQ similar
            for doc in documentos:
                if doc.metadata.get("source") == "faq":
                    score = similitud_texto(pregunta, doc.metadata.get("pregunta_original", ""))
                    if score >= 0.75:
                        return Response({
                            "respuesta": doc.metadata["respuesta_original"],
                            "pregunta_relacionada": doc.metadata["pregunta_original"],
                            "fuente": "FAQ",
                            "metodo": "faq_similitud_validada",
                            "similitud": round(score, 3)
                        }, status=200)

            # 2. Buscar en web/pdf con LLM como refuerzo
            contexto = "\n\n".join([doc.page_content[:500] for doc in documentos])
            prompt = f"""Eres un asistente académico del Departamento de Ciencias de la Computación de la ESPE.
Responde a la siguiente pregunta utilizando solamente la siguiente información:

Contexto:
{contexto}

Pregunta:
{pregunta}

Respuesta:"""

            respuesta_llm = consultar_llm_mistral(prompt)
            return Response({
                "respuesta": respuesta_llm,
                "fuente": "LLM",
                "metodo": "llm_mistral"
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