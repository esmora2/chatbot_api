from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

from .vector_store import buscar_documentos  # Importa desde vector_store.py

# Función para consultar Hugging Face (puedes cambiar a Ollama si quieres)
def consultar_llama(prompt):
    token = "Bearer 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"
    endpoint = "https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta"

    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    data = {
        "inputs": prompt
    }

    response = requests.post(endpoint, headers=headers, json=data)
    
    if response.status_code == 200:
        return response.json()[0]["generated_text"].strip()
    else:
        return f"[Error {response.status_code}] {response.text}"

# API REST del chatbot
class ChatbotAPIView(APIView):
    def post(self, request):
        pregunta = request.data.get("pregunta")
        if not pregunta:
            return Response({"error": "Falta el campo 'pregunta'"}, status=400)

        # Buscar contexto en base de conocimiento
        documentos = buscar_documentos(pregunta)
        contexto = "\n\n".join([doc.page_content for doc in documentos])

        # Construir prompt con contexto real
        prompt = f"""Eres un asistente académico del Departamento de Ciencias de la Computación de la ESPE.
Responde a la siguiente pregunta utilizando únicamente la información proporcionada a continuación.

Contexto:
{contexto}

Pregunta:
{pregunta}

Respuesta:"""
        
        respuesta = consultar_llama(prompt)
        return Response({"respuesta": respuesta}, status=200)
