#!/usr/bin/env python3
"""
Test de configuración para verificar que todo funciona correctamente
"""
import os
import sys

def test_cors_config():
    """Test de configuración CORS"""
    print("🧪 Probando configuración CORS...")
    
    # Simular diferentes valores de BACKEND_CORS_ORIGINS
    test_cases = [
        ("*", ["*"]),
        ("http://localhost:3000", ["http://localhost:3000"]),
        ("http://localhost:3000,https://miapp.com", ["http://localhost:3000", "https://miapp.com"]),
        ('["http://localhost:3000","https://miapp.com"]', ["http://localhost:3000", "https://miapp.com"]),
        ("", ["*"]),  # Caso vacío
        (None, ["http://localhost:3000", "http://localhost:8000", "https://localhost:3000", "https://localhost:8000"]),
    ]
    
    for test_value, expected in test_cases:
        # Configurar variable de entorno
        if test_value is None:
            if "BACKEND_CORS_ORIGINS" in os.environ:
                del os.environ["BACKEND_CORS_ORIGINS"]
        else:
            os.environ["BACKEND_CORS_ORIGINS"] = test_value
        
        try:
            # Importar configuración
            from app.core.config import Settings
            settings = Settings()
            result = settings.BACKEND_CORS_ORIGINS
            
            print(f"   Input: {test_value} -> Output: {result}")
            
            if result == expected:
                print(f"   ✅ PASS")
            else:
                print(f"   ❌ FAIL - Expected: {expected}")
                return False
                
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            return False
    
    print("✅ Todos los tests de CORS pasaron")
    return True

def test_environment_variables():
    """Test de variables de entorno críticas"""
    print("\n🧪 Probando variables de entorno...")
    
    # Variables críticas para producción
    critical_vars = ["DATABASE_URL", "SECRET_KEY"]
    
    for var in critical_vars:
        if var not in os.environ:
            print(f"   ⚠️  {var} no está configurada (OK para desarrollo)")
        else:
            print(f"   ✅ {var} está configurada")
    
    return True

def test_imports():
    """Test de importaciones críticas"""
    print("\n🧪 Probando importaciones críticas...")
    
    try:
        import fastapi
        print(f"   ✅ FastAPI {fastapi.__version__}")
    except ImportError as e:
        print(f"   ❌ FastAPI: {e}")
        return False
    
    try:
        import uvicorn
        print(f"   ✅ Uvicorn {uvicorn.__version__}")
    except ImportError as e:
        print(f"   ❌ Uvicorn: {e}")
        return False
    
    try:
        import pydantic
        print(f"   ✅ Pydantic {pydantic.__version__}")
    except ImportError as e:
        print(f"   ❌ Pydantic: {e}")
        return False
    
    try:
        import socketio
        print(f"   ✅ Socket.IO {socketio.__version__}")
    except ImportError as e:
        print(f"   ❌ Socket.IO: {e}")
        return False
    
    return True

def main():
    """Función principal"""
    print("🚀 Test de configuración para Parqués Distribuido IA")
    print("=" * 50)
    
    # Configurar path para importaciones
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    all_passed = True
    
    # Ejecutar tests
    all_passed &= test_imports()
    all_passed &= test_environment_variables()
    all_passed &= test_cors_config()
    
    print("\n" + "=" * 50)
    if all_passed:
        print("🎉 Todos los tests pasaron - Configuración OK")
        return 0
    else:
        print("❌ Algunos tests fallaron - Revisar configuración")
        return 1

if __name__ == "__main__":
    exit(main())