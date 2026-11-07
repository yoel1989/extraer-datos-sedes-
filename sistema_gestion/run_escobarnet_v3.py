#!/usr/bin/env python3
"""
Script de inicio del Sistema ESCOBARNET 100% Supabase
Inicia la aplicación en el puerto 5002
"""

import os
import sys

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    """Iniciar la aplicación ESCOBARNET 100% Supabase"""
    
    print("=" * 60)
    print("     SISTEMA DE GESTION INTEGRAL ESCOBARNET v3.0")
    print("              100% SUPABASE - SIN SQLITE")
    print("=" * 60)
    
    # Mostrar configuración
    print(f"Directorio: {os.getcwd()}")
    print(f"Puerto: 5002")
    print(f"URL: http://localhost:5002")
    
    # Verificar variables de entorno
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if supabase_url and supabase_key:
        print(f"Supabase: {supabase_url[:30]}...")
        print("Base de datos: Supabase Cloud ACTIVA")
    else:
        print("ERROR: Faltan variables de Supabase")
        return 1
    
    print("\nCredenciales de Acceso:")
    print("   Usuario: admin")
    print("   Contrasena: admin123")
    
    print("\nModulos disponibles:")
    print("   [OK] Dashboard - Panel principal")
    print("   [OK] Extraccion de Datos - Automatizacion Telegram")
    print("   [OK] Contabilidad - Gestion financiera")
    print("   [OK] Television - Servicios TV")
    print("   [OK] Sedes - Gestion de sedes")
    print("   [OK] Portales Cautivos - WiFi management")
    
    print("\n" + "=" * 60)
    print("Iniciando aplicacion en puerto 5002...")
    print("   Presiona Ctrl+C para detener")
    print("=" * 60)
    
    try:
        # Probar importar dependencias
        print("\nVerificando dependencias...")
        
        # Verificar Supabase
        try:
            from supabase import create_client
            print("[OK] Cliente Supabase disponible")
        except ImportError:
            print("[ERROR] Instala: pip install supabase")
            return 1
        
        # Verificar Flask
        try:
            from flask import Flask
            print("[OK] Flask disponible")
        except ImportError:
            print("[ERROR] Instala: pip install flask")
            return 1
        
        # Verificar nuestro gestor
        try:
            from utils.supabase_db import db_manager
            print("[OK] Gestor Supabase disponible")
        except ImportError as e:
            print(f"[ERROR] Error importando gestor: {e}")
            return 1
        
        print("\nProbando conexion a Supabase...")
        if db_manager.test_connection():
            print("[OK] Conexion a Supabase exitosa!")
        else:
            print("[ERROR] No se puede conectar a Supabase")
            return 1
        
        print("\nIniciando aplicacion Flask...")
        from app import create_app
        
        # Configurar puerto
        os.environ['FLASK_RUN_PORT'] = '5002'
        os.environ['FLASK_RUN_HOST'] = '0.0.0.0'
        
        # Crear y ejecutar aplicación
        app = create_app('development')
        
        print("\n" + "=" * 60)
        print("     SISTEMA ESCOBARNET ACTIVO")
        print(f"     URL: http://localhost:5002")
        print("     100% Supabase - 100% Cloud")
        print("=" * 60)
        
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5002
        )
        
    except KeyboardInterrupt:
        print("\n\nAplicacion detenida por el usuario")
    except Exception as e:
        print(f"\nError al iniciar la aplicacion: {e}")
        print("\nPosibles soluciones:")
        print("1. Verifica que las dependencias esten instaladas:")
        print("   pip install -r requirements.txt")
        print("2. Verifica la configuracion en el archivo .env")
        print("3. Asegurate que el puerto 5002 este disponible")
        print("4. Revisa la conexion a Supabase")
        return 1
    
    return 0

if __name__ == '__main__':
    sys.exit(main())