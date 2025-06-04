from rest_framework.views import APIView
from rest_framework.response import Response
import requests
from .vector_store import buscar_documentos

def consultar_llama(prompt):
    token = "Bearer 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"
    endpoint = "https://api-inference.huggingface.co/models/tiiuae/falcon-7b-instruct"

    headers = {
        "Authorization": token,
        "Content-Type": "application/json"
    }
    data = {"inputs": prompt}

    try:
        response = requests.post(endpoint, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        result = response.json()
        return result[0]["generated_text"].strip()
    except Exception as e:
        return f"[Error] {str(e)}"

class ChatbotAPIView(APIView):
    def post(self, request):
        pregunta = request.data.get("pregunta")
        if not pregunta:
            return Response({"error": "Falta el campo 'pregunta'"}, status=400)

        documentos = buscar_documentos(pregunta)
        if not documentos:
            return Response({"respuesta": "No se encuentra información suficiente para responder con certeza."})

        contexto = "\n".join([doc.page_content for doc in documentos])[:1000]

        prompt = f"""Responde como un asistente académico experto de la ESPE.

Tu única fuente de información es el siguiente CONTEXTO.
No puedes inventar datos. Si no hay información en el contexto, responde:
"No se encuentra información suficiente para responder con certeza".

=== CONTEXTO ===
{contexto}
================

Pregunta: {pregunta}
Respuesta:"""

        respuesta = consultar_llama(prompt)
        return Response({"respuesta": respuesta})
