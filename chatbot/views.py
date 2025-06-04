from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import re
import time

from .vector_store import buscar_documentos

# SOLUCIÓN 1: Alternativa con modelo gratuito diferente
def consultar_llama_alternativo(prompt):
    """
    Usa un modelo completamente gratuito sin límites
    """
    token = "Bearer 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"
    # Modelo alternativo gratuito
    endpoint = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
    
    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    
    data = {
        "inputs": prompt,
        "parameters": {
            "max_length": 300,
            "temperature": 0.7,
            "do_sample": True,
            "return_full_text": False
        }
    }

    try:
        response = requests.post(endpoint, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "").strip()
            else:
                return ""
        elif response.status_code == 503:
            # Modelo cargándose, esperar y reintentar
            time.sleep(2)
            return "El modelo está cargándose, intenta nuevamente en unos segundos."
        else:
            return f"Error en API: {response.status_code}"
            
    except Exception as e:
        return f"Error de conexión: {str(e)}"

# SOLUCIÓN 2: Respuesta directa sin LLM
def generar_respuesta_directa(contexto, pregunta):
    """
    Genera respuesta basada en coincidencias simples sin usar LLM
    """
    # Búsqueda de palabras clave en el contexto
    pregunta_lower = pregunta.lower()
    contexto_lower = contexto.lower()
    
    # Extraer la oración más relevante
    oraciones = contexto.split('.')
    mejor_oracion = ""
    mejor_score = 0
    
    for oracion in oraciones:
        oracion = oracion.strip()
        if len(oracion) < 10:
            continue
            
        # Contar palabras en común
        palabras_pregunta = set(pregunta_lower.split())
        palabras_oracion = set(oracion.lower().split())
        coincidencias = len(palabras_pregunta.intersection(palabras_oracion))
        
        if coincidencias > mejor_score:
            mejor_score = coincidencias
            mejor_oracion = oracion
    
    return mejor_oracion if mejor_oracion else contexto[:200] + "..."

# SOLUCIÓN 3: API mejorada con fallbacks
class ChatbotAPIView(APIView):
    def post(self, request):
        pregunta = request.data.get("pregunta")
        if not pregunta:
            return Response({"error": "Falta el campo 'pregunta'"}, status=400)

        try:
            # Buscar contexto en base de conocimiento
            documentos = buscar_documentos(pregunta, top_k=2)
            
            if not documentos:
                return Response({
                    "respuesta": "No encontré información relevante para tu pregunta.",
                    "metodo": "sin_documentos"
                }, status=200)
            
            # Preparar contexto
            contexto_partes = []
            for doc in documentos:
                contenido = doc.page_content[:300]
                if len(doc.page_content) > 300:
                    contenido += "..."
                contexto_partes.append(contenido)
            
            contexto = "\n\n".join(contexto_partes)
            
            # Verificar si es del CSV (respuesta directa)
            if documentos[0].metadata.get("source") == "faq":
                return Response({
                    "respuesta": documentos[0].page_content,
                    "fuente": "faq",
                    "metodo": "respuesta_directa"
                }, status=200)
            
            # Intentar con LLM alternativo
            prompt = f"Pregunta: {pregunta}\nContexto: {contexto[:400]}\nRespuesta breve:"
            respuesta_llm = consultar_llama_alternativo(prompt)
            
            # Si falla el LLM, usar respuesta directa
            if "Error" in respuesta_llm or len(respuesta_llm.strip()) < 10:
                respuesta = generar_respuesta_directa(contexto, pregunta)
                metodo = "respuesta_directa_fallback"
            else:
                respuesta = respuesta_llm
                metodo = "llm_alternativo"
            
            return Response({
                "respuesta": respuesta,
                "documentos_encontrados": len(documentos),
                "metodo": metodo
            }, status=200)
            
        except Exception as e:
            return Response({
                "error": "Error interno del servidor",
                "detalle": str(e)
            }, status=500)

# SOLUCIÓN 4: Solo respuestas directas (sin LLM)
class ChatbotDirectoAPIView(APIView):
    """
    Versión que NO usa LLM, solo búsqueda directa en documentos
    """
    def post(self, request):
        pregunta = request.data.get("pregunta")
        if not pregunta:
            return Response({"error": "Falta el campo 'pregunta'"}, status=400)

        try:
            # Buscar documentos relevantes
            documentos = buscar_documentos(pregunta, top_k=3)
            
            if not documentos:
                return Response({
                    "respuesta": "No encontré información relevante para tu pregunta."
                }, status=200)
            
            # Priorizar respuestas del CSV
            respuesta_csv = None
            for doc in documentos:
                if doc.metadata.get("source") == "faq":
                    respuesta_csv = doc.page_content
                    break
            
            if respuesta_csv:
                # Usar respuesta del CSV
                respuesta = respuesta_csv
                fuente = "FAQ"
            else:
                # Usar el documento más relevante
                respuesta = documentos[0].page_content[:400]
                if len(documentos[0].page_content) > 400:
                    respuesta += "..."
                fuente = documentos[0].metadata.get("source", "PDF")
            
            return Response({
                "respuesta": respuesta,
                "fuente": fuente,
                "documentos_encontrados": len(documentos),
                "metodo": "busqueda_directa"
            }, status=200)
            
        except Exception as e:
            return Response({
                "error": "Error interno del servidor"
            }, status=500)

# SOLUCIÓN 5: Uso de OpenAI (si tienes API key)
def consultar_openai(prompt):
    """
    Alternativa usando OpenAI (requiere API key)
    """
    import openai
    
    try:
        # Configurar tu API key de OpenAI
        openai.api_key = "tu-api-key-aqui"  # Reemplazar con tu key
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un asistente académico. Responde de forma concisa."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            temperature=0.3
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"Error con OpenAI: {str(e)}"

# SOLUCIÓN 6: Usar Ollama local (si está instalado)
def consultar_ollama(prompt):
    """
    Alternativa usando Ollama local
    """
    try:
        import ollama
        
        response = ollama.chat(model='llama2', messages=[
            {
                'role': 'user',
                'content': prompt,
            },
        ])
        
        return response['message']['content']
        
    except Exception as e:
        return f"Error con Ollama: {str(e)}"