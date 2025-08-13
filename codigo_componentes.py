#!/usr/bin/env python3
"""
CÓDIGO ESPECÍFICO: Componentes que resuelven preguntas no directas
"""

def mostrar_codigo_componentes():
    print("💻 CÓDIGO ESPECÍFICO: Componentes para preguntas no directas")
    print("=" * 70)
    print()
    
    print("1️⃣ DETECCIÓN INTELIGENTE (_es_pregunta_academica_valida)")
    print("   📍 Ubicación: views.py, líneas 474-542")
    print("   🎯 Función: Detecta si pregunta es académicamente válida")
    print()
    
    codigo_deteccion = '''
def _es_pregunta_academica_valida(self, pregunta):
    pregunta_lower = pregunta.lower().strip()
    
    # Palabras clave que indican claramente contexto académico DCCO/ESPE
    indicadores_academicos_fuertes = [
        "espe", "universidad de las fuerzas armadas", "campus sangolquí",
        "dcco", "departamento de ciencias de la computación",
        "aplicaciones basadas en el conocimiento", "aplicaciones distribuidas",
        "dónde queda la espe", "donde está la espe", "ubicación de la espe"
    ]
    
    # Combinaciones de palabras que indican contexto válido
    combinaciones_validas = [
        ["materia", "espe"], ["curso", "espe"], ["carrera", "espe"],
        ["aplicaciones", "conocimiento"], ["aplicaciones", "distribuidas"]
    ]
    
    # Patrones regex para preguntas académicas
    patrones_academicos = [
        r"(?:dónde|donde) (?:está|queda|se encuentra) .*(espe|universidad|campus)",
        r"(?:qué|que) (?:es|trata|significa) .*(espe|dcco|carrera|materia|curso)"
    ]
    '''
    
    print("📝 CÓDIGO EJEMPLO:")
    print(codigo_deteccion)
    print()
    
    print("2️⃣ VALIDACIÓN MEJORADA")
    print("   📍 Ubicación: views.py, líneas 688-693")
    print("   🎯 Función: Usa detección inteligente en validación")
    print()
    
    codigo_validacion = '''
# 8. Validar relevancia antes del fallback - MEJORADO para contexto académico
es_pregunta_academica_valida = self._es_pregunta_academica_valida(pregunta)
if not validar_relevancia_respuesta(pregunta, "", documentos) and not es_pregunta_academica_valida:
    return Response({
        "respuesta": generar_respuesta_fuera_contexto(),
        "metodo": "sin_contexto_relevante"
    })
    '''
    
    print("📝 CÓDIGO EJEMPLO:")
    print(codigo_validacion)
    print()
    
    print("3️⃣ PROMPT INTELIGENTE CON CONOCIMIENTO BASE")
    print("   📍 Ubicación: views.py, líneas 697-734")
    print("   🎯 Función: Prompt especializado con conocimiento del DCCO")
    print()
    
    codigo_prompt = '''
prompt_inteligente = f"""Eres un asistente académico especializado del DCCO de la ESPE.

INFORMACIÓN INSTITUCIONAL QUE CONOCES:
- Universidad: ESPE (Universidad de las Fuerzas Armadas)
- Departamento: DCCO (Departamento de Ciencias de la Computación)
- Ubicación: Campus Sangolquí, Ecuador

CARRERAS DEL DCCO:
- Ingeniería en Software
- Tecnologías de la Información  
- Sistemas de Información
- Ciencias de la Computación

MATERIAS DESTACADAS:
- Aplicaciones Basadas en el Conocimiento (sistemas expertos, IA, minería de datos)
- Aplicaciones Distribuidas (sistemas distribuidos, microservicios)

DIRECTORES CONOCIDOS:
- Director de Carrera de Software: Ing. Mauricio Campaña

PREGUNTA DEL ESTUDIANTE: {pregunta}
RESPUESTA (específica y útil):"""
    '''
    
    print("📝 CÓDIGO EJEMPLO:")
    print(codigo_prompt)
    print()
    
    print("4️⃣ PROCESAMIENTO CON OPENAI")
    print("   📍 Ubicación: views.py, líneas 735-755")
    print("   🎯 Función: Usa OpenAI con prompt inteligente")
    print()
    
    codigo_procesamiento = '''
respuesta_fallback = consultar_llm_inteligente(prompt_inteligente)
if respuesta_fallback is not None:
    metodo = "llm_academico_inteligente"
else:
    # Fallback si OpenAI falla
    metodo = "contenido_directo"

return Response({
    "respuesta": respuesta_fallback,
    "fuente": "LLM Académico",
    "metodo": metodo
})
    '''
    
    print("📝 CÓDIGO EJEMPLO:")
    print(codigo_procesamiento)
    print()
    
    print("🔍 FLUJO LÓGICO EN EL CÓDIGO:")
    print()
    print("1. Firebase RAG busca → No encuentra")
    print("2. Vector store busca → Similitud baja")
    print("3. _es_pregunta_academica_valida() → TRUE")
    print("4. prompt_inteligente con conocimiento base")
    print("5. consultar_llm_inteligente() → OpenAI procesa")
    print("6. Respuesta útil con método 'llm_academico_inteligente'")
    print()
    
    print("✅ RESULTADO:")
    print("   El sistema NO depende solo de Firebase/documentos")
    print("   Usa INTELIGENCIA + CONOCIMIENTO BASE + OpenAI")
    print("   para responder preguntas académicas válidas")

if __name__ == "__main__":
    mostrar_codigo_componentes()
