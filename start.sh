#!/bin/bash

# Script de inicio para Render
echo "🚀 Iniciando aplicación Parqués Distribuido IA..."

# Verificar variables de entorno críticas
if [ -z "$DATABASE_URL" ]; then
    echo "❌ ERROR: DATABASE_URL no está configurada"
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    echo "❌ ERROR: SECRET_KEY no está configurada"
    exit 1
fi

# Configurar variables por defecto si no existen
export ENVIRONMENT=${ENVIRONMENT:-production}
export DEBUG=${DEBUG:-false}
export BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS:-"*"}

echo "✅ Variables de entorno configuradas:"
echo "   - ENVIRONMENT: $ENVIRONMENT"
echo "   - DEBUG: $DEBUG"
echo "   - BACKEND_CORS_ORIGINS: $BACKEND_CORS_ORIGINS"
echo "   - DATABASE_URL: [CONFIGURADA]"
echo "   - SECRET_KEY: [CONFIGURADA]"

# Cambiar al directorio Backend
cd Backend

echo "📦 Verificando dependencias..."
python -c "import fastapi, uvicorn, pydantic, socketio; print('✅ Dependencias principales OK')" || {
    echo "❌ ERROR: Faltan dependencias críticas"
    exit 1
}

echo "🔄 Ejecutando migraciones de base de datos..."
alembic upgrade head || {
    echo "⚠️  ADVERTENCIA: No se pudieron ejecutar las migraciones"
    echo "   Continuando sin migraciones..."
}

echo "🌐 Iniciando servidor en puerto $PORT..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 1