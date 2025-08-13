# Plan de Pruebas de Software
## Sistema de Chatbot Académico DCCO/ESPE

---

| **Información del Documento** |  |
|---|---|
| **Título** | Plan de Pruebas - Sistema de Chatbot Académico DCCO/ESPE |
| **Versión** | 1.0 |
| **Fecha** | 12 de agosto de 2025 |
| **Autor** | Equipo de Desarrollo DCCO |
| **Revisor** | [Pendiente] |
| **Aprobador** | [Pendiente] |
| **Estado** | Borrador |

---

## Tabla de Contenidos

1. [Identificador del Plan de Pruebas](#1-identificador-del-plan-de-pruebas)
2. [Referencias](#2-referencias)
3. [Introducción](#3-introducción)
4. [Elementos de Prueba](#4-elementos-de-prueba)
5. [Características a Probar](#5-características-a-probar)
6. [Características que No se Probarán](#6-características-que-no-se-probarán)
7. [Aproximación](#7-aproximación)
8. [Criterios de Éxito/Fallo](#8-criterios-de-éxitofallo)
9. [Criterios de Suspensión y Reanudación](#9-criterios-de-suspensión-y-reanudación)
10. [Entregables de Prueba](#10-entregables-de-prueba)
11. [Tareas de Prueba](#11-tareas-de-prueba)
12. [Necesidades del Entorno](#12-necesidades-del-entorno)
13. [Responsabilidades](#13-responsabilidades)
14. [Cronograma](#14-cronograma)
15. [Riesgos y Contingencias](#15-riesgos-y-contingencias)
16. [Aprobaciones](#16-aprobaciones)

---

## 1. Identificador del Plan de Pruebas

**ID del Plan:** TP-CHATBOT-DCCO-001  
**Nombre del Proyecto:** Sistema de Chatbot Académico DCCO/ESPE  
**Versión del Software:** 1.0  
**Entorno Objetivo:** Producción  

### 1.1 Propósito del Documento

Este documento define la estrategia, objetivos, cronograma, estimaciones, recursos y aproximación para las actividades de prueba del Sistema de Chatbot Académico del Departamento de Ciencias de la Computación (DCCO) de la Universidad ESPE.

### 1.2 Audiencia Objetivo

- Equipo de Desarrollo de Software
- Arquitectos de Software
- Especialistas en QA/Testing
- Project Manager
- Stakeholders del DCCO

---

## 2. Referencias

### 2.1 Documentos de Referencia

| **Documento** | **Versión** | **Ubicación** |
|---|---|---|
| Especificación de Requisitos de Software | 1.0 | [SRS-CHATBOT-001] |
| Documento de Arquitectura de Software | 1.0 | [SAD-CHATBOT-001] |
| Manual de Usuario | 1.0 | [UM-CHATBOT-001] |
| Política de Calidad de Software | 2.1 | [QP-ESPE-021] |

### 2.2 Estándares Aplicables

- **IEEE 829-2008:** Standard for Software and System Test Documentation
- **ISO/IEC 25010:** Systems and software Quality Requirements and Evaluation (SQuaRE)
- **ISO/IEC/IEEE 29119:** Software Testing Standard
- **ISTQB Foundation Level:** Testing Best Practices

---

## 3. Introducción

### 3.1 Descripción del Sistema

El Sistema de Chatbot Académico DCCO/ESPE es una aplicación web basada en inteligencia artificial que proporciona asistencia automatizada a estudiantes y personal del Departamento de Ciencias de la Computación. El sistema integra:

- **Backend:** Django REST Framework
- **Base de Datos:** SQLite (desarrollo), PostgreSQL (producción)
- **Inteligencia Artificial:** OpenAI GPT-3.5-turbo
- **Sistema RAG:** Firebase Firestore con embeddings vectoriales
- **Búsqueda:** Vector store con sentence-transformers
- **Autenticación:** Token-based authentication

### 3.2 Objetivos de las Pruebas

#### 3.2.1 Objetivos Primarios
- Verificar que el sistema cumple con los requisitos funcionales especificados
- Validar la integración correcta entre componentes (Django, OpenAI, Firebase)
- Asegurar la calidad de las respuestas del chatbot en contexto académico
- Garantizar la seguridad y privacidad de los datos

#### 3.2.2 Objetivos Secundarios
- Evaluar el rendimiento bajo cargas normales y pico
- Verificar la usabilidad de las interfaces de usuario
- Validar la mantenibilidad del código
- Asegurar la compatibilidad con diferentes navegadores y dispositivos

### 3.3 Alcance de las Pruebas

#### 3.3.1 Dentro del Alcance
- Funcionalidades del API REST
- Procesamiento de lenguaje natural y respuestas del chatbot
- Integración con servicios externos (OpenAI, Firebase)
- Seguridad de la aplicación
- Rendimiento y escalabilidad
- Calidad del código fuente

#### 3.3.2 Fuera del Alcance
- Infraestructura de servidores y red
- Servicios de terceros (OpenAI API, Firebase infrastructure)
- Interfaces de usuario frontend (si las hay)
- Migración de datos históricos

---

## 4. Elementos de Prueba

### 4.1 Componentes del Software

| **Componente** | **Versión** | **Descripción** | **Criticidad** |
|---|---|---|---|
| chatbot.views | 1.0 | API principal del chatbot | Alta |
| firebase_embeddings | 1.0 | Sistema RAG con embeddings | Alta |
| firebase_service | 1.0 | Gestión de datos Firebase | Alta |
| vector_store | 1.0 | Búsqueda vectorial local | Media |
| authentication | 1.0 | Sistema de autenticación | Alta |
| simple_views | 1.0 | Vistas de gestión FAQ | Media |
| document_loader | 1.0 | Carga de documentos PDF | Baja |

### 4.2 Configuraciones de Prueba

| **Configuración** | **Descripción** | **Propósito** |
|---|---|---|
| Desarrollo | Entorno local con SQLite | Pruebas unitarias e integración |
| Staging | Servidor de pruebas con PostgreSQL | Pruebas de sistema y aceptación |
| Producción | Servidor productivo | Pruebas de humo y monitoreo |

---

## 5. Características a Probar

### 5.1 Funcionalidades Principales

#### 5.1.1 Procesamiento de Consultas (Prioridad: Alta)
- **F001:** Recepción y validación de preguntas de usuarios
- **F002:** Detección de contexto académico vs. fuera de contexto
- **F003:** Búsqueda en base de conocimiento Firebase
- **F004:** Reformulación de respuestas con OpenAI
- **F005:** Generación de respuestas para preguntas no documentadas

#### 5.1.2 Gestión de Base de Conocimiento (Prioridad: Media)
- **F006:** Agregar nuevas entradas FAQ
- **F007:** Modificar entradas existentes
- **F008:** Validación de duplicados
- **F009:** Gestión de embeddings automática

#### 5.1.3 Autenticación y Autorización (Prioridad: Alta)
- **F010:** Autenticación por token para gestión
- **F011:** Acceso público para consultas
- **F012:** Validación de permisos

### 5.2 Características No Funcionales

#### 5.2.1 Rendimiento (Prioridad: Alta)
- **NF001:** Tiempo de respuesta < 3 segundos para 95% de consultas
- **NF002:** Capacidad de 100 usuarios concurrentes
- **NF003:** Disponibilidad del sistema > 99%

#### 5.2.2 Seguridad (Prioridad: Alta)
- **NF004:** Protección contra inyección SQL
- **NF005:** Protección contra ataques XSS
- **NF006:** Validación de entrada de datos
- **NF007:** Logging de accesos y errores

#### 5.2.3 Usabilidad (Prioridad: Media)
- **NF008:** Respuestas claras y relevantes
- **NF009:** Manejo adecuado de errores
- **NF010:** Retroalimentación apropiada al usuario

#### 5.2.4 Mantenibilidad (Prioridad: Media)
- **NF011:** Código cumple estándares PEP 8
- **NF012:** Cobertura de pruebas > 80%
- **NF013:** Documentación de código adecuada

---

## 6. Características que No se Probarán

### 6.1 Componentes Excluidos

- **Infraestructura:** Configuración de servidores, red, DNS
- **Servicios Externos:** Funcionamiento interno de OpenAI API y Firebase
- **Navegadores Legacy:** Internet Explorer, versiones obsoletas
- **Dispositivos Específicos:** Hardware especializado o muy antiguo

### 6.2 Justificación de Exclusiones

Las exclusiones se basan en:
- Componentes fuera del control del equipo de desarrollo
- Tecnologías obsoletas o no soportadas
- Limitaciones de tiempo y recursos
- Riesgos aceptables para el negocio

---

## 7. Aproximación

### 7.1 Estrategia General

La estrategia de pruebas sigue un enfoque **basado en riesgos** con implementación de **testing en pirámide**:

```
                ┌─────────────┐
                │     E2E     │  (20%)
                │  Manual/API │
            ┌───┼─────────────┼───┐
            │   │ Integration │   │  (30%)
            │   │  Component  │   │
        ┌───┼───┼─────────────┼───┼───┐
        │   │   │    Unit     │   │   │  (50%)
        │   │   │   Tests     │   │   │
        └───┴───┴─────────────┴───┴───┘
```

### 7.2 Tipos de Prueba

#### 7.2.1 Pruebas Estáticas
- **Revisión de Código:** Análisis manual de código crítico
- **Análisis Estático:** Herramientas automatizadas (pylint, flake8)
- **Revisión de Documentación:** Verificación de completitud y precisión

#### 7.2.2 Pruebas Dinámicas

**Pruebas de Caja Blanca:**
- Pruebas unitarias con pytest
- Análisis de cobertura de código
- Pruebas de flujo de control

**Pruebas de Caja Negra:**
- Pruebas funcionales basadas en requisitos
- Pruebas de partición de equivalencia
- Pruebas de valores límite
- Pruebas de casos de uso

**Pruebas de Caja Gris:**
- Pruebas de integración de componentes
- Pruebas de API con conocimiento interno

### 7.3 Niveles de Prueba

#### 7.3.1 Pruebas Unitarias (50% del esfuerzo)
- **Herramientas:** pytest, unittest, mock
- **Cobertura:** 80% mínimo
- **Automatización:** 100%

#### 7.3.2 Pruebas de Integración (30% del esfuerzo)
- **Herramientas:** pytest-django, requests
- **Enfoque:** Big Bang y Bottom-up
- **Automatización:** 90%

#### 7.3.3 Pruebas de Sistema (15% del esfuerzo)
- **Herramientas:** Postman, curl scripts
- **Enfoque:** End-to-end scenarios
- **Automatización:** 70%

#### 7.3.4 Pruebas de Aceptación (5% del esfuerzo)
- **Herramientas:** Manual testing, user scenarios
- **Enfoque:** Business requirements validation
- **Automatización:** 30%

### 7.4 Herramientas de Prueba

#### 7.4.1 Framework y Librerías
```python
# Core testing framework
pytest==7.4.0
pytest-django==4.5.2
pytest-cov==4.1.0
pytest-mock==3.11.1

# Test data generation
factory-boy==3.3.0
faker==19.3.0

# API testing
requests==2.31.0
responses==0.23.1
```

#### 7.4.2 Análisis de Calidad
```python
# Static analysis
pylint==2.17.4
flake8==6.0.0
mypy==1.5.1
black==23.7.0

# Security analysis
bandit==1.7.5
safety==2.3.5
```

#### 7.4.3 Métricas y Reportes
```python
# Coverage and reporting
coverage==7.2.7
pytest-html==3.2.0
pytest-json-report==1.5.0
```

---

## 8. Criterios de Éxito/Fallo

### 8.1 Criterios de Éxito

#### 8.1.1 Criterios Funcionales
- ✅ **100%** de casos de prueba críticos pasan
- ✅ **95%** de casos de prueba totales pasan
- ✅ **90%** de precisión en respuestas académicas
- ✅ **0** defectos críticos abiertos
- ✅ **≤ 2** defectos altos abiertos

#### 8.1.2 Criterios No Funcionales
- ✅ **≥ 80%** cobertura de código
- ✅ **≥ 8.0/10** score de pylint
- ✅ **< 3 segundos** tiempo de respuesta promedio
- ✅ **0** vulnerabilidades críticas o altas
- ✅ **100%** disponibilidad durante pruebas

#### 8.1.3 Criterios de Calidad
- ✅ **0** violaciones de estándares de codificación críticas
- ✅ **≥ 90%** conformidad con requisitos
- ✅ **100%** de documentación de casos de prueba ejecutados

### 8.2 Criterios de Fallo

#### 8.2.1 Fallo Crítico
- ❌ Sistema no puede procesar consultas básicas
- ❌ Pérdida o corrupción de datos
- ❌ Vulnerabilidades de seguridad críticas
- ❌ Caída del sistema sin posibilidad de recuperación

#### 8.2.2 Fallo Alto
- ❌ > 10% de casos de prueba críticos fallan
- ❌ Tiempo de respuesta > 10 segundos constantemente
- ❌ Imposibilidad de agregar nuevas FAQs
- ❌ Respuestas incorrectas > 20% del tiempo

---

## 9. Criterios de Suspensión y Reanudación

### 9.1 Criterios de Suspensión

Las pruebas se suspenderán si:

1. **Build Inestable:** > 50% de casos de prueba fallan debido a problemas de build
2. **Entorno Inaccesible:** Servicios críticos (Firebase, OpenAI) no disponibles > 4 horas
3. **Datos Corruptos:** Base de datos de pruebas corrupta sin posibilidad de restauración
4. **Recursos Insuficientes:** Falta de personal clave por > 2 días consecutivos
5. **Bloqueos Críticos:** Defectos que impiden continuar con > 70% de casos de prueba

### 9.2 Criterios de Reanudación

Las pruebas se reanudarán cuando:

1. **Build Estable:** < 10% de fallos en casos de prueba básicos
2. **Entorno Disponible:** Todos los servicios externos accesibles y estables
3. **Datos Restaurados:** Base de datos de pruebas restaurada y validada
4. **Recursos Disponibles:** Personal clave disponible para continuar
5. **Bloqueos Resueltos:** Defectos críticos resueltos y verificados

---

## 10. Entregables de Prueba

### 10.1 Documentos de Planificación

| **Documento** | **Responsable** | **Fecha Entrega** |
|---|---|---|
| Plan de Pruebas | QA Lead | Semana 1 |
| Especificación de Casos de Prueba | QA Engineer | Semana 2 |
| Plan de Datos de Prueba | QA Engineer | Semana 2 |
| Configuración de Entorno de Pruebas | DevOps | Semana 1 |

### 10.2 Artefactos de Ejecución

| **Artefacto** | **Formato** | **Frecuencia** |
|---|---|---|
| Reporte de Ejecución Diario | HTML/JSON | Diario |
| Reporte de Cobertura | HTML | Semanal |
| Reporte de Defectos | Tracking System | Continuo |
| Métricas de Calidad | Dashboard | Tiempo Real |

### 10.3 Código de Pruebas

```
tests/
├── unit/
│   ├── test_views.py
│   ├── test_firebase_service.py
│   ├── test_embeddings.py
│   └── test_authentication.py
├── integration/
│   ├── test_api_endpoints.py
│   ├── test_firebase_integration.py
│   └── test_openai_integration.py
├── system/
│   ├── test_end_to_end.py
│   └── test_performance.py
├── security/
│   ├── test_injection.py
│   └── test_xss.py
└── fixtures/
    ├── test_data.json
    └── mock_responses.py
```

---

## 11. Tareas de Prueba

### 11.1 Fase de Preparación (Semana 1)

#### 11.1.1 Configuración del Entorno
- **T001:** Configurar entorno de pruebas local
- **T002:** Configurar entorno de pruebas staging
- **T003:** Instalar herramientas de testing
- **T004:** Configurar CI/CD pipeline

#### 11.1.2 Preparación de Datos
- **T005:** Crear datos de prueba base
- **T006:** Configurar mocks para servicios externos
- **T007:** Preparar datasets de FAQs de prueba
- **T008:** Validar conectividad con servicios

### 11.2 Fase de Pruebas Unitarias (Semana 2-3)

#### 11.2.1 Desarrollo de Casos de Prueba
- **T009:** Escribir tests para views.py
- **T010:** Escribir tests para firebase_service.py
- **T011:** Escribir tests para firebase_embeddings.py
- **T012:** Escribir tests para authentication.py
- **T013:** Escribir tests para vector_store.py

#### 11.2.2 Ejecución y Análisis
- **T014:** Ejecutar suite de pruebas unitarias
- **T015:** Analizar cobertura de código
- **T016:** Refactorizar tests basado en resultados
- **T017:** Documentar casos de prueba

### 11.3 Fase de Pruebas de Integración (Semana 3-4)

#### 11.3.1 Integración de Componentes
- **T018:** Probar integración Django-Firebase
- **T019:** Probar integración Django-OpenAI
- **T020:** Probar flujo completo de consultas
- **T021:** Probar gestión de FAQs end-to-end

#### 11.3.2 Integración de Sistema
- **T022:** Probar APIs REST completos
- **T023:** Probar autenticación y autorización
- **T024:** Probar manejo de errores
- **T025:** Probar logging y monitoreo

### 11.4 Fase de Pruebas No Funcionales (Semana 4-5)

#### 11.4.1 Pruebas de Rendimiento
- **T026:** Ejecutar pruebas de carga
- **T027:** Probar tiempo de respuesta
- **T028:** Analizar uso de memoria
- **T029:** Probar escalabilidad

#### 11.4.2 Pruebas de Seguridad
- **T030:** Ejecutar análisis de vulnerabilidades
- **T031:** Probar inyección SQL/NoSQL
- **T032:** Probar ataques XSS
- **T033:** Validar autenticación y autorización

### 11.5 Fase de Pruebas Especializadas (Semana 5)

#### 11.5.1 Pruebas de IA/ML
- **T034:** Validar precisión de respuestas
- **T035:** Probar detección de contexto
- **T036:** Validar reformulación de respuestas
- **T037:** Probar casos edge de IA

#### 11.5.2 Pruebas de Usabilidad
- **T038:** Validar claridad de respuestas
- **T039:** Probar manejo de errores
- **T040:** Validar experiencia de usuario

---

## 12. Necesidades del Entorno

### 12.1 Entorno de Hardware

#### 12.1.1 Servidor de Desarrollo
- **CPU:** 4 cores, 2.5GHz mínimo
- **RAM:** 8GB mínimo, 16GB recomendado
- **Almacenamiento:** 100GB SSD
- **Red:** Conexión estable 100Mbps

#### 12.1.2 Servidor de Staging
- **CPU:** 8 cores, 3.0GHz
- **RAM:** 16GB mínimo, 32GB recomendado
- **Almacenamiento:** 200GB SSD
- **Red:** Conexión estable 1Gbps

### 12.2 Entorno de Software

#### 12.2.1 Sistema Operativo
- **SO:** Ubuntu 20.04 LTS o superior
- **Python:** 3.11+
- **Base de Datos:** PostgreSQL 14+ (staging), SQLite 3.40+ (desarrollo)

#### 12.2.2 Dependencias Externas
- **OpenAI API:** Acceso con API key válida
- **Firebase:** Proyecto configurado con Firestore
- **Internet:** Acceso estable para servicios cloud

### 12.3 Herramientas de Prueba

```bash
# Testing framework
pip install pytest pytest-django pytest-cov pytest-mock

# Code quality
pip install pylint flake8 mypy black bandit safety

# Test utilities
pip install factory-boy faker responses requests-mock

# Performance testing
pip install locust

# Security testing
pip install bandit safety owasp-zap-python
```

### 12.4 Configuración de Entorno

#### 12.4.1 Variables de Entorno
```bash
# Django configuration
DJANGO_SETTINGS_MODULE=chatbot_api.settings
SECRET_KEY=test-secret-key-for-testing
DEBUG=True

# Database
DATABASE_URL=postgresql://user:pass@localhost/testdb

# External services
OPENAI_API_KEY=sk-test-key
FIREBASE_PROJECT_ID=chatbot-dcco-test
GOOGLE_APPLICATION_CREDENTIALS=path/to/test-credentials.json

# Testing specific
TESTING=True
PYTEST_CURRENT_TEST=1
```

#### 12.4.2 Configuración de CI/CD
```yaml
# .github/workflows/tests.yml
name: Test Suite
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.11, 3.12]
    
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-testing.txt
    
    - name: Run tests
      run: |
        pytest --cov=chatbot --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

---

## 13. Responsabilidades

### 13.1 Roles y Responsabilidades

#### 13.1.1 QA Lead
**Responsable:** [Nombre del QA Lead]
- Planificación y coordinación de actividades de prueba
- Revisión y aprobación de casos de prueba
- Gestión de defectos y métricas de calidad
- Comunicación con stakeholders

**Entregables:**
- Plan de pruebas
- Reportes de estado
- Métricas de calidad
- Recomendaciones de mejora

#### 13.1.2 QA Engineer
**Responsable:** [Nombre del QA Engineer]
- Diseño y desarrollo de casos de prueba
- Ejecución de pruebas manuales y automatizadas
- Reporte y seguimiento de defectos
- Mantenimiento de scripts de prueba

**Entregables:**
- Casos de prueba detallados
- Scripts de automatización
- Reportes de defectos
- Resultados de ejecución

#### 13.1.3 Desarrollador Senior
**Responsable:** [Nombre del Developer]
- Soporte técnico para entorno de pruebas
- Revisión de casos de prueba críticos
- Resolución de defectos
- Implementación de mejoras de testabilidad

**Entregables:**
- Código con unit tests
- Documentación técnica
- Fixes de defectos
- Mejoras de arquitectura

#### 13.1.4 DevOps Engineer
**Responsable:** [Nombre del DevOps]
- Configuración de entornos de prueba
- Implementación de CI/CD pipeline
- Monitoreo de entornos
- Backup y restauración de datos

**Entregables:**
- Entornos configurados
- Pipeline de CI/CD
- Scripts de deployment
- Procedimientos de backup

### 13.2 Matriz RACI

| **Actividad** | **QA Lead** | **QA Eng** | **Dev** | **DevOps** | **PM** |
|---|---|---|---|---|---|
| Plan de Pruebas | R,A | C | C | C | I |
| Casos de Prueba | A | R | C | I | I |
| Entorno de Pruebas | C | C | C | R,A | I |
| Ejecución de Pruebas | A | R | C | I | I |
| Reporte de Defectos | A | R | C | I | I |
| Resolución de Defectos | C | C | R,A | C | I |
| Reportes de Estado | R,A | C | I | I | C |

**Leyenda:** R=Responsable, A=Aprobador, C=Consultado, I=Informado

---

## 14. Cronograma

### 14.1 Cronograma Maestro

| **Fase** | **Duración** | **Fecha Inicio** | **Fecha Fin** | **Hitos** |
|---|---|---|---|---|
| Planificación | 1 semana | 13/08/2025 | 20/08/2025 | Plan aprobado |
| Preparación | 1 semana | 20/08/2025 | 27/08/2025 | Entorno listo |
| Pruebas Unitarias | 2 semanas | 27/08/2025 | 10/09/2025 | 80% cobertura |
| Pruebas Integración | 1.5 semanas | 10/09/2025 | 20/09/2025 | APIs validadas |
| Pruebas Sistema | 1 semana | 20/09/2025 | 27/09/2025 | E2E completos |
| Pruebas No Funcionales | 1 semana | 27/09/2025 | 04/10/2025 | SLAs validados |
| Cierre | 0.5 semanas | 04/10/2025 | 08/10/2025 | Reporte final |

### 14.2 Cronograma Detallado

#### 14.2.1 Semana 1: Planificación (13-20 Agosto)
| **Día** | **Actividades** | **Entregables** | **Responsable** |
|---|---|---|---|
| Lunes | Kickoff, revisión de requisitos | Acta de reunión | QA Lead |
| Martes | Análisis de riesgos, estimaciones | Matriz de riesgos | QA Lead |
| Miércoles | Diseño de estrategia de pruebas | Plan preliminar | QA Lead |
| Jueves | Revisión con stakeholders | Plan revisado | QA Lead |
| Viernes | Aprobación y comunicación | Plan aprobado | QA Lead |

#### 14.2.2 Semana 2: Preparación (20-27 Agosto)
| **Día** | **Actividades** | **Entregables** | **Responsable** |
|---|---|---|---|
| Lunes | Setup entorno desarrollo | Entorno dev listo | DevOps |
| Martes | Setup entorno staging | Entorno staging listo | DevOps |
| Miércoles | Instalación herramientas | Herramientas configuradas | QA Eng |
| Jueves | Preparación datos de prueba | Datasets listos | QA Eng |
| Viernes | Validación y smoke tests | Entorno validado | QA Eng |

#### 14.2.3 Semanas 3-4: Pruebas Unitarias (27 Ago - 10 Sep)
| **Semana** | **Foco** | **Meta** | **Criterio Éxito** |
|---|---|---|---|
| Semana 3 | Core functionality | 40% cobertura | Tests views, firebase |
| Semana 4 | Edge cases, refactoring | 80% cobertura | Suite completa |

#### 14.2.4 Semana 5-6: Integración y Sistema (10-27 Sep)
| **Semana** | **Foco** | **Meta** | **Criterio Éxito** |
|---|---|---|---|
| Semana 5 | Component integration | APIs funcionando | End-to-end básico |
| Semana 6 | System testing | Flujos completos | Scenarios críticos |

#### 14.2.5 Semana 7: No Funcionales (27 Sep - 4 Oct)
| **Tipo** | **Duración** | **Meta** | **Criterio Éxito** |
|---|---|---|---|
| Performance | 2 días | < 3s response | SLA cumplido |
| Security | 2 días | 0 critical vulns | Scan limpio |
| Usability | 1 día | Responses claras | Feedback positivo |

### 14.3 Dependencias Críticas

| **Dependencia** | **Impacto** | **Contingencia** |
|---|---|---|
| Acceso OpenAI API | Alto | Usar mocks temporalmente |
| Firebase disponibilidad | Alto | Base datos local backup |
| Servidor staging | Medio | Usar entorno local |
| Personal QA | Alto | Training cross-functional |

---

## 15. Riesgos y Contingencias

### 15.1 Identificación de Riesgos

#### 15.1.1 Riesgos Técnicos

| **ID** | **Riesgo** | **Probabilidad** | **Impacto** | **Nivel** |
|---|---|---|---|---|
| RT001 | API OpenAI inaccesible durante pruebas | Media | Alto | Alto |
| RT002 | Firebase limits excedidos | Baja | Alto | Medio |
| RT003 | Cambios arquitectura tardíos | Media | Alto | Alto |
| RT004 | Performance del modelo IA variable | Alta | Medio | Alto |
| RT005 | Datos de prueba insuficientes | Baja | Medio | Bajo |

#### 15.1.2 Riesgos de Proyecto

| **ID** | **Riesgo** | **Probabilidad** | **Impacto** | **Nivel** |
|---|---|---|---|---|
| RP001 | Retrasos en desarrollo | Media | Alto | Alto |
| RP002 | Recursos QA insuficientes | Baja | Alto | Medio |
| RP003 | Cambios de requisitos | Media | Medio | Medio |
| RP004 | Entorno staging inestable | Media | Medio | Medio |
| RP005 | Falta documentación técnica | Alta | Bajo | Medio |

#### 15.1.3 Riesgos de Calidad

| **ID** | **Riesgo** | **Probabilidad** | **Impacto** | **Nivel** |
|---|---|---|---|---|
| RQ001 | Casos de prueba incompletos | Media | Alto | Alto |
| RQ002 | Automatización insuficiente | Media | Medio | Medio |
| RQ003 | Cobertura de código baja | Alta | Medio | Alto |
| RQ004 | Defectos no detectados | Baja | Alto | Medio |
| RQ005 | False positives en tests | Media | Bajo | Bajo |

### 15.2 Estrategias de Mitigación

#### 15.2.1 Mitigación de Riesgos Técnicos

**RT001 - API OpenAI inaccesible:**
- **Prevención:** Monitoreo proactivo de status
- **Mitigación:** Mocks comprehensivos para todas las funciones
- **Contingencia:** Tests offline con respuestas pre-grabadas
- **Responsable:** DevOps Engineer

**RT003 - Cambios arquitectura tardíos:**
- **Prevención:** Freeze arquitectural después de Semana 1
- **Mitigación:** Tests modulares adaptables
- **Contingencia:** Re-planning con tiempo adicional
- **Responsable:** QA Lead + Arquitecto

**RT004 - Performance IA variable:**
- **Prevención:** Baseline de performance establecido
- **Mitigación:** Tests estadísticos (percentiles)
- **Contingencia:** Criterios flexibles documentados
- **Responsable:** QA Engineer

#### 15.2.2 Mitigación de Riesgos de Proyecto

**RP001 - Retrasos en desarrollo:**
- **Prevención:** Checkpoints semanales
- **Mitigación:** Priorización de tests críticos
- **Contingencia:** Scope reduction documentado
- **Responsable:** QA Lead + PM

**RP002 - Recursos QA insuficientes:**
- **Prevención:** Cross-training desarrolladores
- **Mitigación:** Automatización máxima
- **Contingencia:** Outsourcing temporal
- **Responsable:** QA Lead

#### 15.2.3 Mitigación de Riesgos de Calidad

**RQ001 - Casos de prueba incompletos:**
- **Prevención:** Peer review obligatorio
- **Mitigación:** Template estandarizado
- **Contingencia:** Audit externo
- **Responsable:** QA Engineer

**RQ003 - Cobertura código baja:**
- **Prevención:** Gates automáticos en CI/CD
- **Mitigación:** Identificación gaps diaria
- **Contingencia:** Sprint adicional de testing
- **Responsable:** QA Engineer + Developer

### 15.3 Plan de Contingencia

#### 15.3.1 Escenario: Retraso Crítico (>1 semana)

**Trigger:** Desarrollo atrasado >5 días
**Acción Inmediata:**
1. Reunión emergencia stakeholders
2. Re-evaluar scope crítico vs. nice-to-have
3. Priorizar tests para funcionalidad core
4. Comunicar impacto a usuario final

**Responsable:** QA Lead + PM

#### 15.3.2 Escenario: Falla Servicios Externos

**Trigger:** OpenAI/Firebase down >4 horas
**Acción Inmediata:**
1. Activar modo "tests offline"
2. Usar mocks y data sintética
3. Continuar con tests unitarios
4. Re-schedule tests integración

**Responsable:** DevOps + QA Engineer

#### 15.3.3 Escenario: Defectos Críticos Masivos

**Trigger:** >50% tests fallando
**Acción Inmediata:**
1. Stop testing, evaluar build
2. Triage de defectos por severidad
3. Focus en show-stoppers únicamente
4. Daily stand-ups hasta resolución

**Responsable:** QA Lead + Development Lead

---

## 16. Aprobaciones

### 16.1 Revisión del Documento

| **Rol** | **Nombre** | **Fecha Revisión** | **Estado** | **Comentarios** |
|---|---|---|---|---|
| QA Lead | [Nombre] | [DD/MM/YYYY] | ⏳ Pendiente | |
| Tech Lead | [Nombre] | [DD/MM/YYYY] | ⏳ Pendiente | |
| Project Manager | [Nombre] | [DD/MM/YYYY] | ⏳ Pendiente | |
| Product Owner | [Nombre] | [DD/MM/YYYY] | ⏳ Pendiente | |

### 16.2 Aprobación Formal

#### 16.2.1 Criterios de Aprobación
- ✅ Revisión técnica completada sin observaciones críticas
- ✅ Alineación con objetivos de negocio confirmada
- ✅ Recursos y cronograma validados como factibles
- ✅ Riesgos identificados y mitigaciones aceptables
- ✅ Stakeholders informados y comprometidos

#### 16.2.2 Firmas de Aprobación

| **Rol** | **Nombre** | **Firma** | **Fecha** |
|---|---|---|---|
| **QA Manager** | [Nombre] | ________________ | [DD/MM/YYYY] |
| **Development Manager** | [Nombre] | ________________ | [DD/MM/YYYY] |
| **Project Manager** | [Nombre] | ________________ | [DD/MM/YYYY] |
| **Product Owner** | [Nombre] | ________________ | [DD/MM/YYYY] |

### 16.3 Control de Versiones

| **Versión** | **Fecha** | **Autor** | **Descripción de Cambios** |
|---|---|---|---|
| 0.1 | 12/08/2025 | QA Team | Borrador inicial |
| 1.0 | [DD/MM/YYYY] | [Autor] | Primera versión aprobada |

### 16.4 Distribución

Este documento será distribuido a:
- ✅ Equipo de Desarrollo
- ✅ Equipo de QA
- ✅ Project Management Office
- ✅ Product Owner / Stakeholders
- ✅ DevOps Team
- ✅ Archivo del proyecto

---

## Anexos

### Anexo A: Plantillas de Casos de Prueba

#### A.1 Template de Caso de Prueba Funcional
```
ID: TC-[COMPONENT]-[NUMBER]
Título: [Descripción breve del caso]
Precondiciones: [Estado inicial requerido]
Pasos:
1. [Acción específica]
2. [Acción específica]
3. [Acción específica]
Resultado Esperado: [Resultado específico y verificable]
Datos de Prueba: [Datos específicos necesarios]
Prioridad: [Alta/Media/Baja]
Automatizable: [Sí/No]
```

#### A.2 Template de Caso de Prueba de API
```
ID: TC-API-[ENDPOINT]-[NUMBER]
Endpoint: [URL del endpoint]
Método: [GET/POST/PUT/DELETE]
Headers: [Headers requeridos]
Body: [JSON de request]
Status Code Esperado: [200/400/401/etc]
Response Body Esperado: [Estructura JSON]
Validaciones: [Campos a validar]
```

### Anexo B: Configuración de Herramientas

#### B.1 Configuración pytest.ini
```ini
[tool:pytest]
DJANGO_SETTINGS_MODULE = chatbot_api.settings.test
python_files = tests.py test_*.py *_tests.py
python_classes = Test*
python_functions = test_*
addopts = 
    --verbose
    --tb=short
    --cov=chatbot
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
    --strict-markers
markers =
    unit: Unit tests
    integration: Integration tests
    api: API tests
    security: Security tests
    performance: Performance tests
```

#### B.2 Configuración pylint
```ini
[MASTER]
load-plugins=pylint_django
django-settings-module=chatbot_api.settings

[MESSAGES CONTROL]
disable=missing-docstring,
        line-too-long,
        too-few-public-methods

[FORMAT]
max-line-length=120

[DESIGN]
max-args=10
max-attributes=15
```

### Anexo C: Scripts de Automatización

#### C.1 Script de Ejecución Completa
```bash
#!/bin/bash
# run_test_suite.sh

echo "🚀 Iniciando Suite Completa de Pruebas"

# 1. Análisis estático
echo "📊 Ejecutando análisis estático..."
pylint chatbot/ --score=yes
flake8 chatbot/
bandit -r chatbot/

# 2. Pruebas unitarias
echo "🧪 Ejecutando pruebas unitarias..."
pytest tests/unit/ --cov=chatbot --cov-report=html

# 3. Pruebas de integración
echo "🔗 Ejecutando pruebas de integración..."
pytest tests/integration/ -v

# 4. Pruebas de API
echo "🌐 Ejecutando pruebas de API..."
pytest tests/api/ -v

# 5. Reporte final
echo "📋 Generando reporte final..."
coverage report
coverage html

echo "✅ Suite completa ejecutada"
```

---

**Fin del Documento**

---

*Este plan de pruebas ha sido desarrollado siguiendo estándares IEEE 829-2008 y ISO/IEC/IEEE 29119 para asegurar la calidad y completitud de las actividades de testing del Sistema de Chatbot Académico DCCO/ESPE.*
