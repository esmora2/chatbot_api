# API de Gestión de FAQ - Documentación

## Endpoints Protegidos para Gestión de FAQ

El sistema incluye endpoints protegidos que permiten agregar y gestionar preguntas y respuestas en el archivo CSV del FAQ.

### Autenticación

Todos los endpoints de gestión de FAQ requieren un token de autorización en el header:

```
Authorization: Bearer your-secure-token-here-change-in-production
```

**⚠️ IMPORTANTE**: Cambia el token en `settings.py` antes de usar en producción.

### Endpoints Disponibles

#### 1. Agregar Nueva Entrada al FAQ

**POST** `/chatbot/faq/manage/`

Agrega una nueva pregunta y respuesta al archivo FAQ.

**Headers:**
```
Content-Type: application/json
Authorization: Bearer your-secure-token-here-change-in-production
```

**Body:**
```json
{
    "pregunta": "¿Cuál es el horario de atención del departamento?",
    "respuesta": "El horario de atención es de lunes a viernes de 8:00 a 17:00",
    "verificar_duplicados": true,  // opcional, por defecto true
    "forzar": false  // opcional, para forzar agregar aunque haya duplicados
}
```

**Respuesta Exitosa (201):**
```json
{
    "mensaje": "FAQ agregado exitosamente",
    "entrada": {
        "Pregunta": "¿Cuál es el horario de atención del departamento?",
        "Respuesta": "El horario de atención es de lunes a viernes de 8:00 a 17:00",
        "Fecha_Agregado": "2025-07-14 15:30:45"
    },
    "estadisticas": {
        "total_preguntas": 15,
        "archivo_existe": true,
        "tamaño_archivo": 2048,
        "ultima_modificacion": "2025-07-14 15:30:45"
    }
}
```

**Respuesta de Duplicado (409):**
```json
{
    "error": "Pregunta duplicada detectada",
    "pregunta_similar": "¿Cuál es el horario de atención?",
    "similitud": 0.85,
    "sugerencia": "Use forzar=true para agregar de todos modos"
}
```

#### 2. Obtener Estadísticas del FAQ

**GET** `/chatbot/faq/manage/`

Obtiene estadísticas básicas del archivo FAQ.

**Headers:**
```
Authorization: Bearer your-secure-token-here-change-in-production
```

**Respuesta (200):**
```json
{
    "estadisticas": {
        "total_preguntas": 15,
        "archivo_existe": true,
        "tamaño_archivo": 2048,
        "ultima_modificacion": "2025-07-14 15:30:45"
    },
    "mensaje": "Estadísticas del FAQ obtenidas exitosamente"
}
```

#### 3. Verificar Duplicados

**POST** `/chatbot/faq/check-duplicate/`

Verifica si una pregunta ya existe en el FAQ sin agregarla.

**Headers:**
```
Content-Type: application/json
Authorization: Bearer your-secure-token-here-change-in-production
```

**Body:**
```json
{
    "pregunta": "¿Cuál es el horario?",
    "umbral_similitud": 0.8  // opcional, por defecto 0.8
}
```

**Respuesta (200):**
```json
{
    "pregunta_consultada": "¿Cuál es el horario?",
    "umbral_usado": 0.8,
    "es_duplicado": true,
    "pregunta_similar": "¿Cuál es el horario de atención?",
    "similitud": 0.85,
    "recomendacion": "No agregar"
}
```

### Endpoint Público (Sin Autenticación)

#### Consultar Chatbot

**POST** `/chatbot/chatbot/`

Este endpoint permanece público y no requiere autenticación.

**Body:**
```json
{
    "pregunta": "¿Cuáles son los horarios de atención?"
}
```

## Códigos de Error

- **400**: Datos inválidos o faltantes
- **401**: Token de autorización faltante o inválido
- **409**: Pregunta duplicada detectada
- **500**: Error interno del servidor

## Configuración de Seguridad

### Cambiar el Token de Producción

En `chatbot_api/settings.py`, modifica:

```python
FAQ_MANAGEMENT_TOKEN = 'tu-token-super-seguro-aqui'
```

### Generar un Token Seguro

Puedes generar un token seguro usando Python:

```python
import secrets
token = secrets.token_urlsafe(32)
print(f"Tu nuevo token: {token}")
```

## Validaciones

### Pregunta
- Mínimo 5 caracteres
- No puede estar vacía
- Se elimina whitespace automáticamente

### Respuesta
- Mínimo 10 caracteres
- No puede estar vacía
- Se elimina whitespace automáticamente

### Detección de Duplicados
- Usa algoritmo de similitud de secuencias
- Umbral por defecto: 0.8 (80% de similitud)
- Configurable por petición

## Ejemplos de Uso

### Ejemplo con cURL

```bash
# Agregar FAQ
curl -X POST "http://localhost:8000/chatbot/faq/manage/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secure-token-here-change-in-production" \
  -d '{
    "pregunta": "¿Cómo puedo contactar al departamento?",
    "respuesta": "Puede contactarnos al teléfono 123-456-7890 o por email a dcco@espe.edu.ec"
  }'

# Verificar duplicados
curl -X POST "http://localhost:8000/chatbot/faq/check-duplicate/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your-secure-token-here-change-in-production" \
  -d '{
    "pregunta": "¿Cómo contactar?",
    "umbral_similitud": 0.7
  }'

# Obtener estadísticas
curl -X GET "http://localhost:8000/chatbot/faq/manage/" \
  -H "Authorization: Bearer your-secure-token-here-change-in-production"
```

### Ejemplo con JavaScript/Fetch

```javascript
const token = 'your-secure-token-here-change-in-production';
const baseUrl = 'http://localhost:8000/chatbot';

// Agregar FAQ
async function agregarFAQ(pregunta, respuesta) {
    const response = await fetch(`${baseUrl}/faq/manage/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
            pregunta: pregunta,
            respuesta: respuesta,
            verificar_duplicados: true
        })
    });
    
    return await response.json();
}

// Usar función
agregarFAQ(
    "¿Cuándo abren las inscripciones?",
    "Las inscripciones abren en febrero para el período académico de abril"
).then(resultado => {
    console.log('FAQ agregado:', resultado);
}).catch(error => {
    console.error('Error:', error);
});
```

## Estructura del Archivo CSV

El archivo `media/docs/basecsvf.csv` tendrá la siguiente estructura:

```csv
Pregunta,Respuesta,Fecha_Agregado
"¿Cuál es el horario de atención?","Lunes a viernes de 8:00 a 17:00","2025-07-14 15:30:45"
"¿Cómo puedo contactar al departamento?","Teléfono: 123-456-7890, Email: dcco@espe.edu.ec","2025-07-14 16:45:20"
```

## Logs y Monitoreo

El sistema registra todas las operaciones en el log de Django:

- Agregado exitoso de FAQ
- Errores al procesar
- Validaciones de duplicados
- Errores de autenticación
