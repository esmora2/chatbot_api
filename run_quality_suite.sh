#!/bin/bash
# Script de Instalación y Ejecución de Suite de Calidad
# Para exposición de Aseguramiento de Calidad de Software

echo "🚀 SETUP DE HERRAMIENTAS DE ASEGURAMIENTO DE CALIDAD"
echo "=================================================="
echo "Universidad ESPE - Departamento de Ciencias de la Computación"
echo "=================================================="

# Verificar que estamos en el directorio correcto
if [ ! -f "manage.py" ]; then
    echo "❌ Error: Ejecuta este script desde el directorio del proyecto Django"
    exit 1
fi

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    echo "🔧 Activando entorno virtual..."
    source venv/bin/activate
else
    echo "⚠️ No se encontró entorno virtual en ./venv"
    echo "   Creando entorno virtual..."
    python3 -m venv venv
    source venv/bin/activate
fi

echo "📦 Instalando herramientas de testing y calidad..."

# Instalar herramientas de testing
pip install -r requirements-testing.txt --quiet

echo "✅ Herramientas instaladas exitosamente"
echo ""

# Verificar instalación
echo "🔍 Verificando instalación de herramientas..."
echo "  - pytest: $(pytest --version 2>/dev/null || echo 'NO INSTALADO')"
echo "  - pylint: $(pylint --version 2>/dev/null | head -1 || echo 'NO INSTALADO')"
echo "  - flake8: $(flake8 --version 2>/dev/null || echo 'NO INSTALADO')"
echo "  - bandit: $(bandit --version 2>/dev/null || echo 'NO INSTALADO')"
echo ""

echo "🎯 EJECUTANDO SUITE COMPLETA DE CALIDAD"
echo "======================================="

# Ejecutar suite de calidad
python quality_assurance_suite.py

echo ""
echo "📋 RESULTADOS DISPONIBLES EN:"
echo "  - REPORTE_CALIDAD.txt (Reporte principal)"
echo "  - htmlcov/index.html (Cobertura de código)"
echo "  - test_results.json (Resultados detallados)"
echo ""

echo "🎉 SUITE DE CALIDAD COMPLETADA"
echo "Puedes usar estos resultados para tu exposición de aseguramiento de calidad"
