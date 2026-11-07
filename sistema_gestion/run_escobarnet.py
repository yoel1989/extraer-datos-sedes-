#!/usr/bin/env python3
"""
Script de inicio del Sistema ESCOBARNET
Inicia la aplicación en el puerto 5002
"""

import os
import sys

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Iniciar la aplicación ESCOBARNET"""
    
    print("=" * 60)
    print("🚀 SISTEMA DE GESTIÓN INTEGRAL ESCOBARNET")
    print("=" * 60)
    
    # Mostrar configuración
    print(f"📁 Directorio: {os.getcwd()}")
    print(f"🌐 Puerto: 5002")
    print(f"🔗 URL: http://localhost:5002")
    print(f"💾 Base de datos: {'Supabase' if os.getenv('USE_SUPABASE') == 'true' else 'SQLite'}")
    
    # Verificar variables de entorno
    supabase_url = os.getenv('SUPABASE_URL')
    if os.getenv('USE_SUPABASE') == 'true' and supabase_url:
        print(f"🌐 Supabase: {supabase_url[:30]}...")
    else:
        print("💾 Usando SQLite local")
    
    print("\n🔐 Credenciales de acceso:")
    print("   Usuario: admin")
    print("   Contraseña: admin123")
    
    print("\n📋 Módulos disponibles:")
    print("   ✅ Dashboard - Panel principal")
    print("   ✅ Extracción de Datos - Automatización Telegram")
    print("   ✅ Contabilidad - Gestión financiera")
    print("   ✅ Televisión - Servicios TV")
    print("   ✅ Sedes - Gestión de sedes")
    print("   ✅ Portales Cautivos - WiFi management")
    
    print("\n" + "=" * 60)
    print("🚀 Iniciando aplicación en puerto 5002...")
    print("   Presiona Ctrl+C para detener")
    print("=" * 60)
    
    try:
        from app import create_app
        
        # Configurar puerto
        os.environ['FLASK_RUN_PORT'] = '5002'
        os.environ['FLASK_RUN_HOST'] = '0.0.0.0'
        
        # Crear y ejecutar aplicación
        app = create_app('development')
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5002
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Aplicación detenida por el usuario")
    except Exception as e:
        print(f"\n❌ Error al iniciar la aplicación: {e}")
        print("\n🔧 Posibles soluciones:")
        print("1. Verifica que las dependencias estén instaladas: pip install -r requirements.txt")
        print("2. Verifica la configuración en el archivo .env")
        print("3. Asegúrate que el puerto 5002 esté disponible")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())