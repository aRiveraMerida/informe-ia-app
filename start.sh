#!/bin/bash

# Script de inicio rápido para la aplicación de informes con IA

echo "🚀 Iniciando Generador de Informes Ejecutivos con IA..."
echo ""

# Verificar si el entorno virtual existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
    echo "✅ Entorno virtual creado"
fi

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias si es necesario
if [ ! -f "venv/.installed" ]; then
    echo "📚 Instalando dependencias..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch venv/.installed
    echo "✅ Dependencias instaladas"
fi

# Verificar API key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo ""
    echo "⚠️  Variable ANTHROPIC_API_KEY no configurada"
    echo "   Puedes configurarla ahora o introducirla en la UI"
    echo ""
    read -p "¿Quieres configurarla ahora? (s/n): " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        read -p "Introduce tu API key: " api_key
        export ANTHROPIC_API_KEY=$api_key
        echo "✅ API key configurada para esta sesión"
    fi
fi

echo ""
echo "🌟 Iniciando aplicación..."
echo "📍 URL: http://localhost:8501"
echo ""

# Iniciar Streamlit
streamlit run app.py
