# Script para ejecutar el servidor FastAPI en Windows
# Uso: .\run_server.ps1

Write-Host "🚀 Iniciando servidor Parqués Distribuido IA..." -ForegroundColor Green

# Activar entorno virtual
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "✅ Activando entorno virtual..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "❌ ERROR: No se encontró el entorno virtual" -ForegroundColor Red
    Write-Host "   Ejecuta: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Verificar que estamos en el directorio correcto
if (-not (Test-Path ".\app\main.py")) {
    Write-Host "❌ ERROR: No se encontró app\main.py" -ForegroundColor Red
    Write-Host "   Asegúrate de ejecutar este script desde el directorio Backend" -ForegroundColor Yellow
    exit 1
}

# Ejecutar uvicorn
Write-Host "🌐 Iniciando servidor en http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 Documentación disponible en http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload


