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
