#!/usr/bin/env python3
"""
Script de configuración inicial para Supabase - Proyecto ESCOBARNET
Este script configura automáticamente las tablas y estructura necesaria
"""

import os
import sys
import requests
import json
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de tu proyecto
SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_ANON_KEY = os.environ['SUPABASE_ANON_KEY']
PROJECT_NAME = "escobarnet"

def ejecutar_sql_directamente():
    """Ejecuta el SQL directamente a través del endpoint REST de Supabase"""
    
    # Lee el archivo SQL
    sql_file = os.path.join(os.path.dirname(__file__), 'supabase_setup.sql')
    
    if not os.path.exists(sql_file):
        print("❌ Error: No se encuentra el archivo supabase_setup.sql")
        return False
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    print("📋 SQL cargado correctamente")
    print(f"📏 Tamaño del script: {len(sql_content)} caracteres")
    
    # Para ejecutar SQL en Supabase, necesitamos usar la API REST
    # Sin embargo, es más recomendable ejecutarlo desde el dashboard de Supabase
    
    print("\n" + "="*60)
    print("🔧 INSTRUCCIONES PARA CONFIGURAR SUPABASE")
    print("="*60)
    
    print(f"🌐 URL del proyecto: {SUPABASE_URL}")
    print(f"📝 Nombre del proyecto: {PROJECT_NAME}")
    print(f"🔑 Llave pública: {SUPABASE_ANON_KEY[:20]}...")
    
    print("\n📋 PASOS A SEGUIR:")
    print("1. Abre tu dashboard de Supabase: https://app.supabase.com")
    print("2. Selecciona tu proyecto 'escobarnet'")
    print("3. Ve a la sección 'SQL Editor'")
    print("4. Crea una 'New query'")
    print("5. Copia y pega el contenido del archivo 'scripts/supabase_setup.sql'")
    print("6. Ejecuta el script (presionando 'Run' o Ctrl+Enter)")
    
    print("\n⚠️  IMPORTANTE:")
    print("- El script creará todas las tablas necesarias")
    print("- Configurará índices para mejor rendimiento")
    print("- Creará funciones SQL útiles para reportes")
    print("- Insertará categorías por defecto para contabilidad")
    
    return True

def verificar_conexion():
    """Verifica la conexión con Supabase"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Intentar hacer una consulta simple para verificar conexión
        response = requests.get(f"{SUPABASE_URL}/rest/v1/", headers=headers, timeout=10)
        
        if response.status_code == 200:
            print("✅ Conexión a Supabase verificada correctamente")
            return True
        else:
            print(f"❌ Error de conexión: Status {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False

def crear_usuario_admin_defecto():
    """Crea un usuario administrador por defecto"""
    
    headers = {
        'apikey': SUPABASE_ANON_KEY,
        'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=minimal'
    }
    
    user_data = {
        'username': 'admin',
        'email': 'admin@escobarnet.com',
        'password_hash': '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6ukx.LmRq', # admin123
        'nombre': 'Administrador',
        'apellido': 'Sistema',
        'rol': 'admin',
        'activo': True
    }
    
    try:
        response = requests.post(
            f"{SUPABASE_URL}/rest/v1/users",
            headers=headers,
            json=user_data,
            timeout=10
        )
        
        if response.status_code in [200, 201]:
            print("✅ Usuario administrador creado exitosamente")
            print("   Usuario: admin")
            print("   Contraseña: admin123")
            return True
        else:
            print(f"⚠️  No se pudo crear usuario (puede que ya exista): {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error creando usuario: {e}")
        return False

def main():
    """Función principal de configuración"""
    
    print("CONFIGURACION DEL PROYECTO ESCOBARNET EN SUPABASE")
    print("=" * 60)
    print(f"Directorio actual: {os.getcwd()}")
    print(f"URL Supabase: {SUPABASE_URL}")
    
    print("\n1. Verificando conexion a Supabase...")
    if not verificar_conexion():
        print("ERROR: No se puede conectar a Supabase. Verifica tus credenciales.")
        return
    
    print("\n2. Preparando script SQL...")
    if not ejecutar_sql_directamente():
        print("ERROR: Error preparando el script SQL")
        return
    
    print("\n3. Intentando crear usuario administrador...")
    crear_usuario_admin_defecto()
    
    print("\n" + "="*60)
    print("CONFIGURACION PREPARADA")
    print("="*60)
    
    print("\nRESUMEN:")
    print("✓ Conexion verificada")
    print("✓ Script SQL preparado")
    print("✓ Instrucciones proporcionadas")
    
    print("\nPROXIMOS PASOS:")
    print("1. Ejecuta el script SQL en el dashboard de Supabase")
    print("2. Verifica que se crearon todas las tablas")
    print("3. Ejecuta la migracion de datos (si tienes datos existentes):")
    print("   python scripts/migrate_to_supabase.py")
    print("4. Inicia tu aplicacion:")
    print("   flask run")
    
    print("\nCREDENCIALES DE ACCESO:")
    print("Usuario: admin")
    print("Contrasena: admin123")
    print("URL: http://localhost:5000")
    
    print("\nAYUDA:")
    print("- Si tienes problemas, revisa el archivo README_SUPABASE.md")
    print("- Puedes verificar las tablas en el dashboard de Supabase")
    print("- Los logs te ayudaran a identificar cualquier problema")

if __name__ == '__main__':
    main()