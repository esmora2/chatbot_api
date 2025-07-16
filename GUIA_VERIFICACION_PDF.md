# Guía de Verificación del PDF: espe_software_aplicaciones_basadas_en_el_conocimiento.pdf

## 🎯 Objetivo
Verificar que el PDF del syllabus de "Aplicaciones Basadas en el Conocimiento" se carga correctamente y funciona en el chatbot.

## 📋 Pasos de Verificación

### 1. **Verificar que el archivo existe**
```bash
# Verifica que el archivo está en la ubicación correcta
ls -la media/docs/espe_software_aplicaciones_basadas_en_el_conocimiento.pdf
```

### 2. **Verificar carga de documentos**
```bash
# Ejecuta el endpoint de verificación
curl -X GET http://localhost:8000/chatbot/docs/check/
```

**Respuesta esperada:**
```json
{
    "documentos_totales": 150,
    "faq_count": 45,
    "web_count": 30,
    "pdf_count": 75,
    "pdfs_detectados": [
        "espe_software_aplicaciones_basadas_en_el_conocimiento.pdf",
        "otro_syllabus.pdf"
    ],
    "pdf_especifico": {
        "nombre": "espe_software_aplicaciones_basadas_en_el_conocimiento.pdf",
        "chunks": 15,
        "encontrado": true
    }
}
```

### 3. **Probar búsqueda específica**
```bash
# Ejecuta el script de prueba
python test_pdf_simple.py
```

### 4. **Verificación manual con el chatbot**

#### **Preguntas que DEBERÍAN funcionar:**
```json
{
  "pregunta": "¿Qué es aplicaciones basadas en el conocimiento?"
}
```

#### **Preguntas específicas del syllabus:**
```json
{
  "pregunta": "¿Cuál es el contenido de la materia de aplicaciones basadas en el conocimiento?"
}
```

```json
{
  "pregunta": "¿Cuáles son los objetivos de aplicaciones basadas en el conocimiento?"
}
```

```json
{
  "pregunta": "¿Qué metodología se usa en aplicaciones basadas en el conocimiento?"
}
```

## 🔍 Indicadores de que el PDF está funcionando

### ✅ **Señales POSITIVAS:**
- **Chunks detectados**: `pdf_especifico.chunks > 0`
- **Respuestas específicas**: El chatbot responde con información del syllabus
- **Fuente correcta**: Las respuestas indican fuente "pdf" o "Contenido"
- **Contenido relevante**: Menciona temas específicos del syllabus

### ❌ **Señales de PROBLEMAS:**
- **Sin chunks**: `pdf_especifico.chunks = 0`
- **Respuestas genéricas**: El chatbot responde con información general
- **Fuente incorrecta**: Las respuestas vienen solo de "FAQ" o "LLM"
- **Método fallback**: `metodo = "llm_sin_respuesta_base"`

## 🔧 Solución de Problemas

### **Si el PDF no se detecta:**

1. **Verificar ubicación:**
   ```bash
   # Debe estar en esta ruta exacta
   media/docs/espe_software_aplicaciones_basadas_en_el_conocimiento.pdf
   ```

2. **Verificar permisos:**
   ```bash
   # Asegúrate de que el archivo sea legible
   chmod 644 media/docs/espe_software_aplicaciones_basadas_en_el_conocimiento.pdf
   ```

3. **Verificar contenido:**
   ```bash
   # Ejecuta el verificador detallado
   python verificar_pdf.py
   ```

4. **Reiniciar servidor:**
   ```bash
   # Los documentos se cargan al iniciar
   python manage.py runserver
   ```

### **Si el PDF se detecta pero no responde:**

1. **Verificar contenido del PDF:**
   - El PDF debe tener texto extraíble (no solo imágenes)
   - El contenido debe ser en español
   - Debe tener información relevante sobre la materia

2. **Ajustar preguntas:**
   - Usar términos específicos del syllabus
   - Preguntar sobre temas exactos del documento
   - Incluir "aplicaciones basadas en el conocimiento" en la pregunta

3. **Verificar vector store:**
   ```bash
   # Reinicializar el vector store
   # (esto se hace automáticamente al reiniciar el servidor)
   ```

## 📊 Métricas de Éxito

### **Mínimo esperado:**
- **Chunks**: ≥ 5 (para un syllabus típico)
- **Respuestas relevantes**: ≥ 70% de preguntas específicas
- **Tiempo de respuesta**: < 5 segundos

### **Óptimo:**
- **Chunks**: 10-20 (syllabus completo)
- **Respuestas relevantes**: ≥ 90% de preguntas específicas
- **Información específica**: Objetivos, contenido, evaluación, bibliografía

## 🧪 Scripts de Prueba

### **Ejecutar todos los tests:**
```bash
# Verificación completa
python verificar_pdf.py

# Prueba simple
python test_pdf_simple.py

# Verificar endpoint
curl -X GET http://localhost:8000/chatbot/docs/check/
```

### **Prueba individual:**
```bash
# Probar una pregunta específica
curl -X POST http://localhost:8000/chatbot/chatbot/ \
  -H "Content-Type: application/json" \
  -d '{"pregunta": "¿Qué es aplicaciones basadas en el conocimiento?"}'
```

## 📝 Registro de Verificación

### **Fecha**: ___________
### **Verificado por**: ___________

- [ ] Archivo PDF existe en media/docs/
- [ ] Endpoint /docs/check/ detecta el PDF
- [ ] PDF tiene chunks > 0
- [ ] Respuestas contienen información del syllabus
- [ ] Fuente de respuestas es "pdf" o "Contenido"
- [ ] Tiempo de respuesta < 5 segundos
- [ ] Preguntas específicas funcionan correctamente

### **Notas adicionales:**
_____________________________________________
_____________________________________________
_____________________________________________

## 🚀 Siguiente Paso

Una vez verificado que el PDF funciona correctamente, puedes:
1. Agregar más PDFs de otros syllabus
2. Mejorar las preguntas del FAQ relacionadas
3. Ajustar los umbrales de relevancia si es necesario
4. Implementar categorización por materias
