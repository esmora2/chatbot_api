from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
import re

from .vector_store import buscar_documentos

# API mejorada que maneja correctamente las respuestas del CSV
class ChatbotAPIView(APIView):
    def post(self, request):
        pregunta = request.data.get("pregunta")
        if not pregunta:
            return Response({"error": "Falta el campo 'pregunta'"}, status=400)

        try:
            # Buscar documentos relevantes
            documentos = buscar_documentos(pregunta, top_k=5)  # Buscar más documentos
            
            if not documentos:
                return Response({
                    "respuesta": "No encontré información relevante para tu pregunta."
                }, status=200)
            
            # Priorizar documentos del CSV
            mejor_respuesta = None
            mejor_score = 0
            
            for doc in documentos:
                if doc.metadata.get("source") == "faq":
                    # Si tenemos la respuesta original en metadata, usarla
                    if "respuesta_original" in doc.metadata:
                        return Response({
                            "respuesta": doc.metadata["respuesta_original"],
                            "pregunta_relacionada": doc.metadata.get("pregunta_original", ""),
                            "fuente": "FAQ",
                            "metodo": "csv_directo"
                        }, status=200)
                    
                    # Si no, extraer de page_content
                    if "Respuesta:" in doc.page_content:
                        respuesta_extraida = doc.page_content.split("Respuesta:")[-1].strip()
                        return Response({
                            "respuesta": respuesta_extraida,
                            "fuente": "FAQ",
                            "metodo": "csv_extraido"
                        }, status=200)
            
            # Si no hay documentos CSV, usar el más relevante
            doc_relevante = documentos[0]
            respuesta = doc_relevante.page_content[:400]
            if len(doc_relevante.page_content) > 400:
                respuesta += "..."
            
            return Response({
                "respuesta": respuesta,
                "fuente": doc_relevante.metadata.get("source", "PDF"),
                "documentos_encontrados": len(documentos),
                "metodo": "documento_general"
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