# Filtrado de Contexto - Ejemplos de Uso

## Descripción
El sistema ahora incluye un filtrado inteligente que rechaza preguntas fuera del contexto del DCCO/ESPE y proporciona respuestas apropiadas.

## Casos de Uso

### ✅ PREGUNTAS ACEPTADAS (Dentro del contexto)

```json
{
  "pregunta": "¿Dónde está el departamento de computación?"
}
```
**Respuesta**: Información específica sobre la ubicación del DCCO.

```json
{
  "pregunta": "¿Qué carreras ofrece el DCCO?"
}
```
**Respuesta**: Lista de carreras disponibles en el departamento.

```json
{
  "pregunta": "¿Cuál es el horario de atención?"
}
```
**Respuesta**: Horarios específicos del departamento.

```json
{
  "pregunta": "¿Cómo me inscribo en una materia?"
}
```
**Respuesta**: Proceso de inscripción en materias.

### ❌ PREGUNTAS RECHAZADAS (Fuera del contexto)

```json
{
  "pregunta": "¿Quién es el presidente de Ecuador?"
}
```
**Respuesta**: 
```json
{
    "respuesta": "Lo siento, pero solo puedo ayudarte con preguntas relacionadas al Departamento de Ciencias de la Computación (DCCO) de la ESPE. ¿Hay algo específico sobre la universidad, carreras, materias o servicios estudiantiles en lo que pueda ayudarte?",
    "fuente": "sistema",
    "metodo": "fuera_de_contexto"
}
```

```json
{
  "pregunta": "¿Qué país es el más grande del mundo?"
}
```
**Respuesta**: Mensaje de filtrado indicando que solo responde preguntas del DCCO/ESPE.

```json
{
  "pregunta": "¿Qué hora es?"
}
```
**Respuesta**: Mensaje de filtrado redirigiendo al contexto universitario.

## Métodos de Filtrado

### 1. Detección Pre-procesamiento
- **Método**: `fuera_de_contexto`
- **Descripción**: La pregunta es rechazada antes de buscar documentos
- **Activación**: Palabras clave fuera del contexto académico

### 2. Validación de Relevancia
- **Método**: `sin_contexto_relevante`
- **Descripción**: No se encuentran documentos relevantes
- **Activación**: Relevancia promedio < 0.15

### 3. Validación de Respuesta
- **Método**: `respuesta_no_relevante`
- **Descripción**: La respuesta generada no es relevante
- **Activación**: Respuesta no contiene indicadores del DCCO/ESPE

### 4. LLM con Restricción
- **Método**: `llm_con_restriccion_contexto`
- **Descripción**: LLM con instrucciones específicas de contexto
- **Activación**: Fallback con validación adicional

## Palabras Clave de Contexto Válido

### Universidad/Institución
- espe, universidad, fuerzas armadas, militar, dcco
- departamento, computación, ciencias de la computación

### Académico
- carrera, materia, profesor, docente, estudiante
- clase, curso, syllabus, semestre, examen, tarea
- inscripción, matrícula, graduación, titulación

### Servicios Universitarios
- biblioteca, laboratorio, aula, secretaría
- coordinador, director, bienestar, psicólogo
- comedor, parqueo, beca, ayuda financiera

### Tecnología/Computación
- programación, software, hardware, algoritmo
- base de datos, redes, sistemas, ingeniería
- desarrollo, inteligencia artificial

## Temas Prohibidos

### Política
- presidente, gobierno, político, elecciones
- congreso, ministro, alcalde

### Geografía General
- país, capital, ciudad, continente, océano
- clima, temperatura, población

### Entretenimiento
- película, actor, cantante, música, deporte
- televisión, series, videojuego

### Tiempo/Fecha
- hora, tiempo, fecha, día, mes, año

## Endpoint de Prueba

```bash
POST /chatbot/test-context/
Content-Type: application/json

{
    "pregunta": "¿Quién es el presidente de Ecuador?"
}
```

**Respuesta**:
```json
{
    "pregunta": "¿Quién es el presidente de Ecuador?",
    "es_fuera_contexto": true,
    "documentos_encontrados": 0,
    "relevancia_promedio": 0.0,
    "analisis": {
        "decision": "rechazar",
        "razon": "Pregunta fuera del contexto DCCO/ESPE"
    }
}
```

## Configuración

### Umbrales de Relevancia
- **FAQ exacta**: ≥ 0.75
- **Contenido web/PDF**: ≥ 0.3
- **Relevancia mínima**: ≥ 0.15

### Respuestas Variadas
El sistema proporciona 4 diferentes respuestas de filtrado para evitar repetición:

1. "Lo siento, pero solo puedo ayudarte con preguntas relacionadas al DCCO..."
2. "Mi función es asistir con consultas relacionadas al DCCO y la ESPE..."
3. "Estoy diseñado para ayudarte específicamente con información del DCCO..."
4. "Solo puedo proporcionar información relacionada con el DCCO y la ESPE..."

## Monitoreo

Los métodos de respuesta incluyen información sobre cómo fue procesada la pregunta:
- `fuera_de_contexto`: Rechazada por filtro inicial
- `sin_contexto_relevante`: Sin documentos relevantes
- `respuesta_no_relevante`: Respuesta generada no relevante
- `llm_con_restriccion_contexto`: Procesada con restricciones
